#!/usr/bin/env python3
"""Build coauthor-review manuscript and supplement DOCX/PDF inputs.

Source text: completed, post-discovery AusTraits paper (NOT new analysis).
Source media: PASS figure_manifest.json and PNG/SVG files generated from
original immutable K / LOFO / source-ascertainment summary artifacts.

Generates Markdown staging and Pandoc reference DOCX styles; never calls a
statistical model, reads a trait observation or constructs a new K.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

MAIN_FIGS = {
 "figure1_common_tips_family_organK.png": "Figure 1.",
 "figure3_taxon_vs_source_stages.png": "Figure 2."
}
SUPPLEMENT_FIG = "figure2_family_holdout_Brier.png"
SUPPLEMENT_LABEL = "Supplementary Figure S1."
EXPECTED_FIGURE_RUNS = {
 "module_lofo": 38686389859,
 "transition": 39202352075,
 "joint_source_K": 39006469805
}


def must(ok, name):
    if not ok:
        raise ValueError(name)


def section(markdown, title):
    # Pull exactly one static prose subsection without interpreting data.
    start = markdown.find("### "+title)
    must(start >= 0, "Missing manuscript section: "+title)
    after = markdown[start+len("### "+title):]
    end = re.search(r"\n#{2,3} ", after)
    return after[:end.start()].strip() if end else after.strip()


def make_reference_doc(path, landscape=False):
    d = Document()
    sec = d.sections[0]
    if landscape:
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
        sec.left_margin=sec.right_margin=Cm(1.65)
        sec.top_margin=sec.bottom_margin=Cm(1.6)
    else:
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
        sec.left_margin=sec.right_margin=Cm(2.35)
        sec.top_margin=sec.bottom_margin=Cm(2.0)
    normal = d.styles["Normal"]
    normal.font.name="Liberation Serif"
    normal.font.size=Pt(9.5 if landscape else 10.5)
    normal.paragraph_format.space_after=Pt(6)
    normal.paragraph_format.line_spacing=1.18
    for name,pts in [("Title",17),("Heading 1",14),("Heading 2",11.8),
                     ("Heading 3",10.6)]:
        s=d.styles[name]
        s.font.name="Liberation Sans"
        s.font.size=Pt(pts)
        s.font.bold=True
        s.paragraph_format.space_before=Pt(10)
        s.paragraph_format.space_after=Pt(5)
    # Default python-docx templates do not expose a "Table Normal" style
    # in every version. Tables inherit Normal; don't assume this style exists.
    foot=sec.footer.paragraphs[0]
    foot.text="Internal scientific review draft — post-discovery AusTraits results; not submitted"
    foot.alignment=WD_ALIGN_PARAGRAPH.CENTER
    foot.style="Caption"
    for run in foot.runs:
        run.font.size=Pt(8)
    d.save(path)


def strip_front_matter(md):
    # The manuscript opening has status lines; retain its title and formal
    # abstract, but use one clean coauthor-review document status, not hidden
    # author names or a fabricated submission record.
    md=re.sub(r"\*\*Manuscript draft v0\.2[^\n]*\n","",md,count=1)
    md=re.sub(r"\*\*Status:\*\*[^\n]*\n","",md,count=1)
    title,sep,remaining=md.partition("\n")
    must(bool(sep) and title.startswith("# "), "Original manuscript title absent")
    status=(
      "**COAUTHOR SCIENTIFIC REVIEW DRAFT • 20 October 2026**\n\n"
      "Exploratory, post-discovery analysis; no independent primary-source "
      "replication or verified evolutionary mechanism. Not submitted.\n\n")
    return title+"\n\n"+status+remaining.lstrip()


def build_review_sources(main_path, supp_path, media_dir, out_dir):
    text=main_path.read_text(encoding="utf-8")
    supplement=supp_path.read_text(encoding="utf-8")
    manifest_path=media_dir/"figure_manifest.json"
    must(manifest_path.exists(),"Missing source figure manifest")
    manifest=json.loads(manifest_path.read_text())
    must(manifest.get("status")=="PASS_SOURCE_LINKED_REPORTING_FIGURES",
         "Figure manifest is not original source-linked PASS")
    must(manifest.get("source_workflow_runs")==EXPECTED_FIGURE_RUNS,
         "Original figure workflow run IDs mutated")
    must(manifest.get("new_biological_effects")==0,"Figure builder opened new effects")
    must(len(manifest.get("outputs",[]))==6,"Original three figures incomplete")
    for p in [*MAIN_FIGS, SUPPLEMENT_FIG]:
        must((media_dir/p).stat().st_size>4000,"Figure missing/empty: "+p)
        must((media_dir/p.replace(".png",".svg")).stat().st_size>4000,
             "Vector figure missing: "+p)

    for must_phrase in (
      "non-nested hypothesis selection",
      "natural logarithm",
      "313/406",
      "314/397",
      "110/142",
      "121/142",
      "120/142",
      "81/101",
      "phytools::phylosig"
    ):
        must(must_phrase.casefold() in text.casefold(),
             "Reporting/technical limitation missing: "+must_phrase)
    must("Supplementary data tables" in supplement,"Supplementary denominator sheet absent")

    # Prepare main body up through its formal results/discussion, then add only
    # journal-relevant secondary matter (not production storyboard/checklists).
    split=text.find("### Figure assignments")
    must(split>0,"Original manuscript editorial section boundary missing")
    main=strip_front_matter(text[:split].rstrip())
    main+="\n\n## Source-resolved supplementary reporting\n\n"
    main+="Supplementary Tables S1–S3 provide the complete source and taxon support denominators, conditional family-held-out prediction scores and exact matched-identity three-stage descriptive transitions. These are **post-discovery** within-AusTraits results; neither source access nor release of aggregate values demonstrates new independent original observations.\n\n"
    for title in ("Data and code availability","Research ethics and statistical scope"):
        main+="## "+title+"\n\n"+section(text,title)+"\n\n"
    main+="## References\n\n"+section(text,"Selected references and reproducibility sources")+"\n\n"
    main+="## Figures and captions\n\n"
    captions=section(text, "Verified main-figure sources and captions (reporting only)")
    def caption_for(label):
        marker="**"+label+"** "
        pos=captions.find(marker)
        must(pos>=0, "Specific Figure caption missing: "+label)
        rest=captions[pos+len(marker):]
        nxt=re.search(r"\n\n\*\*(?:Figure [12]|Supplementary Figure S1)\.",rest)
        return (rest[:nxt.start()] if nxt else rest).strip()

    for image,caption_header in MAIN_FIGS.items():
        figure_num=caption_header.split()[1].strip(".")
        main+=f"### Figure {figure_num}\n\n"
        main+=f"![](figures/{image}){{width=5.9in}}\n\n"
        main+=f"**{caption_header}** {caption_for(caption_header)}\n\n"
    supplement_caption=caption_for(SUPPLEMENT_LABEL)
    must("post" in supplement_caption.lower() and "64.47%" in supplement_caption,
         "Supplementary Brier caption lacks redundancy caveat")

    # No bibliography fabrication, no author/title-page identity.
    supp="# Supplementary tables — coauthor review\n\n"
    supp+="**AusTraits organ-K post-discovery analysis • 20 October 2026.** "
    supp+="The tables are reporting-only and share the main manuscript's evidence boundaries.\n\n"
    supp+=supp_path.read_text(encoding="utf-8")
    supp+="\n\n## Supplementary Figure S1. Conditional Brier scoring\n\n"
    supp+=f"![Supplementary original source figure](figures/{SUPPLEMENT_FIG})\n\n"
    supp+=f"**{SUPPLEMENT_LABEL}** {supplement_caption}\n"
    out_dir.mkdir(parents=True,exist_ok=True)
    (out_dir/"manuscript_review.md").write_text(main,encoding="utf-8")
    (out_dir/"supplement_review.md").write_text(supp,encoding="utf-8")
    make_reference_doc(out_dir/"reference_manuscript.docx",False)
    make_reference_doc(out_dir/"reference_supplement.docx",True)
    return {
       "status":"READY_FOR_COAUTHOR_RENDER_NOT_SUBMISSION",
       "main_figures":sorted(MAIN_FIGS),
       "supplementary_figure":SUPPLEMENT_FIG,
       "original_source_run_ids":EXPECTED_FIGURE_RUNS,
       "input_sha256":{
         "main_manuscript":hashlib.sha256(main_path.read_bytes()).hexdigest(),
         "supplement":hashlib.sha256(supp_path.read_bytes()).hexdigest(),
         "figure_manifest":hashlib.sha256(manifest_path.read_bytes()).hexdigest()
       },
       "assertions":{
         "no_new_models_or_K":True,
         "post_discovery_status_explicit":True,
         "figure_provenance_pinned":True,
         "submission_authorization_obtained":False,
       }
    }


def main():
    p=argparse.ArgumentParser()
    for n in ("manuscript","supplementary","figures","out-dir"):
        p.add_argument("--"+n,required=True,type=Path)
    a=p.parse_args()
    out=build_review_sources(a.manuscript,a.supplementary,a.figures,a.out_dir)
    (a.out_dir/"source_manifest.json").write_text(json.dumps(out,indent=2)+"\n")
    (a.out_dir/"README.txt").write_text(
        "AusTraits functional organ K — coauthor scientific review bundle\n"
        "Generated 2026-10-20 from exact original source-output figures.\n\n"
        "CONTENTS: Main manuscript PDF/DOCX; supplemental tables PDF/DOCX; "
        "original 2 main + 1 supplementary figure PNG/SVG; source_manifest.json and source-only QA.\n\n"
        "IMPORTANT INFERENTIAL CORRECTION: The 64.47% / 65.46% organ-only "
        "hard accuracy is EXACTLY the same post-selected reproductive-higher K "
        "count with half-credit for within-organ ties, not a second independent "
        "biological result. Brier improvements are conditional retrospective "
        "Brier prediction scores, not separate calibration; model selection was non-nested.\n\n"
        "Important: This is a post-discovery exploratory analysis, "
        "NOT independently confirmed or submitted. Figure source run IDs and "
        "immutable SHA256 hashes are in source_manifest.json and the original figure_manifest.json.\n"
        "This package excludes source-native raw trait records and does not "
        "establish reuse rights for nonpublic data.\n"
        "Original repository PR: https://github.com/zuizui0223/turnover/pull/38\n",
        encoding="utf-8")
    print(json.dumps(out,indent=2))


if __name__=="__main__":
    main()
