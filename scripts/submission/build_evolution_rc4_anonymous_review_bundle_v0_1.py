#!/usr/bin/env python3
"""Build a neutral, author-identity-free 201-system RC4 evidence/code ZIP for review.

Original BIEN species records are intentionally absent. No new statistical fit is run.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,shutil,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
TABLE="results/trait_memory_positive_only_cleaning_impact_v0_2/effects_positive_only_cleaned_recovered_v0_2.csv"
STAGE="results/trait_memory_positive_only_cleaning_impact_v0_2/result.json"
MODEL_SCRIPTS=[
 "scripts/analysis/fit_trait_memory_measurement_aware_v0_3.R",
 "scripts/analysis/test_trait_memory_portability_blup_v0_3.R",
 "scripts/analysis/test_trait_memory_correlated_trait_null_v0_3.R",
 "scripts/figures/render_trait_memory_rc4_cleaned_v0_1.py",
]

def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding="utf-8")

def assemble(output):
    base=output/"Anonymous_RC4_Evidence"
    base.mkdir(parents=True,exist_ok=True)
    for name in [TABLE,STAGE]+MODEL_SCRIPTS:
        p=base/name;p.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,p)
    source=json.loads((ROOT/"data/trait_memory_robustness_design_v0_3.json").read_text())
    # Source CI run IDs and repository refs are removed but exact statistical rules are retained.
    design={"version":source["version"],
            "status":source["status"],
            "measurement_error":source["measurement_error"],
            "correlated_trait_family_null":source["correlated_trait_family_null"],
            "trait_domain_sensitivity":source["trait_domain_sensitivity"]}
    write(base/"data/trait_memory_robustness_design_v0_3.json",json.dumps(design,indent=2)+"\n")
    write(base/"data/rc4_replay_model_contract.json",json.dumps({
        "status":"TRAIT_MEMORY_ROBUST_EFFECTS_AGGREGATED",
        "n_systems":201,"n_families":45,"n_traits":12,
        "source_description":"Source-validity-corrected 201-system derived effects for unchanged model replay",
        "no_original_species_measurements_released":True
    },indent=2)+"\n")
    reader=list(csv.DictReader((base/TABLE).open(newline="",encoding="utf-8")))
    assert len(reader)==201
    assert len({x["system_id"] for x in reader})==201
    assert sum(x["cleaning_status"]=="CLEANED_STAGE_B" for x in reader)==49
    assert sum(x["cleaning_status"]=="CLEAN_UNCHANGED_STAGE_A" for x in reader)==152
    x=json.loads((base/STAGE).read_text())
    assert x["all_201_support_retained"] and x["all_201_cleaned_log_available"]
    readme="""# Anonymous RC4 derived data and reproducible models

These are 201 corrected family-by-trait phylogenetic memory gradient estimates and
species-cluster bootstrap uncertainty from BIEN 4.2.8, plus the frozen downstream
statistical analysis and figure-generation programs used for the accompanying
double-anonymous Evolution manuscript.

Data were corrected under a frozen, biologically justified positive-only source
measurement rule, before examining the corrected effects. The data contain
201 system summaries (45 plant families, 12 traits), not original BIEN species
records, species-level trait values, or species identities.

The 49 source-invalid systems were recomputed; 152 untouched systems were
retained identically. Both raw and log trait representations are included.
The original biological measurements are not redistributed.

R >= 4.4 with packages jsonlite, lme4, metafor, Matrix and MASS is required
for model replay. Python with numpy and matplotlib renders the frozen figures.

Reproduce the crossed model, training-only family holdout BLUP prediction and
original correlated-trait null from the recovered table:

Rscript scripts/analysis/fit_trait_memory_measurement_aware_v0_3.R \
  --effects results/trait_memory_positive_only_cleaning_impact_v0_2/effects_positive_only_cleaned_recovered_v0_2.csv \
  --aggregate-json data/rc4_replay_model_contract.json \
  --out out/measurement_aware.json --bootstrap-table out/cluster_bootstrap.csv

Rscript scripts/analysis/test_trait_memory_portability_blup_v0_3.R \
  --effects results/trait_memory_positive_only_cleaning_impact_v0_2/effects_positive_only_cleaned_recovered_v0_2.csv \
  --aggregate-json data/rc4_replay_model_contract.json \
  --out out/blup.json --predictions out/blup_predictions.csv

Rscript scripts/analysis/test_trait_memory_correlated_trait_null_v0_3.R \
  --effects results/trait_memory_positive_only_cleaning_impact_v0_2/effects_positive_only_cleaned_recovered_v0_2.csv \
  --aggregate-json data/rc4_replay_model_contract.json \
  --out out/correlated_trait_null.json --null-table out/null_draws.csv

python scripts/figures/render_trait_memory_rc4_cleaned_v0_1.py --out-dir out/figures

The manuscript's exact 201-system scientific results have previously been replayed
under the unchanged models. No additional hypothesis selection is intended here.
Results must be interpreted on the defined distance-dissimilarity gradient,
not as evolutionary rates, adaptive mechanisms, or effects on biomass.

The source BIEN and phylogeny resource usage requirements remain binding.
This anonymous review archive is NOT an approved final public data release.
After acceptance, authors will supply a licensed, versioned public archive
with a persistent accession/DOI under the publisher's data policies.

AI-assisted-development disclosure: ChatGPT (OpenAI) assisted drafting
and debugging some analysis scripts. All computations, reported numerical
results and scientific decisions remain under author responsibility.
"""
    write(base/"README.md",readme)
    files=sorted(p for p in base.rglob("*") if p.is_file())
    prohibited=["zuizui0223","rachelzhang","github.com/","tohoku university",
                "zhang ruiqi"]
    emails=re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
    for p in files:
        raw=p.read_bytes()
        txt=raw.decode("utf-8")
        for needle in prohibited:
            if needle in txt.lower():
                raise ValueError(f"Non-anonymous token in {p.relative_to(base)}: {needle}")
        if emails.search(txt):raise ValueError(f"Email in {p.relative_to(base)}")
        assert not p.name.startswith(".")
    manifest={
        "status":"RC4_DERIVED_201_ANONYMOUS_EVIDENCE_SOURCE_QUALIFIED",
        "n_systems":201,"corrected":49,"inherited":152,
        "original_observation_rows":0,"new_effect_models":0,
        "source_data_licence_review_still_required":True,
        "files":[{"path":str(p.relative_to(base)),
                  "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                  "bytes":p.stat().st_size} for p in files]}
    write(base/"MANIFEST.json",json.dumps(manifest,indent=2)+"\n")
    bundle=output/"Anonymous_RC4_Evidence_Review.zip"
    with zipfile.ZipFile(bundle,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(base.rglob("*")):
            if p.is_file():z.write(p,arcname=str(p.relative_to(output)))
    with zipfile.ZipFile(bundle) as z:
        assert z.testzip() is None
        assert set(x["path"] for x in manifest["files"])==set(
            f.split("/",1)[1] for f in z.namelist()
            if f!="Anonymous_RC4_Evidence/MANIFEST.json")
    status={"status":manifest["status"],"zip":bundle.name,
            "sha256":hashlib.sha256(bundle.read_bytes()).hexdigest(),
            "n_files":len(files)+1,"n_derived_systems":201,
            "submission_ready":False}
    write(output/"anonymous_review_bundle_status.json",json.dumps(status,indent=2)+"\n")
    print(json.dumps(status,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args()
    assemble(a.output_dir)
