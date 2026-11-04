# report_generator.py
"""
বৃক্ষরোপণ তথ্য থেকে Word (.docx) / Excel রিপোর্ট তৈরি
ফরম্যাট: শিক্ষার্থী কর্তৃক বাসস্থান বা অন্যত্র রোপনকৃত বৃক্ষের তথ্য.docx
"""
from io import BytesIO
from datetime import date
import requests
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---- বাংলা ফন্ট (Word-এ সঠিকভাবে দেখানোর জন্য) ----
BANGLA_FONT = "Nirmala UI"   # Windows-এ ডিফল্ট; না থাকলে "Kalpurush" বা "SolaimanLipi" দিন


def _set_cell_bangla(cell, text: str, bold: bool = False, size: int = 9,
                     align=WD_ALIGN_PARAGRAPH.CENTER):
    """সেলের ভেতরে বাংলা টেক্সট সেট করে"""
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    run = p.add_run(str(text) if text is not None else "")
    run.font.name = BANGLA_FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), BANGLA_FONT)
    run.font.size = Pt(size)
    run.font.bold = bold
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def _set_col_width(cell, width_cm: float):
    """কলামের প্রস্থ নির্ধারণ"""
    cell.width = Cm(width_cm)


def _add_page_number_footer(section):
    """ফুটারে পৃষ্ঠা নম্বর"""
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)


def _download_image(url: str) -> BytesIO | None:
    """ছবি URL থেকে ডাউনলোড (Supabase public URL)"""
    if not url or not url.startswith("http"):
        return None
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return BytesIO(r.content)
    except Exception:
        pass
    return None


def generate_docx_report(df: pd.DataFrame, include_photos: bool = True,
                          upazila_name: str = "রাণীনগর",
                          district_name: str = "নওগাঁ",
                          officer_name: str = "মোঃ জোনাব আলী") -> BytesIO:
    """
    সম্পূর্ণ রিপোর্ট .docx আকারে তৈরি করে BytesIO ফেরত দেয়।
    df-এ অবশ্যই থাকতে হবে: school_index, school_name, district, upazila,
    union_name, village, fruit_species, fruit_count, timber_species,
    timber_count, medicinal_species, medicinal_count, planting_date,
    location, student_name, father_name, mother_name, class_name,
    student_address, student_mobile, head_name, head_mobile, photo_url
    """
    doc = Document()

    # ---- পেজ সেটআপ: A4 ল্যান্ডস্কেপ ----
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    new_w, new_h = section.page_height, section.page_width
    section.page_width = new_w
    section.page_height = new_h
    section.top_margin = Cm(1.2)
    section.bottom_margin = Cm(1.2)
    section.left_margin = Cm(1.0)
    section.right_margin = Cm(1.0)

    _add_page_number_footer(section)

    # ---- হেডার: সরকারি শিরোনাম ----
    h1 = doc.add_paragraph()
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h1.add_run("গণপ্রজাতন্ত্রী বাংলাদেশ সরকার")
    r.font.name = BANGLA_FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), BANGLA_FONT)
    r.font.size = Pt(13)
    r.font.bold = True

    h2 = doc.add_paragraph()
    h2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h2.add_run("উপজেলা প্রাথমিক শিক্ষা অফিসারের কার্যালয়")
    r.font.name = BANGLA_FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), BANGLA_FONT)
    r.font.size = Pt(12)
    r.font.bold = True

    h3 = doc.add_paragraph()
    h3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = h3.add_run(f"{upazila_name}, {district_name}।")
    r.font.name = BANGLA_FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), BANGLA_FONT)
    r.font.size = Pt(12)
    r.font.bold = True

    # ---- রিপোর্ট শিরোনাম ----
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("শিক্ষার্থী কর্তৃক বাসস্থান বা অন্যত্র রোপনকৃত বৃক্ষের তথ্য")
    r.font.name = BANGLA_FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), BANGLA_FONT)
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    # ---- টেবিল (১০ কলাম) ----
    headers = [
        "ক্রমিক\nনং",
        "বিদ্যালয়ের\nনাম",
        "জেলা, উপজেলা,\nইউনিয়ন ও\nগ্রামের নাম",
        "রোপনকৃত\nবৃক্ষের\nপ্রজাতির নাম",
        "রোপনকৃত\nবৃক্ষের\nচারার সংখ্যা",
        "বৃক্ষরোপণের\nতারিখ",
        "বৃক্ষরোপণের\nসুনির্দিষ্ট এলাকা",
        "শিক্ষার্থীর নাম,\nপিতা-মাতার নাম,\nশ্রেণি, ঠিকানা,\nমোবাইল",
        "প্রধান শিক্ষকের\nনাম ও মোবাইল",
        "ছবি",
    ]
    # কলাম প্রস্থ (সেমি) — মোট ~25.7 cm (A4 ল্যান্ডস্কেপ মার্জিন বাদে)
    widths_cm = [1.2, 2.8, 3.0, 2.0, 1.8, 1.8, 2.2, 3.8, 2.8, 2.5]

    table = doc.add_table(rows=2, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # হেডার সেল
    for i, (h, w) in enumerate(zip(headers, widths_cm)):
        cell = table.cell(0, i)
        _set_cell_bangla(cell, h, bold=True, size=9)
        _set_col_width(cell, w)

    # দ্বিতীয় সারি: ১–১০ নম্বর
    for i in range(len(headers)):
        cell = table.cell(1, i)
        _set_cell_bangla(cell, str(i + 1), bold=True, size=8)

    # ---- ডেটা সারি ----
    for _, row in df.iterrows():
        cells = table.add_row().cells

        # ১. ক্রমিক
        _set_cell_bangla(cells[0], f"{int(row['school_index']) + 1:02d}")

        # ২. বিদ্যালয়ের নাম
        _set_cell_bangla(cells[1], row.get("school_name", ""), align=WD_ALIGN_PARAGRAPH.LEFT)

        # ৩. জেলা/উপজেলা/ইউনিয়ন/গ্রাম
        loc_parts = []
        if pd.notna(row.get("district")):
            loc_parts.append(f"জেলা: {row['district']}")
        if pd.notna(row.get("upazila")):
            loc_parts.append(f"উপজেলা: {row['upazila']}")
        if pd.notna(row.get("union_name")):
            loc_parts.append(f"ইউনিয়ন: {row['union_name']}")
        if pd.notna(row.get("village")):
            loc_parts.append(f"গ্রাম: {row['village']}")
        _set_cell_bangla(cells[2], "\n".join(loc_parts), align=WD_ALIGN_PARAGRAPH.LEFT)

        # ৪. প্রজাতি
        species_parts = []
        if pd.notna(row.get("fruit_species")) and row["fruit_species"]:
            species_parts.append(f"ফলদ: {row['fruit_species']}")
        if pd.notna(row.get("timber_species")) and row["timber_species"]:
            species_parts.append(f"বনজ: {row['timber_species']}")
        if pd.notna(row.get("medicinal_species")) and row["medicinal_species"]:
            species_parts.append(f"ঔষধি: {row['medicinal_species']}")
        _set_cell_bangla(cells[3], "\n".join(species_parts) or "—",
                         align=WD_ALIGN_PARAGRAPH.LEFT)

        # ৫. সংখ্যা
        count_parts = [
            f"ফলদ- {int(row.get('fruit_count') or 0)} টি",
            f"বনজ- {int(row.get('timber_count') or 0)} টি",
            f"ঔষধি- {int(row.get('medicinal_count') or 0)} টি",
        ]
        _set_cell_bangla(cells[4], "\n".join(count_parts), align=WD_ALIGN_PARAGRAPH.LEFT)

        # ৬. তারিখ
        d = row.get("planting_date")
        date_str = ""
        if pd.notna(d) and d:
            try:
                date_str = pd.to_datetime(d).strftime("%d/%m/%Y")
            except Exception:
                date_str = str(d)
        _set_cell_bangla(cells[5], date_str or "—")

        # ৭. এলাকা
        _set_cell_bangla(cells[6], row.get("location") or "—",
                         align=WD_ALIGN_PARAGRAPH.LEFT)

        # ৮. শিক্ষার্থী তথ্য
        student_parts = [
            f"নাম: {row.get('student_name') or '—'}",
            f"পিতা: {row.get('father_name') or '—'}",
            f"মাতা: {row.get('mother_name') or '—'}",
            f"শ্রেণি: {row.get('class_name') or '—'}",
            f"ঠিকানা: {row.get('student_address') or '—'}",
            f"মোবাইল: {row.get('student_mobile') or '—'}",
        ]
        _set_cell_bangla(cells[7], "\n".join(student_parts),
                         align=WD_ALIGN_PARAGRAPH.LEFT)

        # ৯. প্রধান শিক্ষক
        head_parts = [
            f"নাম: {row.get('head_name') or '—'}",
            f"মোবাইল: {row.get('head_mobile') or '—'}",
        ]
        _set_cell_bangla(cells[8], "\n".join(head_parts),
                         align=WD_ALIGN_PARAGRAPH.LEFT)

        # ১০. ছবি
        cells[9].text = ""
        p = cells[9].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if include_photos and row.get("photo_url"):
            img_bytes = _download_image(row["photo_url"])
            if img_bytes:
                try:
                    run = p.add_run()
                    run.add_picture(img_bytes, width=Cm(2.2))
                except Exception:
                    r = p.add_run("ছবি লোড হয়নি")
                    r.font.name = BANGLA_FONT
                    r.font.size = Pt(8)
            else:
                r = p.add_run("—")
                r.font.name = BANGLA_FONT
                r.font.size = Pt(8)
        else:
            r = p.add_run("—")
            r.font.name = BANGLA_FONT
            r.font.size = Pt(8)

    # ---- উপজেলার মোট ----
    doc.add_paragraph()  # ফাঁকা লাইন
    totals_para = doc.add_paragraph()
    totals_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    total_fruit = int(df.get("fruit_count", pd.Series(dtype=int)).fillna(0).sum())
    total_timber = int(df.get("timber_count", pd.Series(dtype=int)).fillna(0).sum())
    total_medicinal = int(df.get("medicinal_count", pd.Series(dtype=int)).fillna(0).sum())

    r = totals_para.add_run(
        f"উপজেলার মোট:  ফলদ- {total_fruit} টি  |  "
        f"বনজ- {total_timber} টি  |  "
        f"ঔষধি- {total_medicinal} টি  |  "
        f"মোট বিদ্যালয়- {len(df)} টি"
    )
    r.font.name = BANGLA_FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), BANGLA_FONT)
    r.font.size = Pt(10)
    r.font.bold = True

    # ---- স্বাক্ষর ব্লক ----
    doc.add_paragraph()
    sign = doc.add_paragraph()
    sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    sign_lines = [
        f"মোঃ {officer_name}" if not officer_name.startswith("মোঃ") else officer_name,
        "উপজেলা প্রাথমিক শিক্ষা অফিসার",
        f"{upazila_name}, {district_name}।",
    ]
    for i, line in enumerate(sign_lines):
        r = sign.add_run(line + ("\n" if i < len(sign_lines) - 1 else ""))
        r.font.name = BANGLA_FONT
        r._element.rPr.rFonts.set(qn("w:eastAsia"), BANGLA_FONT)
        r.font.size = Pt(10)
        r.font.bold = (i == 0)

    # ---- ফুটার নোট ----
    note = doc.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = note.add_run(
        f"রিপোর্ট তৈরি: {date.today().strftime('%d/%m/%Y')}  |  "
        f"মোট রেকর্ড: {len(df)}"
    )
    r.font.name = BANGLA_FONT
    r._element.rPr.rFonts.set(qn("w:eastAsia"), BANGLA_FONT)
    r.font.size = Pt(8)
    r.font.italic = True
    r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # ---- BytesIO-তে সেভ ----
    out = BytesIO()
    doc.save(out)
    out.seek(0)
    return out


def generate_excel_report(df: pd.DataFrame) -> BytesIO:
    """Excel রিপোর্ট (সহজ ভিউ ও ফিল্টারের জন্য)"""
    export_df = df.copy()
    export_df["ক্রম"] = export_df["school_index"] + 1
    export_df = export_df.rename(columns={
        "school_name": "বিদ্যালয়ের নাম",
        "district": "জেলা",
        "upazila": "উপজেলা",
        "union_name": "ইউনিয়ন",
        "village": "গ্রাম",
        "fruit_species": "ফলদ প্রজাতি",
        "fruit_count": "ফলদ সংখ্যা",
        "timber_species": "বনজ প্রজাতি",
        "timber_count": "বনজ সংখ্যা",
        "medicinal_species": "ঔষধি প্রজাতি",
        "medicinal_count": "ঔষধি সংখ্যা",
        "planting_date": "তারিখ",
        "location": "এলাকা",
        "student_name": "শিক্ষার্থী",
        "father_name": "পিতা",
        "mother_name": "মাতা",
        "class_name": "শ্রেণি",
        "student_address": "ঠিকানা",
        "student_mobile": "শিক্ষার্থী মোবাইল",
        "head_name": "প্রধান",
        "head_mobile": "প্রধান মোবাইল",
        "remarks": "মন্তব্য",
    })
    cols = ["ক্রম", "বিদ্যালয়ের নাম", "জেলা", "উপজেলা", "ইউনিয়ন", "গ্রাম",
            "ফলদ প্রজাতি", "ফলদ সংখ্যা", "বনজ প্রজাতি", "বনজ সংখ্যা",
            "ঔষধি প্রজাতি", "ঔষধি সংখ্যা", "তারিখ", "এলাকা",
            "শিক্ষার্থী", "পিতা", "মাতা", "শ্রেণি", "ঠিকানা",
            "শিক্ষার্থী মোবাইল", "প্রধান", "প্রধান মোবাইল", "মন্তব্য"]
    cols = [c for c in cols if c in export_df.columns]

    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        export_df[cols].to_excel(writer, index=False, sheet_name="বৃক্ষ তথ্য")

        # সারসংক্ষেপ শিট
        summary = pd.DataFrame({
            "বিভাগ": ["ফলদ", "বনজ", "ঔষধি", "মোট বিদ্যালয়"],
            "মোট": [
                int(df.get("fruit_count", pd.Series()).fillna(0).sum()),
                int(df.get("timber_count", pd.Series()).fillna(0).sum()),
                int(df.get("medicinal_count", pd.Series()).fillna(0).sum()),
                len(df),
            ],
        })
        summary.to_excel(writer, index=False, sheet_name="সারসংক্ষেপ")

    out.seek(0)
    return out