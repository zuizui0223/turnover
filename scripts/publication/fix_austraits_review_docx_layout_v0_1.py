#!/usr/bin/env python3
"""Fix coauthor document pagination and supplemental table column geometry.

No substantive content is changed. Inputs are pandoc-produced Word documents.
Layout modifications are deterministic and checked against frozen paper scope.
"""
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import argparse

LANDSCAPE_WIDTHS = {
    6: [2.15, 1.65, .83, 1.70, .85, 2.92],  # source cohort and notes
    7: [1.05, 1.30, 1.28, 1.09, 1.10, 1.15, 3.23],  # prediction losses and CI
    5: [.85, 1.35, 2.35, 2.78, 2.87],  # three stage support
    4: [.85, 3.15, 3.25, 2.95],  # paired direction flips
}

def format_manuscript(path):
    doc=Document(path)
    seen={}
    for p in doc.paragraphs:
        label=p.text.strip()
        if label in {"Figures and captions", "Figure 2", "Figure 3"}:
            p.paragraph_format.page_break_before=True
            seen[label]=seen.get(label,0)+1
    if seen != {"Figures and captions":1,"Figure 2":1,"Figure 3":1}:
        raise ValueError("Figure headings changed: "+repr(seen))
    descriptions=(
        "34 plant families: fraction of same-tip reproductive versus vegetative Blomberg K comparisons higher in each family under S3 and native prune phylogenies.",
        "Original family-held-out Brier loss under pooled, reproductive/vegetative organ, named trait and named-pair predictive priors on both trees.",
        "Fixed family-by-trait-pair K contrast proportions over three stages: broad non-flora taxon support, restricted shared-source taxa, then shared-source values on fixed taxa."
    )
    shapes=doc.inline_shapes
    if len(shapes)!=3:
        raise ValueError("Original three figure assets missing from coauthor manuscript")
    for shape,descr in zip(shapes,descriptions):
        shape._inline.docPr.set("descr",descr)
    doc.save(path)


def set_repeat_header(row):
    trPr=row._tr.get_or_add_trPr()
    flag=OxmlElement("w:tblHeader")
    flag.set(qn("w:val"),"true")
    trPr.append(flag)


def set_no_row_split(row):
    trPr=row._tr.get_or_add_trPr()
    flag=OxmlElement("w:cantSplit")
    trPr.append(flag)


def format_supplement(path):
    doc=Document(path)
    tables=doc.tables
    if [len(t.columns) for t in tables] != [6,7,5,4]:
        raise ValueError("Supplementary table layout/index changed")
    sec=doc.sections[0]
    usable=(sec.page_width-sec.left_margin-sec.right_margin)/914400
    for t in tables:
        widths=LANDSCAPE_WIDTHS[len(t.columns)]
        if not (sum(widths)<usable and sum(widths)>usable-.35):
            raise ValueError(f"Table width exceeds available page: {widths} > {usable}")
        t.autofit=False
        tblPr=t._tbl.tblPr
        pref=tblPr.first_child_found_in("w:tblW")
        if pref is None:
            pref=OxmlElement("w:tblW")
            tblPr.append(pref)
        pref.set(qn("w:type"),"dxa")
        pref.set(qn("w:w"),str(round(sum(widths)*1440)))
        for i,w in enumerate(widths):
            t.columns[i].width=Inches(w)
        set_repeat_header(t.rows[0])
        for i,row in enumerate(t.rows):
            set_no_row_split(row)
            for col,cell in enumerate(row.cells):
                cell.width=Inches(widths[col])
                for para in cell.paragraphs:
                    para.paragraph_format.space_before=Pt(0)
                    para.paragraph_format.space_after=Pt(1.4)
                    para.paragraph_format.line_spacing=1.0
                    for run in para.runs:
                        run.font.size=Pt(7.6)
                        if i==0:
                            run.bold=True
    doc.save(path)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manuscript",type=Path,required=True)
    p.add_argument("--supplement",type=Path,required=True)
    args=p.parse_args()
    format_manuscript(args.manuscript)
    format_supplement(args.supplement)
    print("DOCX_LAYOUT_FIXED: figure page breaks, 4 full-width landscape tables, repeated headers")

if __name__=="__main__":
    main()
