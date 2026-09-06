"""Reproducible regional simulation experiment using public 1000 Genomes data."""

import argparse
import hashlib
import json
import platform
from collections import Counter
from pathlib import Path

import numpy as np
import pysam
import scipy

from simulation import (
    calibrate_weights,
    ld_r2,
    mosaic_haplotypes,
    new_haplotype_fraction,
    sample_haplotypes,
)

START, END = 41400000, 41650000  # GRCh37, 1-based, [START, END)
PROTECTED = [(41494958, 41524303)]
FOCUS_POS = 41512841  # rs3745274 G>T, verified against NCBI GRCh37
TARGETS = ["BEB", "CHB", "GBR", "YRI"]
SEEDS = [20260906, 20260907, 20260908]
METHODS = [
    "independent",
    "local_copy",
    "regional_copy",
    "pooled_copy",
    "calibrated_copy",
    "calibrated_mosaic",
]
PRIOR_CHROMOSOMES = 20  # Fixed experimental shrinkage, not an inferred sample size
RIDGE = 0.02


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def extract(vcf_path, index_path, panel_path, cache_path):
    """Keep complete, phased, diploid biallelic SNVs with unique positions."""
    manifest_path = cache_path.with_suffix(".json")
    fingerprint = {
        "vcf_sha256": digest(vcf_path),
        "index_sha256": digest(index_path),
        "panel_sha256": digest(panel_path),
        "region": ["19", START, END],
        "extract_version": 1,
    }
    if cache_path.exists() and manifest_path.exists():
        cached_manifest = json.loads(manifest_path.read_text())
        if cached_manifest["fingerprint"] == fingerprint:
            with np.load(cache_path, allow_pickle=False) as loaded:
                return {k: loaded[k] for k in loaded.files}, cached_manifest

    panel = {}
    for line in panel_path.read_text().splitlines()[1:]:
        sample, pop, superpop, sex = line.split()[:4]
        panel[sample] = (pop, superpop, sex)
    stream = pysam.VariantFile(str(vcf_path), index_filename=str(index_path))
    samples = list(stream.header.samples)
    if not all(s in panel for s in samples):
        raise ValueError("Sample metadata incomplete")
    records, positions, refs, alts = [], [], [], []
    exclusions = Counter()
    observed = Counter()
    for record in stream.fetch("19", START - 1, END - 1):
        if not START <= record.pos < END:
            exclusions["overlapping_record_start_outside_region"] += 1
            continue
        observed[record.pos] += 1
        if len(record.alleles) != 2 or not all(
            len(a) == 1 and a in "ACGT" for a in record.alleles
        ):
            exclusions["non_biallelic_snv"] += 1
            continue
        calls = list(record.samples.values())
        if any(
            len(c["GT"]) != 2
            or None in c["GT"]
            or not c.phased
            or any(a not in (0, 1) for a in c["GT"])
            for c in calls
        ):
            exclusions["missing_unphased_or_non_diploid"] += 1
            continue
        records.append(np.array([c["GT"] for c in calls], dtype=np.uint8))
        positions.append(record.pos)
        refs.append(record.ref)
        alts.append(record.alts[0])
    source_header = str(stream.header)
    stream.close()
    keep = np.array([observed[p] == 1 for p in positions])
    exclusions["duplicate_position_snv"] = int((~keep).sum())
    data = {
        "haplotypes": np.stack(records, axis=-1)[:, :, keep].reshape(
            len(samples) * 2, -1
        ),
        "positions": np.array(positions)[keep],
        "refs": np.array(refs)[keep],
        "alts": np.array(alts)[keep],
        "samples": np.array(samples),
        "populations": np.array([panel[s][0] for s in samples]),
        "superpopulations": np.array([panel[s][1] for s in samples]),
    }
    if not np.all(np.diff(data["positions"]) > 0):
        raise ValueError("Unsorted variant positions")
    manifest = {
        "fingerprint": fingerprint,
        "assembly": "GRCh37/b37",
        "coordinate_convention": "1-based, inclusive start, exclusive end",
        "source_vcf": str(vcf_path.resolve()),
        "source_bytes": vcf_path.stat().st_size,
        "reference_header": [
            line
            for line in source_header.splitlines()
            if line.startswith(("##reference=", "##source=", "##fileDate="))
        ],
        "source_url": "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/ALL.chr19.phase3_shapeit2_mvncall_integrated_v5b.20130502.genotypes.vcf.gz",
        "panel_url": "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel",
        "samples": len(samples),
        "retained_snvs": len(data["positions"]),
        "exclusions": dict(exclusions),
        "protected_intervals": PROTECTED,
        "focus_marker": {
            "id": "rs3745274",
            "position": FOCUS_POS,
            "ref": "G",
            "alt": "T",
        },
        "missing_marker": {
            "id": "rs2279343",
            "position": 41515263,
            "ref": "A",
            "alt": "G",
            "status": "absent from source regional variant records; not assumed reference",
        },
    }
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache_path, **data)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return data, manifest


def hap_rows(sample_ids):
    return (2 * sample_ids[:, None] + np.array([0, 1])).ravel()


def split(data, population, seed, n_local=20):
    rng = np.random.default_rng(seed)
    target = np.flatnonzero(data["populations"] == population)
    shuffled = rng.permutation(target)
    local, heldout = shuffled[:n_local], shuffled[n_local:]
    superpop = data["superpopulations"][target[0]]
    reference = np.flatnonzero(
        (data["superpopulations"] == superpop) & (data["populations"] != population)
    )
    assert not (
        set(local) & set(heldout)
        or set(reference) & set(heldout)
        or set(local) & set(reference)
    )
    return local, reference, heldout


def selected_markers(frequencies, count):
    eligible = np.flatnonzero((frequencies >= 0.05) & (frequencies <= 0.95))
    return eligible[
        np.unique(
            np.linspace(0, len(eligible) - 1, min(count, len(eligible))).astype(int)
        )
    ]


def fit(data, local_ids, reference_ids):
    local = data["haplotypes"][hap_rows(local_ids)]
    reference = data["haplotypes"][hap_rows(reference_ids)]
    donors = np.concatenate([local, reference])
    local_af, reference_af = local.mean(0), reference.mean(0)
    target = (local.sum(0) + PRIOR_CHROMOSOMES * reference_af) / (
        len(local) + PRIOR_CHROMOSOMES
    )
    features = selected_markers(donors.mean(0), 48)
    focus = np.flatnonzero(data["positions"] == FOCUS_POS)
    features = np.unique(np.concatenate([features, focus]))
    weights = calibrate_weights(donors[:, features], target[features], ridge=RIDGE)
    return {
        "local": local,
        "reference": reference,
        "donors": donors,
        "local_af": local_af,
        "weights": weights,
        "features": features,
    }


def generate(fitted, data, method, n_people, seed):
    rng = np.random.default_rng(seed)
    count = 2 * n_people
    if method == "independent":
        return (
            rng.random((count, len(data["positions"]))) < fitted["local_af"]
        ).astype(np.uint8)
    if method == "local_copy":
        return sample_haplotypes(fitted["local"], count, rng)
    if method == "regional_copy":
        return sample_haplotypes(fitted["reference"], count, rng)
    if method == "pooled_copy":
        return sample_haplotypes(fitted["donors"], count, rng)
    if method == "calibrated_copy":
        return sample_haplotypes(fitted["donors"], count, rng, fitted["weights"])
    if method == "calibrated_mosaic":
        return mosaic_haplotypes(
            fitted["donors"],
            data["positions"],
            count,
            rng,
            fitted["weights"],
            PROTECTED,
        )
    raise ValueError(method)


def evaluate(generated, heldout, donors, positions, markers, common):
    # Training-selected marker set; undefined held-out monomorphic r2 is excluded.
    test_af, syn_af = heldout.mean(0), generated.mean(0)
    test_r2 = ld_r2(heldout[:, markers])
    syn_r2 = ld_r2(generated[:, markers])
    polymorphic = (test_af[markers] > 0) & (test_af[markers] < 1)
    pairs = np.triu(np.outer(polymorphic, polymorphic), k=1)
    distance = np.abs(positions[markers, None] - positions[None, markers])
    protected = (positions >= PROTECTED[0][0]) & (positions <= PROTECTED[0][1])
    focus = int(np.flatnonzero(positions == FOCUS_POS)[0])
    test_gt = heldout[:, focus].reshape(-1, 2).sum(1).astype(int)
    syn_gt = generated[:, focus].reshape(-1, 2).sum(1).astype(int)
    test_dist = np.bincount(test_gt, minlength=3) / len(test_gt)
    syn_dist = np.bincount(syn_gt, minlength=3) / len(syn_gt)
    missing = (test_af > 0) & (donors.sum(0) == 0)
    return {
        "common_af_mae": float(np.abs(test_af[common] - syn_af[common]).mean()),
        "ld_r2_mae": float(np.abs(test_r2 - syn_r2)[pairs].mean()),
        "short_ld_r2_mae": float(
            np.abs(test_r2 - syn_r2)[pairs & (distance <= 50000)].mean()
        ),
        "long_ld_r2_mae": float(
            np.abs(test_r2 - syn_r2)[pairs & (distance > 50000)].mean()
        ),
        "focus_af_error": float(abs(test_af[focus] - syn_af[focus])),
        "focus_genotype_total_variation": float(np.abs(test_dist - syn_dist).sum() / 2),
        "focus_real_af": float(test_af[focus]),
        "focus_synthetic_af": float(syn_af[focus]),
        "novel_region_haplotype_fraction": new_haplotype_fraction(generated, donors),
        "novel_protected_haplotype_fraction": new_haplotype_fraction(
            generated[:, protected], donors[:, protected]
        ),
        "heldout_alt_sites_absent_from_pooled_donors": int(missing.sum()),
        "common_sites_evaluated": int(common.sum()),
        "ld_pairs_evaluated": int(pairs.sum()),
    }


def write_vcf(path, generated, data):
    """Write and index phased synthetic regional variants, then verify every GT."""
    n_people = len(generated) // 2
    if len(generated) % 2:
        raise ValueError("Diploid data require an even haplotype count")
    sample_ids = [f"SYNTHETIC_{i:06d}" for i in range(n_people)]
    with pysam.BGZFile(str(path), "w") as stream:
        header = (
            "##fileformat=VCFv4.2\n"
            "##source=AnukritiRegionalSyntheticResearchPrototype\n"
            "##reference=GRCh37\n"
            "##contig=<ID=19,length=59128983>\n"
            "##SYNTHETIC=true\n"
            "##intended_use=research_only_no_clinical_validation\n"
            f"##simulated_region=19:{START}-{END - 1}\n"
            "##missing_known_marker=rs2279343_GRCh37_19_41515263_A_G_not_assumed_reference\n"
            '##FORMAT=<ID=GT,Number=1,Type=String,Description="Phased synthetic genotype">\n'
            "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t"
            + "\t".join(sample_ids)
            + "\n"
        )
        stream.write(header.encode())
        labels = np.array(["0|0", "0|1", "1|0", "1|1"])
        genotypes = generated.reshape(n_people, 2, -1)
        for j, position in enumerate(data["positions"]):
            ids = 2 * genotypes[:, 0, j] + genotypes[:, 1, j]
            marker = "rs3745274" if position == FOCUS_POS else "."
            line = f"19\t{position}\t{marker}\t{data['refs'][j]}\t{data['alts'][j]}\t.\t.\t.\tGT\t"
            stream.write((line + "\t".join(labels[ids]) + "\n").encode())
    pysam.tabix_index(str(path), preset="vcf", force=True)
    variant_count = 0
    with pysam.VariantFile(str(path)) as stream:
        assert list(stream.header.samples) == sample_ids
        for j, record in enumerate(stream.fetch("19", START - 1, END - 1)):
            assert record.pos == data["positions"][j]
            assert record.alleles == (data["refs"][j], data["alts"][j])
            calls = list(record.samples.values())
            assert all(c.phased for c in calls)
            recovered = np.array([c["GT"] for c in calls], dtype=np.uint8).ravel()
            assert np.array_equal(recovered, generated[:, j])
            variant_count += 1
    assert variant_count == len(data["positions"])
    return {
        "path": path.name,
        "sha256": digest(path),
        "samples": n_people,
        "variants": variant_count,
        "all_genotypes_roundtrip_verified": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vcf", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path(__file__).parent / "results")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    data, manifest = extract(args.vcf, args.index, args.panel, args.cache)
    positions = data["positions"]
    focus = np.flatnonzero(positions == FOCUS_POS)
    assert (
        len(focus) == 1
        and data["refs"][focus[0]] == "G"
        and data["alts"][focus[0]] == "T"
    )
    assert 41515263 not in positions
    print(
        f"Extracted {len(positions)} SNVs across {len(data['samples'])} real samples",
        flush=True,
    )
    results, splits = [], []
    for population in TARGETS:
        for seed in SEEDS:
            local_ids, reference_ids, heldout_ids = split(data, population, seed)
            fitted = fit(data, local_ids, reference_ids)
            heldout = data["haplotypes"][hap_rows(heldout_ids)]
            train_af = fitted["donors"].mean(0)
            common = (train_af >= 0.01) & (train_af <= 0.99)
            markers = selected_markers(train_af, 128)
            splits.append(
                {
                    "population": population,
                    "seed": seed,
                    "local_samples": data["samples"][local_ids].tolist(),
                    "reference_samples": data["samples"][reference_ids].tolist(),
                    "heldout_samples": data["samples"][heldout_ids].tolist(),
                    "calibration_positions": positions[fitted["features"]].tolist(),
                    "ld_marker_positions": positions[markers].tolist(),
                    "donor_weight_kish_ess": float(1 / np.sum(fitted["weights"] ** 2)),
                    "ess_interpretation": "weight concentration among donor haplotypes; not independent synthetic evidence",
                }
            )
            for method_i, method in enumerate(METHODS):
                generated = generate(fitted, data, method, 1024, seed + 100 * method_i)
                metrics = evaluate(
                    generated, heldout, fitted["donors"], positions, markers, common
                )
                results.append(
                    {
                        "population": population,
                        "seed": seed,
                        "method": method,
                        "n_local": len(local_ids),
                        "n_reference": len(reference_ids),
                        "n_heldout": len(heldout_ids),
                        "n_synthetic": 1024,
                        **metrics,
                    }
                )
            print(f"Completed {population} seed={seed}", flush=True)
    report = {
        "source": manifest,
        "design": {
            "local_n": 20,
            "synthetic_per_run": 1024,
            "prior_chromosomes": PRIOR_CHROMOSOMES,
            "ridge": RIDGE,
            "features": "48 training-common markers plus rs3745274",
            "populations": TARGETS,
            "seeds": SEEDS,
            "relatedness": "sample-ID disjoint; cross-sample kinship not screened",
            "scope": "regional biallelic SNV distribution benchmark, no outcomes",
        },
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "pysam": pysam.__version__,
        },
        "code_sha256": {
            p.name: digest(p)
            for p in [Path(__file__), Path(__file__).with_name("simulation.py")]
        },
        "runs": results,
        "splits": splits,
    }
    (args.out / "metrics.json").write_text(json.dumps(report, indent=2) + "\n")
    # Preselected illustrative export: BEB proxy, first seed; not a Bhutan cohort.
    local_ids, reference_ids, heldout_ids = split(data, "BEB", SEEDS[0])
    fitted = fit(data, local_ids, reference_ids)
    generated = generate(fitted, data, "calibrated_mosaic", 5000, SEEDS[0] + 9000)
    export = write_vcf(args.out / "synthetic_beb_proxy_chr19.vcf.gz", generated, data)
    export.update(
        {
            "population_proxy": "BEB; not Bhutan",
            "method": "calibrated_mosaic",
            "seed": SEEDS[0] + 9000,
            "local_seed": SEEDS[0],
            "n_local_real_people": len(local_ids),
            "n_regional_real_people": len(reference_ids),
            "novel_full_region_haplotype_fraction": new_haplotype_fraction(
                generated, fitted["donors"]
            ),
        }
    )
    (args.out / "export_manifest.json").write_text(json.dumps(export, indent=2) + "\n")
    print(json.dumps(export), flush=True)


if __name__ == "__main__":
    main()
