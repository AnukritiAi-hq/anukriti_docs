import numpy as np
import pytest

from experiment import FOCUS_POS, split, write_vcf
from simulation import calibrate_weights, mosaic_haplotypes, offspring


def test_meiosis_inherits_only_from_corresponding_parent():
    mother = np.array([[0, 0, 1, 0], [1, 0, 0, 0]])
    father = np.array([[1, 1, 1, 1], [1, 0, 1, 0]])
    genetic_map = np.array([0, 0.1, 0.5, 1.0])
    children = [
        offspring(mother, father, genetic_map, genetic_map, np.random.default_rng(seed))
        for seed in range(100)
    ]
    for child in children:
        assert np.all((child[0] == mother[0]) | (child[0] == mother[1]))
        assert np.all((child[1] == father[0]) | (child[1] == father[1]))
        assert child[0, 1] == 0 and child[1, 2] == 1
    assert len({child.tobytes() for child in children}) > 4


def test_no_recombination_copies_intact_parental_homologues():
    parent = np.array([[0, 0, 0], [1, 1, 1]])
    child = offspring(parent, parent, [0, 0, 0], [0, 0, 0], np.random.default_rng(1))
    assert all(np.unique(row).size == 1 for row in child)
    with pytest.raises(ValueError):
        offspring(parent, parent, [0, 1, 0], [0, 0, 0], np.random.default_rng(1))


def test_calibration_moves_distribution_toward_local_target():
    donors = np.array([[0], [0], [0], [1]])
    weights = calibrate_weights(donors, [0.7])
    fitted_frequency = float((weights @ donors)[0])
    assert abs(fitted_frequency - 0.7) < 0.02
    assert np.isclose(weights.sum(), 1) and np.all(weights > 0)


def test_mosaic_preserves_protected_block_and_can_create_new_combinations():
    donors = np.array([[0] * 9, [1] * 9], dtype=np.uint8)
    positions = np.arange(0, 225000, 25000)
    kwargs = dict(
        donors=donors,
        positions=positions,
        count=200,
        weights=[0.5, 0.5],
        protected=[(49000, 151000)],
    )
    a = mosaic_haplotypes(rng=np.random.default_rng(8), **kwargs)
    b = mosaic_haplotypes(rng=np.random.default_rng(8), **kwargs)
    assert np.array_equal(a, b)
    block = (positions >= 49000) & (positions <= 151000)
    assert np.all(a[:, block] == a[:, block][:, :1])
    assert any(len(np.unique(row)) == 2 for row in a)


def test_population_splits_exclude_heldout_and_other_superpopulations():
    data = {
        "populations": np.array(["BEB"] * 30 + ["PJL"] * 10 + ["CHB"] * 10),
        "superpopulations": np.array(["SAS"] * 40 + ["EAS"] * 10),
    }
    local, reference, test = split(data, "BEB", 7)
    assert len(local) == 20 and len(test) == 10
    assert set(reference) == set(range(30, 40))
    assert set(local).isdisjoint(test)


def test_export_roundtrips_phased_genotypes(tmp_path):
    data = {
        "positions": np.array([FOCUS_POS, FOCUS_POS + 10]),
        "refs": np.array(["G", "A"]),
        "alts": np.array(["T", "C"]),
    }
    generated = np.array([[0, 1], [1, 0], [1, 1], [1, 0]], dtype=np.uint8)
    result = write_vcf(tmp_path / "example.vcf.gz", generated, data)
    assert result["all_genotypes_roundtrip_verified"]
    assert result["samples"] == 2 and result["variants"] == 2
    assert (tmp_path / "example.vcf.gz.tbi").exists()
