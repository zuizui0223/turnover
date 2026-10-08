#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,re,urllib.request
from pathlib import Path
import duckdb,yaml

DOI_RE=re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+",re.I)

def norm_doi(x):
    if x is None: return None
    s=str(x).strip()
    s=re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)","",s,flags=re.I)
    m=DOI_RE.search(s)
    if not m: return None
    d=m.group(0).lower().rstrip(".,;")
    # Remove unmatched terminal punctuation only.
    while d.endswith(")") and d.count("(")<d.count(")"): d=d[:-1]
    while d.endswith("]") and d.count("[")<d.count("]"): d=d[:-1]
    return d

def fetch_primary_doi(dataset_id,commit):
    url=f"https://raw.githubusercontent.com/traitecoevo/austraits.build/{commit}/data/{dataset_id}/metadata.yml"
    try:
        with urllib.request.urlopen(url,timeout=30) as r:
            obj=yaml.safe_load(r.read().decode("utf-8"))
    except Exception:
        return None,"FETCH_OR_PARSE_FAILURE"
    try:
        doi=obj.get("source",{}).get("primary",{}).get("doi")
    except Exception:
        doi=None
    return norm_doi(doi),None

ap=argparse.ArgumentParser()
ap.add_argument("--austraits-parquet",type=Path,required=True)
ap.add_argument("--austraits-core",type=Path,required=True)
ap.add_argument("--traits-yml",type=Path,required=True)
ap.add_argument("--bien-citations",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()
a.out.parent.mkdir(parents=True,exist_ok=True)

cfg=yaml.safe_load(a.traits_yml.read_text())["traits"]["elements"]
core=list(csv.DictReader(a.austraits_core.open(newline="")))
if not core: raise SystemExit("empty AusTraits final core")
families={r["family"] for r in core}; traits={r["trait_name"] for r in core}
if len(families)<12 or len(traits)<4: raise SystemExit("AusTraits final core below frozen minimum")
for r in core:
    if r["trait_name"] not in cfg: raise SystemExit(f"trait missing config: {r['trait_name']}")
    r["config_type"]=str(cfg[r["trait_name"]].get("type","")).strip()
    if r["config_type"] not in {"numeric","categorical"}:
        raise SystemExit(f"unsupported config type: {r['trait_name']} {r['config_type']}")

con=duckdb.connect(database=":memory:")
con.execute("CREATE TEMP TABLE core(family VARCHAR,trait_name VARCHAR,config_type VARCHAR)")
con.executemany("INSERT INTO core VALUES (?,?,?)",[(r["family"],r["trait_name"],r["config_type"]) for r in core])

sql=r"""
WITH base AS (
  SELECT
    trim(CAST(a.family AS VARCHAR)) AS family,
    trim(CAST(a.trait_name AS VARCHAR)) AS trait_name,
    trim(CAST(a.binomial AS VARCHAR)) AS species,
    trim(CAST(a.dataset_id AS VARCHAR)) AS dataset_id,
    trim(CAST(a.value AS VARCHAR)) AS value_text,
    c.config_type
  FROM read_parquet(?) a
  JOIN core c
    ON trim(CAST(a.family AS VARCHAR))=c.family
   AND trim(CAST(a.trait_name AS VARCHAR))=c.trait_name
  WHERE lower(trim(CAST(a.taxon_rank AS VARCHAR)))='species'
    AND a.binomial IS NOT NULL AND trim(CAST(a.binomial AS VARCHAR))<>''
    AND a.dataset_id IS NOT NULL AND trim(CAST(a.dataset_id AS VARCHAR))<>''
    AND a.value IS NOT NULL AND trim(CAST(a.value AS VARCHAR))<>''
),
numeric_ids AS (
  SELECT DISTINCT dataset_id
  FROM base
  WHERE config_type='numeric'
),
cat_counts AS (
  SELECT family,trait_name,species,value_text,count(*) AS n
  FROM base
  WHERE config_type='categorical'
  GROUP BY family,trait_name,species,value_text
),
cat_ranked AS (
  SELECT *,max(n) OVER(PARTITION BY family,trait_name,species) AS max_n
  FROM cat_counts
),
cat_species AS (
  SELECT family,trait_name,species,
         count(*) FILTER(WHERE n=max_n) AS n_modal
  FROM cat_ranked
  GROUP BY family,trait_name,species
),
cat_ids AS (
  SELECT DISTINCT b.dataset_id
  FROM base b
  JOIN cat_species s USING(family,trait_name,species)
  WHERE b.config_type='categorical' AND s.n_modal=1
)
SELECT DISTINCT dataset_id
FROM (
  SELECT dataset_id FROM numeric_ids
  UNION ALL
  SELECT dataset_id FROM cat_ids
) z
ORDER BY dataset_id
"""
dataset_ids=[r[0] for r in con.execute(sql,[str(a.austraits_parquet)]).fetchall()]
con.close()

commit="7fbf6c8169a7eaf9a184e48c171cb63f2b1e2b8c"
austraits_dois={}
failures=[]
for ds in dataset_ids:
    doi,err=fetch_primary_doi(ds,commit)
    if doi: austraits_dois[ds]=doi
    elif err: failures.append(ds)

bien_citations=[]
with a.bien_citations.open(newline="") as fh:
    for r in csv.DictReader(fh):
        if r.get("source_citation"): bien_citations.append(r["source_citation"])
bien_dois=sorted({d for x in bien_citations if (d:=norm_doi(x))})
aust_doi_set=sorted(set(austraits_dois.values()))
overlap=sorted(set(aust_doi_set)&set(bien_dois))
coverage=(len(austraits_dois)/len(dataset_ids)) if dataset_ids else 0.0
overlap_fraction=(len(overlap)/len(aust_doi_set)) if aust_doi_set else None

if overlap_fraction==0 and coverage>=0.80:
    label="INDEPENDENT_SOURCE_REPLICATION"
elif overlap_fraction is not None and 0<overlap_fraction<=0.10 and coverage>=0.80:
    label="LOW_OVERLAP_REPLICATION"
else:
    label="INDEPENDENT_COMPILATION_VALIDATION"

out={
  "version":"v0.5",
  "status":"AUSTRAITS_BIEN_PROVENANCE_OVERLAP_AUDITED",
  "outcome_blind":True,
  "austraits_memory_effects_opened":False,
  "n_final_core_systems":len(core),
  "n_final_core_families":len(families),
  "n_final_core_traits":len(traits),
  "n_austraits_contributing_dataset_ids":len(dataset_ids),
  "n_austraits_dataset_ids_with_primary_doi":len(austraits_dois),
  "austraits_primary_doi_coverage":coverage,
  "n_austraits_unique_primary_dois":len(aust_doi_set),
  "n_bien_source_citations":len(bien_citations),
  "n_bien_unique_dois":len(bien_dois),
  "n_overlapping_unique_dois":len(overlap),
  "overlap_fraction_of_austraits_dois":overlap_fraction,
  "n_metadata_fetch_or_parse_failures":len(failures),
  "replication_language":label,
  "selection_changed_by_overlap":False,
  "caution":"DOI non-overlap does not prove that no individual measurements were ever shared across compilations."
}
a.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(json.dumps(out,indent=2,sort_keys=True))
