# Source identity, permissions and evidence snapshot

Checked 6 September 2026. Machine-readable identities and hashes are in
[source_registry.json](source_registry.json). Retrieval success, execution
success and permission to redistribute are separate fields.

## Published model

The [source tree at commit
e4ba27100d17336a53c3465b873e224afa90624a](https://github.com/Clinical-Pharmacy-Saarland-University/5-FU-PBPK-Model/tree/e4ba27100d17336a53c3465b873e224afa90624a)
contains four `.pksim5` files and a README. The README identifies PK-Sim 9.1;
the SQLite project version fields are internal serialization versions and must
not be interpreted as PK-Sim release numbers.

| File | Bytes | Simulations | Observed-data records | Project version |
|---|---:|---:|---:|---:|
| `5-FU_constant_rate_infusions.pksim5` | 83,922,944 | 42 | 48 | 79 |
| `5-FU_chronomodulated_infusions.pksim5` | 74,739,712 | 40 | 48 | 79 |
| `5-FU_injections.pksim5` | 92,151,808 | 38 | 53 | 77 |
| `Uracil_and_5-FU_oral_solutions.pksim5` | 53,432,320 | 15 | 22 | 77 |

Counts were obtained from read-only SQLite queries against the downloaded source
files. They count stored objects, including variants and reused data, and must
not be reported as numbers of independent clinical studies or participants.

No `LICENSE`, `COPYING` or `NOTICE` file occurs in the complete pinned tree;
the README and project descriptions do not specify model-file reuse terms.
The article points readers to these models, but public availability does not
establish a specific commercial or redistribution license. Model reuse and
distribution terms therefore remain **unresolved**. Upstream projects and their
embedded observation arrays are kept in ignored local acquisition storage;
this docs collection publishes identifiers, checksums and qualification findings.
No permission request or message has been sent to the authors.

## Article and supplement

The [Warwick repository record](https://wrap.warwick.ac.uk/id/eprint/182490/)
labels the published article CC BY-NC 4.0; its PDF confirms noncommercial
attribution terms. The record also contains a separate accepted-manuscript
reuse statement. Neither is silently assigned to the GitHub model files.
The article was downloaded and inspected locally, but is linked rather than
mirrored in the public docs repository.

The [publisher](https://doi.org/10.1002/cpt.3181) lists
`cpt3181-sup-0001-Supinfo.pdf` as Data S1. Both its linked `downloadSupplement`
endpoint and the `doi/suppl/.../supinfo/...pdf` route returned HTTP 403 in this
execution. The author-university metadata links to the same publisher endpoint.
The Europe PMC record for PMID 38264789 reports no hosted full text or supplement.
This is an access result for this environment, not a claim that the supplement
does not exist. Its complete study allocations and numerical tables remain
unread until the actual file is obtained and hashed.

The model database is a useful additional source: it contains source simulation
results and Grem observation arrays. Such embedded data do not replace the
supplement's explanation of fitting, demographics or study selection.

## DPYD/CPIC snapshot

The [official July 2026 notice](https://blog.clinpgx.org/cpic-comment-on-pending-dpyd-guideline-update/)
still describes a pending change for causal HapB3 on the execution date. The
live [CPIC DPYD allele endpoint](https://api.cpicpgx.org/v1/allele?genesymbol=eq.DPYD)
returned 84 entries. The causal `c.1129-5923C>G` and combined HapB3 entries both
retain activity value 0.5. Their pending value 0.75 has not been adopted here.

Local `anukriti-pgx-core` is version 0.9.0, commit
`2b1d696951f5a6b2d66140f258eb453068015e49`. Relevant caller, allele, diplotype,
action and provenance files are hashed in the registry. The actual stored
panel has 18 allele rows and 190 diplotype entries; older descriptive counts
inside provenance notes are stale. Freezing these bytes is an identity check,
not a new clinical audit. The clinical-action provenance still marks its own
independent audit as pending.

Before any later clinical evidence update, compare official sources, regenerate
through the core's established scripts, review the resulting clinical changes
and run its regression process. Phase 0 does not amend those tables.

## Permission and access register

| Asset | Access established here | Reuse/distribution disposition |
|---|---|---|
| Pinned 5-FU model projects | Downloaded; read-only inventory and runtime work | Model license unresolved; no public vendoring |
| Marok article | University PDF inspected | CC BY-NC 4.0; linked, not mirrored |
| Marok supplement | Listed by publisher; requests returned 403 | Not acquired; no inferred permission |
| CPIC allele response | Retrieved through official public API | Hash and selected factual state recorded; no clinical-table update |
| Partner oncology participant records | Not supplied | Access and derivative permissions pending |
| Himalayan controlled-access individual genomes | Metadata only in prior research | No acquisition/permission claim in Phase 0 |

The public acquisition/runtime scripts are Anukriti's work. Third-party runtime
components retain their own licenses; process isolation does not remove those
obligations. The runtime lock must distinguish release-specific licenses and
the still-unresolved model terms before any distribution decision.
