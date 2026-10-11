# TRY version 7 — metadata-only provenance and trait support request

**Prepared 2026-10-11. NOT SENT.** This is a scoped request template for the researcher's own TRY-registered PI account or authorized TRY administrator discussion. No TRY v7 raw trait observations have been downloaded or requested through this repository.

## Suggested message

**Subject: TRY v7 metadata-only request for source independence and five plant morphological traits**

Dear TRY team,

I am planning an independent validation of specific plant morphological trait phylogenetic-signal rankings previously identified using AusTraits v7.0.0. Before requesting or analyzing numerical trait values, I would like to qualify whether TRY v7 contains independently measured, semantically matching primary-source data with sufficient species- and family-level support.

The public TRY Data Explorer still identifies itself as based on TRY database version 6.0. Could you confirm the corresponding TRY v7 TraitIDs and precise definitions for the following *candidate* historical IDs?

- Seed width: 239
- Seed dry mass (single seed): 26
- Leaf width (lamina): 145
- Petiole length: 143
- Leaf area without petiole / distinction between compound leaf and leaflet: 3108

Where possible, I would first request **metadata and counts only**, with no trait values, for records in these five groups. The fields useful for qualification are:

- TRY v7 source data version, DatasetID and dataset title; original dataset custodian/publication DOI/citation, a stable original measurement or record-lineage identifier and indication of duplicate/derived records where available.
- TraitID, full standardized definition, native trait-unit concept, leaf-vs-leaflet and petiole inclusion, seed-vs-fruit/diaspore measurement, and summary/individual-record value kind.
- Accepted species/taxon and family, metadata-only distinct species counts by dataset×family×trait, and the number of families represented by two or more of the requested trait types.
- Dataset open/restricted status, usage/citation permissions, and whether a subset excluding AusTraits-derived or shared primary records can be identified.

The prespecified validation eligibility requires at least **10 independent plant families with at least 20 distinct species per trait**, at least **10 families supporting two target traits**, and qualifying data for **at least 4 of the 5 requested trait concepts**. We will not revise these thresholds based on observed trait values or estimates of phylogenetic signal. Our immediate goal is source provenance and sample-size screening, not numerical data release.

Would a metadata-only export or public v7 dataset-level report be possible? If permissions or registration are needed, I can submit the appropriate request under TRY intellectual property guidelines. Please also advise whether the 2019 TRY primary-data-source-reference archive has been superseded by a current v7 provenance mapping.

Thank you for your guidance.

## Source request and integrity notes

- [TRY official request portal](https://www.try-db.org/TryWeb/Prop0.php): registering a PI and accepting TRY intellectual property conditions is required for normal data requests. Any restricted record requires data-custodian authorization.
- [TRY public Data Explorer](https://www.try-db.org/de/de.php): availability metadata; advertises v6.0, not current v7. Do not report its record numbers as v7 counts.
- [TRY public dataset directory](https://www.try-db.org/de/Datasets.php): dataset IDs/titles and public/restricted statuses only, not exact v7 trait support.
- [TRY primary data source references archive](https://www.try-db.org/TryWeb/Data.php): 2019 lineage mapping, not guaranteed current to 2026 v7.
- [AusTraits source provenance audit](https://github.com/zuizui0223/turnover/blob/analysis/brownian-process-null-v0-1/data/try_austraits_public_source_registry_design_v0_1.json): fixed original dataset graph; no selected K hypotheses reopened.
- **Important:** TRY metadata/trait record release formats and permission scope must be honored; do not commit any nonpublic catalogue, data values or measurement IDs to public GitHub without authorization.
- Do not interpret a successful metadata request as replication. Qualification and actual held-out named-rank testing are separate scientific stages.

**Current state:** Prepared, not submitted. TRY v7 independent-source status is HOLD.
