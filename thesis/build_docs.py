#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a Word (.docx) document and a print-ready HTML (printable as PDF) for the
PhD thesis "حرية الاستثمار في التشريع الجزائري".

The .docx is created from scratch (no external libraries required) by writing
the OOXML parts directly into a ZIP container.

The HTML uses RTL direction and a serif Arabic-friendly font stack so the user
can open it in a browser and "Print to PDF".
"""

import os
import re
import sys
import zipfile
from xml.sax.saxutils import escape
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT       = os.path.abspath(os.path.dirname(__file__))
CONTENT    = os.path.join(ROOT, "content")
BUILD      = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)

CONTENT_FILES = [
    "00_front.md",
    "01_intro.md",
    "02_part1_chap1.md",
    "03_part1_chap2.md",
    "04_part2_chap1.md",
    "05_part2_chap2.md",
    "06_refs.md",
]

# ---------------------------------------------------------------------------
# Lightweight parser for our custom marker format
# ---------------------------------------------------------------------------
# Each block is introduced by a marker line:
#   # H1 / # H2 / # H3 / # H4   -> headings
#   # P                           -> paragraph
#   # LIST                        -> bulleted list (one item per line)
#   # REFLIST                     -> numbered references list
#   # QUOTE                       -> indented quote block
#   # TITLE / # SUBTITLE          -> cover title and subtitle
#   # DEDICATION / # THANKS       -> dedication / thanks pages (mixed text)
#   # ABBR_TITLE / # ABBR_LIST    -> abbreviations page
# A blank line separates blocks; consecutive non-marker lines belong to the
# preceding marker.

def parse(md_text):
    blocks = []
    cur_kind = None
    cur_lines = []

    def flush():
        nonlocal cur_kind, cur_lines
        if cur_kind is not None:
            blocks.append((cur_kind, "\n".join(cur_lines).strip("\n")))
        cur_kind = None
        cur_lines = []

    for raw in md_text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^#\s+([A-Z_0-9]+)\s*$", line)
        if m:
            flush()
            cur_kind = m.group(1)
            cur_lines = []
            continue
        if cur_kind is None:
            # ignore stray text before first marker
            continue
        cur_lines.append(line)
    flush()
    return blocks


def load_all_blocks():
    all_blocks = []
    for name in CONTENT_FILES:
        path = os.path.join(CONTENT, name)
        with open(path, "r", encoding="utf-8") as f:
            md = f.read()
        all_blocks.append((name, parse(md)))
    return all_blocks


# ===========================================================================
# DOCX builder (no external libs — emit OOXML directly)
# ===========================================================================

# Minimum needed parts:
#  [Content_Types].xml
#  _rels/.rels
#  word/_rels/document.xml.rels
#  word/document.xml
#  word/styles.xml
#  word/settings.xml
#  word/numbering.xml
#  word/fontTable.xml
#  word/theme/theme1.xml (optional, omitted)
#  docProps/core.xml
#  docProps/app.xml

CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="xml" ContentType="application/xml"/>
 <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
 <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
 <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
 <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
 <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
 <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
 <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
 <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
 <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
 <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
 <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
</Relationships>'''

CORE_XML_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <dc:title>حرية الاستثمار في التشريع الجزائري</dc:title>
 <dc:creator>أطروحة دكتوراه</dc:creator>
 <cp:lastModifiedBy>Auto</cp:lastModifiedBy>
 <dcterms:created xsi:type="dcterms:W3CDTF">{ts}</dcterms:created>
 <dcterms:modified xsi:type="dcterms:W3CDTF">{ts}</dcterms:modified>
</cp:coreProperties>'''

APP_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
            xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
 <Application>thesis-builder</Application>
 <Company></Company>
</Properties>'''

SETTINGS_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
 <w:zoom w:percent="110"/>
 <w:defaultTabStop w:val="720"/>
 <w:characterSpacingControl w:val="doNotCompress"/>
 <w:themeFontLang w:val="ar-DZ" w:eastAsia="" w:bidi="ar-DZ"/>
 <w:bidi/>
</w:settings>'''

FONT_TABLE_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
 <w:font w:name="Traditional Arabic"><w:family w:val="roman"/></w:font>
 <w:font w:name="Amiri"><w:family w:val="roman"/></w:font>
 <w:font w:name="Sakkal Majalla"><w:family w:val="roman"/></w:font>
 <w:font w:name="Times New Roman"><w:family w:val="roman"/></w:font>
</w:fonts>'''

# Numbering definitions: list 1 = bullet, list 2 = decimal numbers
NUMBERING_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
 <w:abstractNum w:abstractNumId="0">
  <w:lvl w:ilvl="0">
   <w:start w:val="1"/>
   <w:numFmt w:val="bullet"/>
   <w:lvlText w:val="\u2022"/>
   <w:lvlJc w:val="right"/>
   <w:pPr><w:bidi/><w:ind w:start="720" w:hanging="360"/></w:pPr>
   <w:rPr><w:rFonts w:cs="Traditional Arabic"/></w:rPr>
  </w:lvl>
 </w:abstractNum>
 <w:abstractNum w:abstractNumId="1">
  <w:lvl w:ilvl="0">
   <w:start w:val="1"/>
   <w:numFmt w:val="decimal"/>
   <w:lvlText w:val="%1."/>
   <w:lvlJc w:val="right"/>
   <w:pPr><w:bidi/><w:ind w:start="720" w:hanging="360"/></w:pPr>
  </w:lvl>
 </w:abstractNum>
 <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
 <w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>
</w:numbering>'''

STYLES_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
 <w:docDefaults>
  <w:rPrDefault>
   <w:rPr>
    <w:rFonts w:ascii="Traditional Arabic" w:hAnsi="Traditional Arabic" w:cs="Traditional Arabic" w:eastAsia="Traditional Arabic"/>
    <w:sz w:val="28"/><w:szCs w:val="28"/>
    <w:lang w:val="ar-DZ" w:bidi="ar-DZ"/>
   </w:rPr>
  </w:rPrDefault>
  <w:pPrDefault>
   <w:pPr>
    <w:bidi/>
    <w:spacing w:before="60" w:after="120" w:line="360" w:lineRule="auto"/>
    <w:jc w:val="both"/>
   </w:pPr>
  </w:pPrDefault>
 </w:docDefaults>
 <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
  <w:name w:val="Normal"/>
  <w:rPr><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>
 </w:style>
 <w:style w:type="paragraph" w:styleId="H1">
  <w:name w:val="Heading 1"/>
  <w:basedOn w:val="Normal"/>
  <w:next w:val="Normal"/>
  <w:pPr>
   <w:bidi/>
   <w:spacing w:before="600" w:after="240" w:line="360" w:lineRule="auto"/>
   <w:jc w:val="center"/>
   <w:pageBreakBefore/>
  </w:pPr>
  <w:rPr><w:b/><w:bCs/><w:sz w:val="44"/><w:szCs w:val="44"/></w:rPr>
 </w:style>
 <w:style w:type="paragraph" w:styleId="H2">
  <w:name w:val="Heading 2"/>
  <w:basedOn w:val="Normal"/>
  <w:next w:val="Normal"/>
  <w:pPr>
   <w:bidi/>
   <w:spacing w:before="360" w:after="180" w:line="360" w:lineRule="auto"/>
   <w:jc w:val="right"/>
  </w:pPr>
  <w:rPr><w:b/><w:bCs/><w:sz w:val="36"/><w:szCs w:val="36"/></w:rPr>
 </w:style>
 <w:style w:type="paragraph" w:styleId="H3">
  <w:name w:val="Heading 3"/>
  <w:basedOn w:val="Normal"/>
  <w:next w:val="Normal"/>
  <w:pPr>
   <w:bidi/>
   <w:spacing w:before="240" w:after="120" w:line="360" w:lineRule="auto"/>
   <w:jc w:val="right"/>
  </w:pPr>
  <w:rPr><w:b/><w:bCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>
 </w:style>
 <w:style w:type="paragraph" w:styleId="H4">
  <w:name w:val="Heading 4"/>
  <w:basedOn w:val="Normal"/>
  <w:next w:val="Normal"/>
  <w:pPr>
   <w:bidi/>
   <w:spacing w:before="180" w:after="100" w:line="360" w:lineRule="auto"/>
   <w:jc w:val="right"/>
  </w:pPr>
  <w:rPr><w:b/><w:bCs/><w:i/><w:iCs/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>
 </w:style>
 <w:style w:type="paragraph" w:styleId="Quote">
  <w:name w:val="Quote"/>
  <w:basedOn w:val="Normal"/>
  <w:pPr>
   <w:bidi/>
   <w:ind w:start="720" w:end="720"/>
   <w:spacing w:before="120" w:after="120" w:line="360" w:lineRule="auto"/>
   <w:jc w:val="both"/>
  </w:pPr>
  <w:rPr><w:i/><w:iCs/></w:rPr>
 </w:style>
 <w:style w:type="paragraph" w:styleId="Title">
  <w:name w:val="Title"/>
  <w:basedOn w:val="Normal"/>
  <w:pPr>
   <w:bidi/>
   <w:spacing w:before="0" w:after="240" w:line="360" w:lineRule="auto"/>
   <w:jc w:val="center"/>
  </w:pPr>
  <w:rPr><w:b/><w:bCs/><w:sz w:val="56"/><w:szCs w:val="56"/></w:rPr>
 </w:style>
 <w:style w:type="paragraph" w:styleId="Subtitle">
  <w:name w:val="Subtitle"/>
  <w:basedOn w:val="Normal"/>
  <w:pPr>
   <w:bidi/>
   <w:spacing w:before="0" w:after="240" w:line="360" w:lineRule="auto"/>
   <w:jc w:val="center"/>
  </w:pPr>
  <w:rPr><w:i/><w:iCs/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>
 </w:style>
</w:styles>'''


def w_run(text, *, bold=False, italic=False, size=None, br_before=False):
    text = escape(text).replace("\n", "</w:t><w:br/><w:t xml:space=\"preserve\">")
    rpr = ""
    if bold or italic or size:
        rpr_inner = ""
        if bold:
            rpr_inner += "<w:b/><w:bCs/>"
        if italic:
            rpr_inner += "<w:i/><w:iCs/>"
        if size:
            rpr_inner += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        rpr = f"<w:rPr>{rpr_inner}</w:rPr>"
    return f'<w:r>{rpr}<w:rtl/><w:t xml:space="preserve">{text}</w:t></w:r>'


def w_para(style, text, *, jc=None, page_break=False, num_id=None):
    ppr_extra = ""
    if jc:
        ppr_extra += f'<w:jc w:val="{jc}"/>'
    if page_break:
        ppr_extra += '<w:pageBreakBefore/>'
    if num_id is not None:
        ppr_extra += f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num_id}"/></w:numPr>'
    style_xml = f'<w:pStyle w:val="{style}"/>' if style else ''
    ppr = f'<w:pPr>{style_xml}<w:bidi/>{ppr_extra}</w:pPr>'
    if text == "":
        return f'<w:p>{ppr}</w:p>'
    run = w_run(text)
    return f'<w:p>{ppr}{run}</w:p>'


def w_blank():
    return '<w:p><w:pPr><w:bidi/></w:pPr></w:p>'


def w_pagebreak():
    return '<w:p><w:pPr><w:bidi/></w:pPr><w:r><w:br w:type="page"/></w:r></w:p>'


def build_document_body(all_blocks):
    out = []

    # ----- Cover page -----
    front_blocks = dict(all_blocks[0][1]) if all_blocks else {}
    title = ""
    subtitle = ""
    # find TITLE / SUBTITLE among front blocks
    for kind, content in all_blocks[0][1]:
        if kind == "TITLE":
            title = content
        elif kind == "SUBTITLE":
            subtitle = content

    out.append(w_blank())
    out.append(w_blank())
    out.append(w_para("Title", "الجمهورية الجزائرية الديمقراطية الشعبية"))
    out.append(w_para("Normal", "وزارة التعليم العالي والبحث العلمي", jc="center"))
    out.append(w_para("Normal", "جامعة …  -  كلية الحقوق والعلوم السياسية", jc="center"))
    out.append(w_blank())
    out.append(w_blank())
    out.append(w_blank())
    # title may itself contain newlines
    for line in title.splitlines():
        out.append(w_para("Title", line))
    out.append(w_blank())
    for line in subtitle.splitlines():
        out.append(w_para("Subtitle", line))
    out.append(w_blank())
    out.append(w_blank())
    out.append(w_blank())
    out.append(w_para("Normal", "إعـــداد الطالــب:                                          إشـــراف الأستــاذ:", jc="center"))
    out.append(w_para("Normal", "....................                                                ....................", jc="center"))
    out.append(w_blank())
    out.append(w_blank())
    out.append(w_para("Normal", "أعضاء لجنة المناقشة:", jc="center"))
    out.append(w_para("Normal", "الأستاذ ..................................   رئيسًا", jc="center"))
    out.append(w_para("Normal", "الأستاذ ..................................   مشرفًا ومقرّرًا", jc="center"))
    out.append(w_para("Normal", "الأستاذ ..................................   مناقشًا", jc="center"))
    out.append(w_para("Normal", "الأستاذ ..................................   مناقشًا", jc="center"))
    out.append(w_para("Normal", "الأستاذ ..................................   مناقشًا", jc="center"))
    out.append(w_para("Normal", "الأستاذ ..................................   مناقشًا", jc="center"))
    out.append(w_blank())
    out.append(w_blank())
    out.append(w_para("Normal", "السنة الجامعية: …… / ……", jc="center"))

    # ----- Walk all blocks across files -----
    # Skip TITLE/SUBTITLE at re-render (they were used on cover).
    for fi, (fname, blocks) in enumerate(all_blocks):
        for kind, content in blocks:
            if kind in ("TITLE", "SUBTITLE"):
                continue
            if kind == "DEDICATION":
                out.append(w_pagebreak())
                # split content into paras (single newlines), keeping markup ## as H2
                for para in content.split("\n\n"):
                    para = para.strip()
                    if not para:
                        continue
                    if para.startswith("##"):
                        out.append(w_para("H2", para.lstrip("# ").strip(), jc="center"))
                    else:
                        out.append(w_para("Normal", para, jc="center"))
            elif kind == "THANKS":
                out.append(w_pagebreak())
                for para in content.split("\n\n"):
                    para = para.strip()
                    if not para:
                        continue
                    if para.startswith("##"):
                        out.append(w_para("H2", para.lstrip("# ").strip(), jc="center"))
                    else:
                        out.append(w_para("Normal", para))
            elif kind == "ABBR_TITLE":
                out.append(w_pagebreak())
                for para in content.split("\n\n"):
                    para = para.strip()
                    if not para:
                        continue
                    if para.startswith("##"):
                        out.append(w_para("H2", para.lstrip("# ").strip(), jc="center"))
                    else:
                        out.append(w_para("Normal", para))
            elif kind == "ABBR_LIST":
                # rows separated by " | "
                for line in content.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    if "|" in line:
                        left, _, right = line.partition("|")
                        # Render as "abbreviation : meaning"
                        out.append(w_para("Normal",
                                          f"{left.strip()}  :  {right.strip()}"))
                    else:
                        out.append(w_para("Normal", line))
            elif kind == "H1":
                out.append(w_para("H1", content))
            elif kind == "H2":
                out.append(w_para("H2", content))
            elif kind == "H3":
                out.append(w_para("H3", content))
            elif kind == "H4":
                out.append(w_para("H4", content))
            elif kind == "P":
                # split on blank lines into multiple <w:p>
                for para in re.split(r"\n\s*\n", content):
                    para = para.strip()
                    if para:
                        out.append(w_para("Normal", para))
            elif kind == "QUOTE":
                for para in re.split(r"\n\s*\n", content):
                    para = para.strip()
                    if para:
                        out.append(w_para("Quote", para))
            elif kind == "LIST":
                for item in content.splitlines():
                    item = item.strip()
                    if item:
                        out.append(w_para("Normal", item, num_id=1))
            elif kind == "REFLIST":
                for item in content.splitlines():
                    item = item.strip()
                    if item:
                        out.append(w_para("Normal", item, num_id=2))
            else:
                # unknown: render as paragraph
                out.append(w_para("Normal", content))

    return "\n".join(out)


def build_document_xml(all_blocks):
    body = build_document_body(all_blocks)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <w:body>
{body}
  <w:sectPr>
   <w:pgSz w:w="11906" w:h="16838"/>
   <w:pgMar w:top="1418" w:right="1418" w:bottom="1418" w:left="1418" w:header="708" w:footer="708" w:gutter="0"/>
   <w:bidi/>
   <w:cols w:space="708"/>
   <w:docGrid w:linePitch="360"/>
  </w:sectPr>
 </w:body>
</w:document>'''


def write_docx(out_path, all_blocks):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    document_xml = build_document_xml(all_blocks)
    core_xml     = CORE_XML_TEMPLATE.format(ts=ts)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/styles.xml", STYLES_XML)
        z.writestr("word/settings.xml", SETTINGS_XML)
        z.writestr("word/numbering.xml", NUMBERING_XML)
        z.writestr("word/fontTable.xml", FONT_TABLE_XML)
        z.writestr("docProps/core.xml", core_xml)
        z.writestr("docProps/app.xml", APP_XML)


# ===========================================================================
# HTML builder (printable as PDF from any browser)
# ===========================================================================

HTML_TEMPLATE_HEAD = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>حرية الاستثمار في التشريع الجزائري</title>
<style>
@page {{
    size: A4;
    margin: 2.5cm 2.5cm 2.5cm 2.5cm;
}}
html, body {{
    direction: rtl;
    text-align: justify;
    font-family: "Traditional Arabic", "Sakkal Majalla", "Amiri", "Noto Naskh Arabic",
                 "Arabic Typesetting", "Times New Roman", serif;
    font-size: 14pt;
    line-height: 1.9;
    color: #111;
    background: #fff;
}}
body {{
    max-width: 18cm;
    margin: 1.5cm auto;
    padding: 0 1cm;
}}
@media print {{
    body {{ max-width: none; margin: 0; padding: 0; }}
}}
h1 {{
    font-size: 24pt;
    text-align: center;
    margin-top: 2em;
    margin-bottom: 1em;
    page-break-before: always;
    border-bottom: 2px solid #333;
    padding-bottom: 0.4em;
}}
h1:first-of-type {{ page-break-before: auto; }}
h2 {{
    font-size: 19pt;
    text-align: right;
    margin-top: 1.6em;
    margin-bottom: 0.8em;
    color: #1a1a1a;
}}
h3 {{
    font-size: 16pt;
    text-align: right;
    margin-top: 1.4em;
    margin-bottom: 0.6em;
}}
h4 {{
    font-size: 14pt;
    font-style: italic;
    text-align: right;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
}}
p {{ margin: 0.4em 0 0.8em 0; text-indent: 1.5em; }}
blockquote {{
    margin: 1em 2em;
    padding: 0.5em 1em;
    border-right: 4px solid #888;
    background: #fafafa;
    font-style: italic;
}}
ul, ol {{ margin: 0.5em 2em 1em 0; padding-right: 1em; }}
li {{ margin: 0.3em 0; }}
.cover {{
    text-align: center;
    height: 27cm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    page-break-after: always;
}}
.cover .uni {{ font-size: 16pt; line-height: 1.6; }}
.cover .title {{ font-size: 28pt; font-weight: bold; line-height: 1.6; }}
.cover .subtitle {{ font-size: 18pt; font-style: italic; line-height: 1.6; }}
.cover .meta {{ font-size: 14pt; line-height: 2; }}
.dedication {{
    text-align: center;
    font-size: 16pt;
    line-height: 2;
    page-break-after: always;
    padding-top: 4cm;
}}
.thanks {{
    line-height: 2.1;
    page-break-after: always;
    padding-top: 2cm;
}}
.abbr-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 13pt;
}}
.abbr-table th, .abbr-table td {{
    border: 1px solid #999;
    padding: 0.4em 0.6em;
    vertical-align: top;
}}
.abbr-table th {{ background: #eee; }}
.section-divider {{ page-break-before: always; }}
</style>
</head>
<body>
'''

HTML_TEMPLATE_FOOT = '''
</body>
</html>
'''


def html_escape(t):
    return escape(t).replace("\n", "<br>")


def render_html(all_blocks):
    out = [HTML_TEMPLATE_HEAD]

    # Cover
    title = ""
    subtitle = ""
    for kind, content in all_blocks[0][1]:
        if kind == "TITLE":
            title = content
        elif kind == "SUBTITLE":
            subtitle = content

    out.append('<div class="cover">')
    out.append('<div class="uni">الجمهورية الجزائرية الديمقراطية الشعبية<br>'
               'وزارة التعليم العالي والبحث العلمي<br>'
               'جامعة …  -  كلية الحقوق والعلوم السياسية</div>')
    out.append(f'<div class="title">{html_escape(title)}</div>')
    out.append(f'<div class="subtitle">{html_escape(subtitle)}</div>')
    out.append('<div class="meta">'
               'إعداد الطالب: ....................<br>'
               'إشراف الأستاذ: ....................<br><br>'
               'أعضاء لجنة المناقشة:<br>'
               'الأستاذ ........................   رئيسًا<br>'
               'الأستاذ ........................   مشرفًا ومقرّرًا<br>'
               'الأستاذ ........................   مناقشًا<br>'
               'الأستاذ ........................   مناقشًا<br>'
               'الأستاذ ........................   مناقشًا<br>'
               'الأستاذ ........................   مناقشًا<br><br>'
               'السنة الجامعية: …… / ……'
               '</div>')
    out.append('</div>')

    for fi, (fname, blocks) in enumerate(all_blocks):
        for kind, content in blocks:
            if kind in ("TITLE", "SUBTITLE"):
                continue
            if kind == "DEDICATION":
                out.append('<div class="dedication">')
                for para in content.split("\n\n"):
                    para = para.strip()
                    if not para:
                        continue
                    if para.startswith("##"):
                        out.append(f'<h2>{html_escape(para.lstrip("# ").strip())}</h2>')
                    else:
                        out.append(f'<p style="text-indent:0">{html_escape(para)}</p>')
                out.append('</div>')
            elif kind == "THANKS":
                out.append('<div class="thanks">')
                for para in content.split("\n\n"):
                    para = para.strip()
                    if not para:
                        continue
                    if para.startswith("##"):
                        out.append(f'<h2 style="text-align:center">{html_escape(para.lstrip("# ").strip())}</h2>')
                    else:
                        out.append(f'<p>{html_escape(para)}</p>')
                out.append('</div>')
            elif kind == "ABBR_TITLE":
                out.append('<div class="section-divider">')
                for para in content.split("\n\n"):
                    para = para.strip()
                    if not para:
                        continue
                    if para.startswith("##"):
                        out.append(f'<h1>{html_escape(para.lstrip("# ").strip())}</h1>')
                    else:
                        out.append(f'<p>{html_escape(para)}</p>')
                out.append('</div>')
            elif kind == "ABBR_LIST":
                out.append('<table class="abbr-table"><thead><tr>'
                           '<th>المختصر</th><th>الدلالة</th></tr></thead><tbody>')
                for line in content.splitlines():
                    line = line.strip()
                    if not line or "|" not in line:
                        continue
                    left, _, right = line.partition("|")
                    out.append(f'<tr><td>{html_escape(left.strip())}</td>'
                               f'<td>{html_escape(right.strip())}</td></tr>')
                out.append('</tbody></table>')
            elif kind == "H1":
                out.append(f'<h1>{html_escape(content)}</h1>')
            elif kind == "H2":
                out.append(f'<h2>{html_escape(content)}</h2>')
            elif kind == "H3":
                out.append(f'<h3>{html_escape(content)}</h3>')
            elif kind == "H4":
                out.append(f'<h4>{html_escape(content)}</h4>')
            elif kind == "P":
                for para in re.split(r"\n\s*\n", content):
                    para = para.strip()
                    if para:
                        out.append(f'<p>{html_escape(para)}</p>')
            elif kind == "QUOTE":
                out.append('<blockquote>')
                for para in re.split(r"\n\s*\n", content):
                    para = para.strip()
                    if para:
                        out.append(f'<p>{html_escape(para)}</p>')
                out.append('</blockquote>')
            elif kind == "LIST":
                out.append('<ul>')
                for item in content.splitlines():
                    item = item.strip()
                    if item:
                        out.append(f'<li>{html_escape(item)}</li>')
                out.append('</ul>')
            elif kind == "REFLIST":
                out.append('<ol>')
                for item in content.splitlines():
                    item = item.strip()
                    if item:
                        out.append(f'<li>{html_escape(item)}</li>')
                out.append('</ol>')
            else:
                out.append(f'<p>{html_escape(content)}</p>')

    out.append(HTML_TEMPLATE_FOOT)
    return "\n".join(out)


# ===========================================================================
# Main
# ===========================================================================
def main():
    all_blocks = load_all_blocks()

    docx_path = os.path.join(BUILD, "حرية_الاستثمار_في_التشريع_الجزائري.docx")
    html_path = os.path.join(BUILD, "حرية_الاستثمار_في_التشريع_الجزائري.html")

    # ASCII-safe duplicates for tools that don't like Arabic filenames
    docx_ascii = os.path.join(BUILD, "thesis_liberte_investissement_DZ.docx")
    html_ascii = os.path.join(BUILD, "thesis_liberte_investissement_DZ.html")

    write_docx(docx_path, all_blocks)
    write_docx(docx_ascii, all_blocks)

    html = render_html(all_blocks)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    with open(html_ascii, "w", encoding="utf-8") as f:
        f.write(html)

    print("OK")
    print("DOCX:", docx_path)
    print("DOCX:", docx_ascii)
    print("HTML:", html_path)
    print("HTML:", html_ascii)


if __name__ == "__main__":
    main()
