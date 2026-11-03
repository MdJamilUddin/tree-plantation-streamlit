# pages/2_📊_ড্যাশবোর্ড.py
import streamlit as st
import pandas as pd
from database import get_all_records, delete_record
from schools import SCHOOLS

st.set_page_config(page_title="ড্যাশবোর্ড", page_icon="📊", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Sans Bengali', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 কেন্দ্রীয় ড্যাশবোর্ড")
st.caption("সব বিদ্যালয়ের তথ্য এক জায়গায় — ফিল্টার, সার্চ, এক্সপোর্ট ও সম্পাদনা।")

# ডেটা লোড
df = get_all_records()

if df.empty:
    st.warning("⚠️ এখনো কোনো তথ্য সংরক্ষিত হয়নি। প্রথমে **📝 তথ্য সংগ্রহ** পেজে যান।")
    st.stop()

# ===== পরিসংখ্যান =====
c1, c2, c3, c4 = st.columns(4)
c1.metric("📋 মোট বিদ্যালয়", f"{len(df)} / 100")
c2.metric("🥭 ফলদ চারা", int(df["fruit_count"].fillna(0).sum()))
c3.metric("🌲 বনজ চারা", int(df["timber_count"].fillna(0).sum()))
c4.metric("🌿 ঔষধি চারা", int(df["medicinal_count"].fillna(0).sum()))

st.progress(len(df) / 100, text=f"অগ্রগতি: {len(df)}/১০০ বিদ্যালয়")

st.divider()

# ===== ফিল্টার =====
st.subheader("🔍 ফিল্টার ও সার্চ")
c1, c2, c3 = st.columns(3)
search = c1.text_input("বিদ্যালয়ের নাম / শিক্ষার্থী দিয়ে খুঁজুন", "")
filter_union = c2.multiselect("ইউনিয়ন", sorted(df["union_name"].dropna().unique().tolist()))
filter_class = c3.multiselect("শ্রেণি", sorted(df["class_name"].dropna().unique().tolist()))

filtered = df.copy()
if search:
    mask = (
        filtered["school_name"].str.contains(search, case=False, na=False)
        | filtered["student_name"].str.contains(search, case=False, na=False)
    )
    filtered = filtered[mask]
if filter_union:
    filtered = filtered[filtered["union_name"].isin(filter_union)]
if filter_class:
    filtered = filtered[filtered["class_name"].isin(filter_class)]

st.caption(f"দেখানো হচ্ছে: **{len(filtered)}** টি রেকর্ড")

# ===== চার্ট =====
st.subheader("📈 ভিজ্যুয়ালাইজেশন")
c1, c2 = st.columns(2)

with c1:
    st.markdown("**ইউনিয়নভিত্তিক বিদ্যালয়**")
    union_counts = filtered["union_name"].fillna("অজানা").value_counts()
    if not union_counts.empty:
        st.bar_chart(union_counts)

with c2:
    st.markdown("**শ্রেণিভিত্তিক শিক্ষার্থী**")
    class_counts = filtered["class_name"].fillna("অজানা").value_counts()
    if not class_counts.empty:
        st.bar_chart(class_counts)

st.divider()

# ===== টেবিল =====
st.subheader("📋 সম্পূর্ণ তালিকা")

display_cols = {
    "school_index": "ক্রম",
    "school_name": "বিদ্যালয়",
    "union_name": "ইউনিয়ন",
    "fruit_count": "ফলদ",
    "timber_count": "বনজ",
    "ঔষধি_count_placeholder": "ঔষধি",  # নিচে ঠিক করা হবে
    "medicinal_count": "ঔষধি",
    "student_name": "শিক্ষার্থী",
    "class_name": "শ্রেণি",
    "planting_date": "তারিখ",
    "photo_url": "ছবি",
}
show_df = filtered[[c for c in display_cols if c in filtered.columns]].rename(columns=display_cols)
show_df["ক্রম"] = show_df["ক্রম"] + 1

st.dataframe(
    show_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "ছবি": st.column_config.ImageColumn("ছবি", width="small"),
    },
)

# ===== এক্সপোর্ট =====
st.subheader("⬇️ এক্সপোর্ট")
c1, c2 = st.columns(2)
with c1:
    csv = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📄 CSV ডাউনলোড",
        data=csv,
        file_name=f"বৃক্ষরোপণ_তথ্য_{pd.Timestamp.now():%Y%m%d}.csv",
        mime="text/csv",
        use_container_width=True,
    )
with c2:
    from io import BytesIO
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        filtered.to_excel(writer, index=False, sheet_name="তথ্য")
    st.download_button(
        "📊 Excel ডাউনলোড",
        data=buf.getvalue(),
        file_name=f"বৃক্ষরোপণ_তথ্য_{pd.Timestamp.now():%Y%m%d}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

st.divider()

# ===== বিস্তারিত দেখা ও মুছে ফেলা =====
with st.expander("🔎 একটি রেকর্ডের বিস্তারিত দেখুন"):
    if not filtered.empty:
        idx = st.selectbox(
            "বিদ্যালয় নির্বাচন করুন",
            filtered["school_index"].tolist(),
            format_func=lambda i: SCHOOLS[int(i)],
            key="detail_select",
        )
        row = filtered[filtered["school_index"] == idx].iloc[0]
        c1, c2 = st.columns([1, 2])
        with c1:
            if row.get("photo_url"):
                st.image(row["photo_url"], use_container_width=True)
        with c2:
            st.markdown(f"**বিদ্যালয়:** {row['school_name']}")
            st.markdown(f"**ইউনিয়ন/গ্রাম:** {row.get('union_name','—')} / {row.get('village','—')}")
            st.markdown(f"**শিক্ষার্থী:** {row['student_name']} (শ্রেণি {row['class_name']})")
            st.markdown(f"**পিতা-মাতা:** {row['father_name']} / {row['mother_name']}")
            st.markdown(f"**প্রধান:** {row['head_name']} — {row['head_mobile']}")
            st.markdown(f"**তারিখ:** {row.get('planting_date','—')}")
            st.markdown(f"**এলাকা:** {row.get('location','—')}")
            st.markdown(f"**মন্তব্য:** {row.get('remarks','—')}")

with st.expander("🗑️ রেকর্ড মুছে ফেলুন"):
    if not filtered.empty:
        del_idx = st.selectbox(
            "মুছে ফেলার জন্য বিদ্যালয়",
            filtered["school_index"].tolist(),
            format_func=lambda i: SCHOOLS[int(i)],
            key="delete_select",
        )
        st.warning(f"⚠️ {SCHOOLS[int(del_idx)]} এর তথ্য স্থায়ীভাবে মুছে যাবে")
        if st.button("নিশ্চিতভাবে মুছুন", type="primary"):
            if delete_record(int(del_idx)):
                st.success("✅ মুছে ফেলা হয়েছে")
                st.rerun()