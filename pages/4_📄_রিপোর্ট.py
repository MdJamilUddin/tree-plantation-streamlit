# pages/4_📄_রিপোর্ট.py
from auth import require_admin, admin_badge
require_admin()   # অ্যাডমিন ছাড়া ঢুকতে পারবে না
admin_badge()
import streamlit as st
import pandas as pd
from database import get_all_records
from report_generator import generate_docx_report, generate_excel_report

st.set_page_config(page_title="রিপোর্ট", page_icon="📄", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Sans Bengali', sans-serif !important; }
    .report-header {
        background: linear-gradient(135deg, #1F4E79, #2e7d32);
        color: white; padding: 24px; border-radius: 10px;
        text-align: center; margin-bottom: 20px;
    }
    .report-header h2 { margin: 0; font-size: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="report-header">
    <h2>📄 বৃক্ষরোপণ তথ্য রিপোর্ট</h2>
    <p style="margin: 6px 0 0; opacity: 0.9;">উপজেলা প্রাথমিক শিক্ষা অফিস, রাণীনগর, নওগাঁ</p>
</div>
""", unsafe_allow_html=True)

df = get_all_records()

if df.empty:
    st.warning("⚠️ এখনো কোনো তথ্য সংরক্ষিত হয়নি। প্রথমে **📝 তথ্য সংগ্রহ** পেজে যান।")
    st.stop()

# ---- ফিল্টার ----
with st.expander("🔎 ফিল্টার (ঐচ্ছিক)", expanded=False):
    c1, c2 = st.columns(2)
    union_filter = c1.multiselect(
        "ইউনিয়ন", sorted(df["union_name"].dropna().unique().tolist())
    )
    class_filter = c2.multiselect(
        "শ্রেণি", sorted(df["class_name"].dropna().unique().tolist())
    )

filtered = df.copy()
if union_filter:
    filtered = filtered[filtered["union_name"].isin(union_filter)]
if class_filter:
    filtered = filtered[filtered["class_name"].isin(class_filter)]

# ---- সারসংক্ষেপ মেট্রিক ----
st.subheader("📊 সারসংক্ষেপ")
c1, c2, c3, c4 = st.columns(4)
c1.metric("মোট বিদ্যালয়", f"{len(filtered)} / 100")
c2.metric("ফলদ চারা", int(filtered["fruit_count"].fillna(0).sum()))
c3.metric("বনজ চারা", int(filtered["timber_count"].fillna(0).sum()))
c4.metric("ঔষধি চারা", int(filtered["medicinal_count"].fillna(0).sum()))

st.divider()

# ---- পূর্বরূপ ----
st.subheader("👁️ রিপোর্টের পূর্বরূপ (টেবিল)")
preview_cols = {
    "school_index": "ক্রম",
    "school_name": "বিদ্যালয়",
    "union_name": "ইউনিয়ন",
    "fruit_count": "ফলদ",
    "timber_count": "বনজ",
    "medicinal_count": "ঔষধি",
    "student_name": "শিক্ষার্থী",
    "class_name": "শ্রেণি",
    "planting_date": "তারিখ",
}
show = filtered[[c for c in preview_cols if c in filtered.columns]].copy()
show = show.rename(columns=preview_cols)
if "ক্রম" in show.columns:
    show["ক্রম"] = show["ক্রম"] + 1

st.dataframe(show, use_container_width=True, hide_index=True)

st.divider()

# ---- ডাউনলোড অপশন ----
st.subheader("⬇️ ডাউনলোড")
c1, c2 = st.columns([2, 1])

with c1:
    include_photos = st.checkbox(
        "📷 Word রিপোর্টে ছবি অন্তর্ভুক্ত করুন",
        value=True,
        help="বন্ধ করলে রিপোর্ট দ্রুত তৈরি হবে (বড় ডেটাসেটে সুপারিশকৃত)"
    )
    officer_name = st.text_input("স্বাক্ষরকারীর নাম", value="মোঃ জোনাব আলী")

with c2:
    st.caption("Word ফাইল তৈরি করতে ক্লিক করুন")

# ---- Word ডাউনলোড ----
col_word, col_excel = st.columns(2)

with col_word:
    if st.button("📄 Word রিপোর্ট তৈরি করুন", type="primary", use_container_width=True):
        with st.spinner("Word রিপোর্ট তৈরি হচ্ছে... ছবি ডাউনলোডের কারণে কিছুটা সময় লাগতে পারে।"):
            try:
                docx_bytes = generate_docx_report(
                    filtered,
                    include_photos=include_photos,
                    officer_name=officer_name,
                )
                st.session_state["docx_bytes"] = docx_bytes.getvalue()
                st.success("✅ Word রিপোর্ট তৈরি সম্পন্ন!")
            except Exception as e:
                st.error(f"❌ ত্রুটি: {e}")

    if "docx_bytes" in st.session_state:
        st.download_button(
            "⬇️ Word (.docx) ডাউনলোড",
            data=st.session_state["docx_bytes"],
            file_name=f"বৃক্ষরোপণ_রিপোর্ট_{pd.Timestamp.now():%Y%m%d}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )

with col_excel:
    if st.button("📊 Excel রিপোর্ট তৈরি করুন", use_container_width=True):
        with st.spinner("Excel তৈরি হচ্ছে..."):
            try:
                xlsx_bytes = generate_excel_report(filtered)
                st.session_state["xlsx_bytes"] = xlsx_bytes.getvalue()
                st.success("✅ Excel রিপোর্ট তৈরি সম্পন্ন!")
            except Exception as e:
                st.error(f"❌ ত্রুটি: {e}")

    if "xlsx_bytes" in st.session_state:
        st.download_button(
            "⬇️ Excel (.xlsx) ডাউনলোড",
            data=st.session_state["xlsx_bytes"],
            file_name=f"বৃক্ষরোপণ_তথ্য_{pd.Timestamp.now():%Y%m%d}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

st.divider()

# ---- নোট ----
st.info("""
💡 **টিপস:**
- Word রিপোর্টে ছবি থাকলে কিছুটা সময় লাগবে (প্রতি ছবি ~২-৩ সেকেন্ড)
- দ্রুত রিপোর্ট চাইলে "ছবি অন্তর্ভুক্ত করুন" বন্ধ করুন
- Word রিপোর্টে বাংলা ফন্ট সঠিকভাবে দেখাতে **Nirmala UI** বা **Kalpurush** ইনস্টল থাকতে হবে
- রিপোর্টে সর্বোচ্চ ১০০টি বিদ্যালয়ের তথ্য থাকবে (যেগুলো সংরক্ষিত আছে)
""")