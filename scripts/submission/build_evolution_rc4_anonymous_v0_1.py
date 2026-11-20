#!/usr/bin/env python3
"""Build anonymous editable RC4 Word manuscript with vetted, source-derived figures."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

ROOT=Path(__file__).resolve().parents[2]
MANUSCRIPT=ROOT/"docs/TRAIT_MEMORY_EVOLUTION_MANUSCRIPT_RC4_CLEANED_V0_1.md"
CAPTIONS=ROOT/"docs/TRAIT_MEMORY_EVOLUTION_RC4_FIGURE_CAPTIONS_V0_1.md"
FIGURES=("Fig1_source_correction_identity.png","Fig2_measurement_aware_point_shares.png","Fig3_raw_vs_log_trait_portability.png")
OMIT={"Teaser text","RC4 evidence and figure status"}

def check(b,t):
    if not b: raise AssertionError(t)

def inline(p,s):
    s=re.sub(r"\[([^\]]+)\]\([^)]+\)",r"\1",s)
    for bit in re.split(r"(\*\*[^*\n]+\*\*|(?<!\*)\*[^*\n]+\*(?!\*))",s):
        if not bit: continue
        if bit.startswith("**") and bit.endswith("**"):p.add_run(bit[2:-2]).bold=True
        elif bit.startswith("*") and bit.endswith("*"):p.add_run(bit[1:-1]).italic=True
        else:p.add_run(bit.replace(chr(96),""))

def chunks(text):
    active=True;acc=[]
    def flush():
        nonlocal acc
        if acc and active:yield "paragraph"," ".join(acc)
        acc=[]
    for line in text.splitlines():
        s=line.strip()
        if s.startswith("# "):
            yield from flush();yield "title",s[2:];continue
        if s.startswith("## "):
            yield from flush()
            section=s[3:].strip();active=section not in OMIT
            if active:yield "heading1",section
            continue
        if s.startswith("### "):
            yield from flush()
            if active:yield "heading2",s[4:]
            continue
        if not active:continue
        if not s:yield from flush();continue
        if s.startswith("- "):
            yield from flush();yield "bullet",s[2:];continue
        acc.append(s)
    yield from flush()

def load_captions():
    source=CAPTIONS.read_text()
    out={}
    for n in (1,2,3):
        m=re.search(rf"^## Figure {n}\.[^\n]*\n(.*?)(?=^## |\Z)",source,re.M|re.S)
        check(m is not None,f"Figure {n} source missing")
        c=re.search(r"\*\*Caption\.\*\*\s*(.*?)(?=\n\s*\*\*Alt text\.\*\*)",m[1],re.S)
        a=re.search(r"\*\*Alt text\.\*\*\s*(.*?)(?=\n\s*$)",m[1],re.S)
        check(c is not None and a is not None,f"Figure {n} caption/alt missing")
        cap=" ".join(c[1].split());alt=" ".join(a[1].split())
        check(len(cap)>100 and len(alt)>30,f"Figure {n} caption unqualified")
        out[n]=(cap,alt)
    return out

def doc_styles(doc):
    for n in ("Normal","Title","Heading 1","Heading 2","List Bullet"):
        style=doc.styles[n]
        style.font.name="Times New Roman";style.font.size=Pt(12)
        style.paragraph_format.line_spacing=2
        style.paragraph_format.space_after=Pt(0)
    for n in ("Title","Heading 1","Heading 2"):doc.styles[n].font.bold=True
    s=doc.styles.add_style("RC4 Figure Caption",WD_STYLE_TYPE.PARAGRAPH)
    s.font.name="Times New Roman";s.font.size=Pt(11)
    s.paragraph_format.line_spacing=1.5
    s.paragraph_format.space_after=Pt(2)

def line_numbers(section):
    ln=OxmlElement("w:lnNumType")
    ln.set(qn("w:countBy"),"1");ln.set(qn("w:restart"),"continuous");ln.set(qn("w:distance"),"360")
    section._sectPr.append(ln)

def page_footer(section):
    p=section.footer.paragraphs[0]
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing=1
    r=p.add_run()
    for name,value in (("begin",None),("instrText"," PAGE "),("separate",None),("t","1"),("end",None)):
        node=OxmlElement("w:instrText" if name=="instrText" else "w:t" if name=="t" else "w:fldChar")
        if name in ("begin","separate","end"):node.set(qn("w:fldCharType"),name)
        if name=="instrText":
            node.set(qn("xml:space"),"preserve");node.text=value
        if name=="t":node.text=value
        r._r.append(node)

def main(fig_dir,out_dir):
    source=MANUSCRIPT.read_text()
    check(len(source)>20000 and "201/201" in source and "5.92%" in source,"Wrong RC4 manuscript")
    caps=load_captions()
    check(all((fig_dir/name).is_file() for name in FIGURES),"Validated figures missing")
    out_dir.mkdir(parents=True,exist_ok=True)
    doc=Document();sec=doc.sections[0]
    sec.page_width=Inches(8.5);sec.page_height=Inches(11)
    sec.top_margin=Inches(.88);sec.bottom_margin=Inches(.82)
    sec.left_margin=Inches(.92);sec.right_margin=Inches(.84)
    sec.footer_distance=Inches(.45)
    line_numbers(sec);page_footer(sec);doc_styles(doc)
    blocks=list(chunks(source))
    check(blocks and blocks[0][0]=="title","No title")
    headers=[s for k,s in blocks if k=="heading1"]
    check(all(x in headers for x in ("Abstract","Keywords","Introduction","Materials and Methods","Results","Discussion","References")),"Sections absent")
    check(not any(x in headers for x in OMIT),"Internal provenance leaked")
    in_references=False
    for kind,t in blocks:
        if kind=="title":
            p=doc.add_paragraph(style="Title");p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after=Pt(12);inline(p,t)
        elif kind=="heading1":
            in_references=t=="References"
            p=doc.add_paragraph(style="Heading 1")
            p.paragraph_format.keep_with_next=True;p.paragraph_format.space_before=Pt(9)
            inline(p,t)
        elif kind=="heading2":
            p=doc.add_paragraph(style="Heading 2")
            p.paragraph_format.keep_with_next=True;p.paragraph_format.space_before=Pt(7)
            inline(p,t)
        else:
            p=doc.add_paragraph(style="List Bullet" if kind=="bullet" else "Normal")
            p.paragraph_format.widow_control=True
            if in_references:
                p.paragraph_format.left_indent=Inches(.26)
                p.paragraph_format.first_line_indent=Inches(-.26)
            elif kind!="bullet":
                p.paragraph_format.first_line_indent=Inches(.22)
            inline(p,t)
    for n,name in enumerate(FIGURES,1):
        p=doc.add_paragraph()
        p.page_break_before=True;p.paragraph_format.space_after=Pt(3)
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        shape=p.add_run().add_picture(str(fig_dir/name),width=Inches(6.7))
        shape._inline.docPr.set("descr",caps[n][1])
        shape._inline.docPr.set("title",f"Figure {n}")
        caption=doc.add_paragraph(style="RC4 Figure Caption")
        caption.paragraph_format.keep_together=True
        cap=re.sub(r"(\*\*|\*)","",caps[n][0])
        inline(caption,f"Figure {n}. "+cap)
    props=doc.core_properties
    props.title=blocks[0][1];props.subject="Anonymous Evolution RC4 manuscript"
    props.author="Anonymous";props.last_modified_by="Anonymous"
    props.keywords="phylogenetic traits; evolutionary memory";props.comments=""
    output=out_dir/"Anonymous_Main_Manuscript_RC4.docx"
    doc.save(output)
    report={"status":"ANONYMOUS_RC4_DOCX_CREATED_SUBMISSION_HOLD",
            "input_figures":list(FIGURES),"sections":headers,
            "figure_alt_descriptions":3,"line_numbers_configured":True,
            "docx":output.name,"models_refitted":False,"submission_ready":False}
    (out_dir/"anonymous_docx_report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--figure-dir",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    main(args.figure_dir,args.output_dir)
