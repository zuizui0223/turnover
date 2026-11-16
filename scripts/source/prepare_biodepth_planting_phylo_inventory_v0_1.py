#!/usr/bin/env python3
"""Source-only original BIODEPTH planted taxon×plot incidence for GBOTB qualification.
No trait values and no plot/year biomass data opened, downloaded or exported.
"""
from __future__ import annotations
import argparse,csv,sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from audit_biodepth_103_taxa_gift_height_v0_1 import source, geometry

def prepare(species_path: str, codes_path: str, out_path: str) -> dict:
    s=source(species_path,"species"); c=source(codes_path,"codes")
    named,plots,meta=geometry(s,c)
    if len(named)!=103 or len(plots)!=480 or sum(len(v) for v in plots.values())!=1934:
        raise ValueError("Original source geometry changed")
    out=Path(out_path);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["site","plot","species"])
        for (site,plot),members in sorted(plots.items()):
            for sp in sorted(members):
                writer.writerow([site,plot,sp])
    return {"status":"BIODEPTH_SOURCE_PLANTING_ONLY_PASS","source_named_taxa":len(named),
            "original_plots":len(plots),"source_sown_incidence":sum(map(len,plots.values())),
            "original_field_sites":len({x[0] for x in plots})}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--species");p.add_argument("--codes");p.add_argument("--out")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        import csv,io
        assert list(csv.reader(io.StringIO("site,plot,species\nGermany,1,poa pratensis\n")))[1][2]=="poa pratensis"
        print("SOURCE_FORMAT_FIXTURE_PASS")
    else:
        if not all((a.species,a.codes,a.out)):p.error("--species --codes --out required")
        print(prepare(a.species,a.codes,a.out))
