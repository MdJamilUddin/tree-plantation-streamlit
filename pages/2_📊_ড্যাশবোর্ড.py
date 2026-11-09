# pages/2_📊_ড্যাশবোর্ড.py
from auth import require_admin, admin_badge
require_admin()   # অ্যাডমিন ছাড়া ঢুকতে পারবে না
admin_badge()
import streamlit as st
import pandas as pd
from database import get_all_records, delete_record
from schools import SCHOOLS
from ui_utils import inject_css, hero, metric_cards, section

st.set_page_config(page_title="ড্যাশবোর্ড", page_icon="📊", layout="wide",
                   initial_sidebar_state="collapsed")
inject_css()
hero("📊 কেন্দ্রীয় ড্যাশবোর্ড", "সব বিদ্যালয়ের তথ্য এক জায়গায়")

df = get_all_records()
if df.empty:
    st.warning("⚠️ এখনো কোনো তথ্য নেই। আগে 📝 তথ্য সংগ্রহ পেজে যান।")
    st.stop()

metric_cards([
    ("📋 মোট বিদ্যালয়", f"{len(df)} / 100"),
    ("🥭 ফলদ", int(df["fruit_count"].fillna(0).sum())),
    ("🌲 বনজ", int(df["timber_count"].fillna(0).sum())),
    ("🌿 ঔষধি", int(df["medicinal_count"].fillna(0).sum())),
])
st.progress(len(df) / 100, text=f"অগ্রগতি: {len(df)}/১০০")

# ---- Filter (collapsed on mobile) ----
with st.expander("🔍 ফিল্টার ও সার্চ", expanded=False):
    search = st.text_input("বিদ্যালয় / শিক্ষার্থী", "")
    c1, c2 = st.columns(2)
    f_union = c1.multiselect("ইউনিয়ন", sorted(df["union_name"].dropna().unique().tolist()))
    f_class = c2.multiselect("শ্রেণি", sorted(df["class_name"].dropna().unique().tolist()))

filtered = df.copy()
if search:
    filtered = filtered[
        filtered["school_name"].str.contains(search, case=False, na=False) |
        filtered["student_name"].str.contains(search, case=False, na=False)
    ]
if f_union: filtered = filtered[filtered["union_name"].isin(f_union)]
if f_class: filtered = filtered[filtered["class_name"].isin(f_class)]

st.caption(f"দেখানো হচ্ছে **{len(filtered)}** টি রেকর্ড")

# ---- Tabs for mobile ----
tab1, tab2, tab3, tab4 = st.tabs(["📋 তালিকা", "📈 চার্ট", "⬇️ এক্সপোর্ট", "🔎 বিস্তারিত"])

with tab1:
    cols = {"school_index":"ক্রম", "school_name":"বিদ্যালয়", "union_name":"ইউনিয়ন",
            "fruit_count":"ফলদ", "timber_count":"বনজ", "medicinal_count":"ঔষধি",
            "student_name":"শিক্ষার্থী", "class_name":"শ্রেণি", "photo_url":"ছবি"}
    show = filtered[[c for c in cols if c in filtered.columns]].rename(columns=cols)
    if "ক্রম" in show.columns: show["ক্রম"] = show["ক্রম"] + 1
    st.dataframe(
        show, use_container_width=True, hide_index=True,
        column_config={"ছবি": st.column_config.ImageColumn("ছবি", width="small")},
    )

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**ইউনিয়নভিত্তিক**")
        uc = filtered["union_name"].fillna("—").value_counts()
        if not uc.empty: st.bar_chart(uc)
    with c2:
        st.markdown("**শ্রেণিভিত্তিক**")
        cc = filtered["class_name"].fillna("—").value_counts()
        if not cc.empty: st.bar_chart(cc)

with tab3:
    csv = filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📄 CSV ডাউনলোড", csv,
                       file_name=f"data_{pd.Timestamp.now():%Y%m%d}.csv",
                       mime="text/csv", use_container_width=True)
    from io import BytesIO
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        filtered.to_excel(w, index=False, sheet_name="তথ্য")
    st.download_button("📊 Excel ডাউনলোড", buf.getvalue(),
                       file_name=f"data_{pd.Timestamp.now():%Y%m%d}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

with tab4:
    if not filtered.empty:
        idx = st.selectbox("বিদ্যালয়", filtered["school_index"].tolist(),
                           format_func=lambda i: SCHOOLS[int(i)], key="det")
        row = filtered[filtered["school_index"] == idx].iloc[0]
        if row.get("photo_url"):
            st.image(row["photo_url"], use_container_width=True)
        with st.container():
            st.markdown(f"**🏫 {row['school_name']}**")
            st.markdown(f"**শিক্ষার্থী:** {row['student_name']} • শ্রেণি {row['class_name']}")
            st.markdown(f"**পিতা-মাতা:** {row['father_name']} / {row['mother_name']}")
            st.markdown(f"**প্রধান:** {row['head_name']} — {row['head_mobile']}")
            st.markdown(f"**তারিখ:** {row.get('planting_date','—')}")