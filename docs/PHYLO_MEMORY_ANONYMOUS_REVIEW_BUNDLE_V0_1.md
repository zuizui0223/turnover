# Anonymous peer-review bundle contract v0.1

Status: **DRAFT — technically reproducible, open-source licence pending**

Target journal: *Methods in Ecology and Evolution* (double-anonymous review).

## Purpose

This bundle is the anonymous review surface for the truth-assignability manuscript. It contains only known-truth simulation contracts, canonical result summaries, analysis/verification code, figure-generation code, and the archived workflow evidence supporting the reported mechanism results. Observed trait values and observed phylogenetic-memory effects are not required or included.

## Included evidence stages

- v0.1 full known-truth measurability programme
- v0.2 calibration-versus-recovery decomposition
- v0.2.1 trait/family breadth audit
- v0.3.1 structural realizability audit
- v0.3.1 OU validity/accessibility decomposition
- v0.4.1 symmetric-Mk2 generator substitution
- v0.5 balance-normalized attenuation audit

Each archived aggregate artifact is downloaded by immutable GitHub Actions artifact ID and checked against the SHA-256 recorded in the canonical result JSON before inclusion.

## Identity firewall

The generated bundle:
- contains no `.git` directory or commit history;
- does not include PR text, author names, title-page metadata, or repository URLs;
- scans unpacked text for the repository-owner identifier and email-address patterns;
- contains a neutral review README generated inside CI.

## Artifact content audit

A direct audit of all seven aggregate workflow artifacts was completed on 2026-10-05.

- downloaded ZIP SHA-256 values matched the hashes recorded in the canonical result files;
- unpacked artifact text contained no repository-owner identifier, email address or GitHub repository URL;
- system-level evidence consists of known-truth diagnostics such as calibration status, recovery summaries, tree/sample geometry, generator parameters, mismatch prevalence and mechanism classifications;
- no observed trait-value field or observed phylogenetic-memory-effect field was present in the evidence tables;
- artifacts that carry explicit outcome-firewall flags record `real_trait_values_used = false` and `real_memory_effects_used = false`.

This audit supports use of the immutable aggregate artifacts in the double-anonymous review package.

## Scientific firewall

The bundle excludes the unexecuted alternative-estimator v0.4 design from the primary review surface. The primary mechanism programme remains closed under `phylo_memory_mechanism_stop_v0_5_2.json` and `phylo_memory_mechanism_close_v0_5_3.json`.

## Submission blocker

The repository currently has **no open-source LICENSE file**. MEE requires submitted code to carry an open-source licence. After the author chooses a licence, the development repository may carry the normal licence while an author-neutral `LICENSE_REVIEW.txt` supplies the same licence terms to the double-anonymous review bundle. The workflow never copies a potentially identifying root licence blindly.
