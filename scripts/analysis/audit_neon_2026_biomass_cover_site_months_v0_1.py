#!/usr/bin/env python3
"""NEON RELEASE-2026 public metadata-only multisite herb biomass/cover source gate.

No biomass or species cover records are downloaded. A passing overlap is
only a catalog-level requirement, NOT proof that plots/dates actually join.
"""
import argparse, collections, hashlib, json, time
import urllib.request, urllib.error
from pathlib import Path
BASE="https://data.neonscience.org/api/v0"
RELEASE="RELEASE-2026"
PRODUCTS={
    "herbaceous_measured_mass":"DP1.10023.001",
    "plant_species_cover":"DP1.10058.001",
}
def get(path):
    url=BASE+path
    req=urllib.request.Request(url,headers={"User-Agent":"turnover-neon-source-only/0.1",
                                           "Accept":"application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=100) as res:
                data=res.read(80_000_001)
            if len(data)>80_000_000:
                raise ValueError('NEON site-only metadata response exceeds safe 80MB size limit')
            root=json.loads(data)
            if not isinstance(root,dict) or not isinstance(root.get("data"),(dict,list)):
                raise ValueError("Unexpected NEON JSON data field")
            return root["data"], hashlib.sha256(data).hexdigest()
        except (ValueError,urllib.error.URLError, TimeoutError):
            if attempt==2:raise
            time.sleep(2**attempt)
def extract_site_months(product):
    sites={}
    for entry in product["siteCodes"]:
        code=entry.get("siteCode")
        available=entry.get("availableReleases",[])
        matches=[a for a in available if a.get("release")==RELEASE]
        if not code or len(matches)!=1:
            continue
        months=set(matches[0].get("availableMonths",[]))
        if months:
            sites[code]=months
    return sites
def main():
    a,b={},{}
    for label,product_id in PRODUCTS.items():
        obj,sha=get("/products/"+product_id+"?release="+RELEASE)
        if obj.get("productCode")!=product_id:raise ValueError("Product ID mismatch")
        a[label]=extract_site_months(obj)
        b[label]={"product_id":product_id,"sha256_json":sha,
                  "n_available_sites":len(a[label]),
                  "n_site_months":sum(len(x) for x in a[label].values()),
                  "source_release":RELEASE}
    sites,sha=get("/sites")
    if not isinstance(sites,list):
        raise ValueError("site endpoint lacks expected list")
    domains={str(x.get("siteCode")):str(x.get("domainCode")) for x in sites
             if x.get("siteCode") and x.get("domainCode")}
    common=sorted(set(a["herbaceous_measured_mass"])&
                  set(a["plant_species_cover"]))
    shared={s:sorted(a["herbaceous_measured_mass"][s] &
                     a["plant_species_cover"][s]) for s in common}
    shared={s:m for s,m in shared.items() if m}
    eco=sorted({domains[s] for s in shared if s in domains})
    n_month=sum(len(m) for m in shared.values())
    status=("TIER0_NEON_SHARED_RELEASE_SITE_MONTH_CATALOG_PASS"
            if len(shared)>=12 and len(eco)>=4 and n_month>=24 and
               len({s for s in shared if s in domains})==len(shared)
            else "TIER0_NEON_SHARED_RELEASE_SOURCE_HOLD")
    out={
        "version":"v0.1","status":status,"release":RELEASE,
        "products":b,
        "n_distinct_site_codes":len(shared),
        "n_shared_site_months":n_month,
        "n_distinct_ecoregion_domains":len(eco),
        "ecoregion_domains":eco,
        "site_catalog_sha256":sha,
        "site_catalog_rows":len(sites),
        "source_independent_site_months_by_site":shared,
        "source_known_domain_by_site":{s:domains[s] for s in shared if s in domains},
        "frozen_thresholds":{"min_sites":12,"min_domains":4,"min_shared_site_months":24},
        "scope":"availability catalog only, not observed samples, not actual plot-level join, no trait FD or biomass effects",
        "hard_nonclaims":[
          "No exact plotID/subplotID match has been verified",
          "An overlapping calendar month does not guarantee the same sampling date or position",
          "Herbaceous clip mass is by group, plant diversity data is by species in different microsites",
          "Releases are common but sampling suspended for some 2026 plots",
          "No direct species-level biomass and no independent trait source has been verified"]
    }
    return out
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    report=main()
    path=Path(args.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("NEON_RELEASE2026_CATALOG_GATE",json.dumps({k:v for k,v in report.items() if
          k not in ("source_independent_site_months_by_site","source_known_domain_by_site")},sort_keys=True))
    if "PASS" not in report["status"]: raise SystemExit(2)
