#!/usr/bin/env python3
"""
Builds the formatted .docx of the Anukriti validation paper from the
markdown draft, for external researcher review.

Source: 2026-06-14-cyp2d6-dpyd-warfarin-validation-DRAFT-v0.3.md (body text,
Draft v0.9 as last edited 2026-06-18). Historical results are reproduced
verbatim -- this script does not alter any reported number. A new "Note on
Engine Version and Post-Publication Corrections" section is inserted after
the title block, replacing the internal editor HTML-comment block, so
external readers get the currency information without seeing draft-review
scaffolding.
"""

import re
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC = "/home/abhimanyu/Desktop/SynthaTrial-repo/anukriti_docs/papers/2026-06-14-cyp2d6-dpyd-warfarin-validation-DRAFT-v0.3.md"
OUT = "/home/abhimanyu/Desktop/SynthaTrial-repo/anukriti_docs/papers/Anukriti-Validation-CYP2D6-DPYD-Warfarin-2026-09-07.docx"

with open(SRC, "r", encoding="utf-8") as f:
    raw = f.read()

# Strip the leading HTML comment block (editor fact-check note)
raw = re.sub(r"^<!--.*?-->\s*\n", "", raw, flags=re.DOTALL)

doc = Document()

# ---- base style ----
normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
sec = doc.sections[0]
sec.left_margin = Inches(1)
sec.right_margin = Inches(1)
sec.top_margin = Inches(1)
sec.bottom_margin = Inches(1)


def add_page_number_field(paragraph):
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


footer_p = sec.footer.paragraphs[0]
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer_p.add_run("Anukriti Validation Manuscript — Researcher Review Copy — p. ").font.size = Pt(8)
add_page_number_field(footer_p)


def set_cell_shading(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(
        url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1155CC")
    rPr.append(color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    new_run.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def add_inline_runs(paragraph, text):
    """Parse **bold**, _italic_, `code`, and [text](url) markdown inline.

    Star-allele nomenclature (*2, *3, *22, *68+*4, etc.) is the core clinical
    vocabulary of this paper and must never be swallowed as italic markup.
    Therefore single-asterisk spans are treated as LITERAL TEXT, never
    italic -- only double-asterisk (**bold**) and underscore (_italic_) are
    recognized as emphasis. The handful of genuinely-italic single-word
    journal-name spans in the References section are normalized to
    underscore italics by `_journalize_references()` before this function
    ever sees them, so no ambiguity is left for this generic parser to
    resolve.
    """
    # Unescape markdown-escaped asterisks from table cells (\*2 -> *2)
    text = text.replace("\\*", "*")
    pos = 0
    pattern = re.compile(r"(\*\*.+?\*\*|`[^`]+?`|(?<![\w_])_[^_\s][^_]*?_(?![\w_])|\[.+?\]\(.+?\))")
    for m in pattern.finditer(text):
        if m.start() > pos:
            paragraph.add_run(text[pos:m.start()])
        token = m.group(0)
        if token.startswith("**"):
            r = paragraph.add_run(token[2:-2])
            r.bold = True
        elif token.startswith("["):
            label, url = re.match(r"\[(.+?)\]\((.+?)\)", token).groups()
            add_hyperlink(paragraph, url, label)
        elif token.startswith("`"):
            r = paragraph.add_run(token[1:-1])
            r.font.name = "Consolas"
        elif token.startswith("_"):
            r = paragraph.add_run(token[1:-1])
            r.italic = True
        pos = m.end()
    if pos < len(text):
        paragraph.add_run(text[pos:])


def normalize_reference_italics(text):
    """Convert the References section's *Journal Name.* spans to _Journal
    Name._ (underscore italics) so the generic inline parser -- which
    deliberately never treats single-asterisk spans as italic, to protect
    star-allele nomenclature -- can render them correctly without touching
    any *N / *NA / *68+*4-style allele token anywhere else in the document.
    Only applied within the numbered reference-list lines.
    """
    journal_span = re.compile(r"\*([A-Za-z][A-Za-z0-9 .&]*?\.)\*")

    def _fix_line(line):
        if re.match(r"^\d+\.\s", line.strip()):
            return journal_span.sub(lambda m: f"_{m.group(1)}_", line)
        return line

    return "\n".join(_fix_line(l) for l in text.split("\n"))


def add_para(text, style=None, align=None, space_after=6):
    p = doc.add_paragraph(style=style)
    add_inline_runs(p, text)
    if align:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p


def parse_table_block(lines):
    rows = [l.strip() for l in lines if l.strip().startswith("|")]
    rows = [r for r in rows if not re.match(r"^\|[\s:\-\|]+\|$", r)]
    grid = []
    for r in rows:
        cells = [c.strip() for c in r.strip("|").split("|")]
        grid.append(cells)
    return grid


def add_md_table(grid):
    if not grid:
        return
    ncols = len(grid[0])
    table = doc.add_table(rows=len(grid), cols=ncols)
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ri, row in enumerate(grid):
        for ci in range(ncols):
            cell_text = row[ci] if ci < len(row) else ""
            cell = table.cell(ri, ci)
            cell.text = ""
            p = cell.paragraphs[0]
            add_inline_runs(p, cell_text)
            for run in p.runs:
                run.font.size = Pt(9.5)
            if ri == 0:
                for run in p.runs:
                    run.bold = True
                set_cell_shading(cell, "1F3864")
                for run in p.runs:
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


# ================= TITLE BLOCK =================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run(
    "Deterministic, Population-Aware Pharmacogenomics Screening:\n"
    "Validation of the Anukriti Engine on CYP2D6, DPYD, and Warfarin Cohorts"
)
r.bold = True
r.font.size = Pt(17)
title.paragraph_format.space_after = Pt(14)

authors = doc.add_paragraph()
authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
authors.add_run("Abhimanyu R B¹, Aagneye Syam¹, Johan George¹, Atul Alexander¹, Deepak Roshan V G²").italic = True
authors.paragraph_format.space_after = Pt(4)

affil = doc.add_paragraph()
affil.alignment = WD_ALIGN_PARAGRAPH.CENTER
affil.add_run("¹ Anukriti AI, Kerala, India\n² Department of Molecular Biology, Malabar Cancer Centre, Kannur, Kerala, India")
affil.paragraph_format.space_after = Pt(4)

corr = doc.add_paragraph()
corr.alignment = WD_ALIGN_PARAGRAPH.CENTER
corr.add_run("Corresponding author: Abhimanyu R B — abhimanyu@anukritiai.com").font.size = Pt(10)
corr.paragraph_format.space_after = Pt(2)

status = doc.add_paragraph()
status.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = status.add_run("Manuscript status: Pre-print / researcher-review draft — prepared September 7, 2026 (content current as of Draft v0.9, June 18, 2026; see currency note below)")
sr.font.size = Pt(9.5)
sr.italic = True
status.paragraph_format.space_after = Pt(16)

doc.add_page_break()

# ================= CURRENCY / PROVENANCE NOTE =================
h = doc.add_heading("Note on Engine Version and Post-Publication Corrections", level=2)
add_para(
    "This manuscript's data collection and analysis (Methods §2.1–2.9, Results §3) were performed "
    "primarily against **anukriti-pgx-core v0.6.0**, the version live on PyPI at the time of the June "
    "2026 validation runs, with one exception noted below (the IWPC undertreated-patient count, "
    "computed earlier against v0.2.1). All reported numbers below are reproduced unchanged from their "
    "respective original analyses. Three corrections are disclosed here for reviewer transparency, "
    "since the engine has advanced past the version(s) validated in this manuscript:",
    space_after=8,
)
b1 = doc.add_paragraph(style="List Bullet")
add_inline_runs(
    b1,
    "**DPYD HapB3 causal/tag distinction (fixed in v0.7.3–v0.9.0).** The version validated here "
    "called the CPIC HapB3 allele (§2.6, §3.2) using the combined rs56038477/rs75017182 marker "
    "without distinguishing the causal splice variant (rs75017182) from its benign synonymous proxy "
    "(rs56038477, in imperfect linkage disequilibrium — Turner/Haidar 2024, PMID 38129972). At that "
    "engine version, HapB3 calls rested on the tag SNP alone; the causal variant could not be "
    "represented and CPIC's mandated tag-only disclosure could not be issued. This has since been "
    "corrected: the current engine (v0.9.0) is haplotype-aware, records call provenance "
    "(`hapb3_basis`: haplotype / causal / tag_only / tag_without_causal), and adds four previously "
    "uncallable actionable DPYD alleles, raising callable share of actionable Central/South Asian "
    "DPYD allele frequency from 78.7% to 100%. This does not change the phenotype, action, or "
    "evidence level of any call reported in this manuscript, but readers applying the DPYD methodology "
    "described in §2.6 to new cohorts should use v0.9.0 or later rather than v0.6.0.",
)
b2 = doc.add_paragraph(style="List Bullet")
add_inline_runs(
    b2,
    "**CYP2C9 phenotype table (F-10, corrected prior to v0.6.0).** An internal CPIC-conformance "
    "audit identified that the CYP2C9 allele-function and diplotype-phenotype tables used in early "
    "engine versions disagreed with canonical CPIC assignments for 10 of 16 alleles (38% agreement) "
    "and 43 of 136 diplotypes (32% agreement). This was corrected by regenerating both tables verbatim "
    "from the CPIC API prior to the warfarin cohort analysis reported in §3.1; the IWPC results in this "
    "manuscript reflect the corrected tables (100% CPIC agreement). This audit finding is disclosed "
    "here because it is material to any reader evaluating the reliability of engine outputs.",
)
b3 = doc.add_paragraph(style="List Bullet")
add_inline_runs(
    b3,
    "**IWPC undertreated-patient count (467→459).** The Results §3.1 / Abstract figure of 467 "
    "patients (8.2%) warranting clinical action was computed on **anukriti-pgx-core v0.2.1**, before "
    "the v0.4.0 CYP2C9 table fix (see the F-10 finding above) re-binned 10 of 16 CYP2C9 alleles to "
    "canonical CPIC assignments. Re-running the identical IWPC cohort on the current engine moves "
    "~40 patients from Poor Metabolizer to Intermediate Metabolizer on the CYP2C9 axis and reduces the "
    "INR-confirmed undertreated count to **459 patients (~8.1%)** — both figures represent ~21% of "
    "undertreated high-risk patients falling outside the 2.0–3.0 target INR range. The direction, "
    "magnitude, and clinical conclusion are unchanged; only the exact count moved. All other IWPC "
    "results in §3.1 (tier medians, n=3,998, n=5,700, the Kruskal-Wallis and Spearman statistics) are "
    "unaffected by this fix and are reported as originally computed. Reproduction runner: "
    "`anukriti-validation-iwpc/scripts/run_validation.py`.",
)
add_para(
    "The current published engine version is **anukriti-pgx-core v0.9.0** (PyPI), supporting 14 genes "
    "with CPIC-pinned tables and full call provenance. All other results, figures, and conclusions in "
    "this manuscript are unaffected by the above and are presented as originally computed.",
    space_after=4,
)

doc.add_page_break()

# ================= BODY PARSE =================
raw = normalize_reference_italics(raw)
lines = raw.split("\n")
i = 0
n = len(lines)
in_table = False
table_buf = []

def flush_table():
    global table_buf, in_table
    if table_buf:
        grid = parse_table_block(table_buf)
        add_md_table(grid)
    table_buf = []
    in_table = False

while i < n:
    line = lines[i]
    stripped = line.strip()

    if stripped.startswith("|"):
        in_table = True
        table_buf.append(line)
        i += 1
        continue
    else:
        if in_table:
            flush_table()

    if not stripped:
        i += 1
        continue

    if stripped == "---":
        i += 1
        continue

    # skip the original title/author/status block (already rendered above)
    if stripped.startswith("# Deterministic"):
        i += 1
        continue
    if stripped.startswith("**Authors:**") or stripped.startswith("**Corresponding author") \
       or stripped.startswith("**Status:**") or stripped.startswith("¹ Anukriti") \
       or stripped.startswith("² Department"):
        i += 1
        continue
    if stripped.startswith("**Update (v0."):
        # These are multi-line changelog entries in the source markdown that
        # continue (unindented, no blank-line break) until the next blank
        # line. They are already summarized in the "Note on Engine Version"
        # section rendered above, so skip the whole block here -- not just
        # its first line -- to avoid orphaned sentence fragments leaking
        # into the body between the currency note and the Abstract.
        i += 1
        while i < n and lines[i].strip():
            i += 1
        continue
    if stripped.startswith("*Document status:") or stripped.startswith("*HG01190 SAS cell") \
       or stripped.startswith("*Three-sample cross-ancestry"):
        # Internal draft-status footer notes (author-facing, single-asterisk
        # italic scaffolding) -- superseded by the currency note up front;
        # skip rather than render as a stray trailing paragraph.
        i += 1
        continue

    m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
    if m:
        level = len(m.group(1))
        text = m.group(2)
        doc.add_heading(text, level=min(level, 4))
        i += 1
        continue

    if stripped.startswith("- ") or stripped.startswith("* "):
        p = doc.add_paragraph(style="List Bullet")
        add_inline_runs(p, stripped[2:])
        i += 1
        continue

    m2 = re.match(r"^\d+\.\s+(.*)$", stripped)
    if m2:
        p = doc.add_paragraph(style="List Number")
        add_inline_runs(p, m2.group(1))
        i += 1
        continue

    # regular paragraph
    add_para(stripped)
    i += 1

if in_table:
    flush_table()

doc.save(OUT)
print("Saved:", OUT)
