# pages/5_🔐_Admin.py
import streamlit as st
import pandas as pd
from io import BytesIO
from database import get_all_records, delete_record, get_record_by_school
from schools import SCHOOLS
from auth import require_admin, logout_button, admin_badge
from ui_utils import inject_css, hero, metric_cards, section

st.set_page_config(page_title="Admin", page_icon="🔐", layout="wide",
                   initial_sidebar_state="collapsed")
inject_css()

# ---- গেট: অ্যাডমিন না হলে লগইন ফর্ম ----
require_admin()

hero("🔐 অ্যাডমিন প্যানেল", "সম্পূর্ণ নিয়ন্ত্রণ ও ব্যবস্থাপনা")
admin_badge()
logout_button()

df = get_all_records()

# ---- মেট্রিক ----
if not df.empty:
    metric_cards([
        ("📋 মোট বিদ্যালয়", f"{len(df)} / 100"),
        ("🥭 ফলদ", int(df["fruit_count"].fillna(0).sum())),
        ("🌲 বনজ", int(df["timber_count"].fillna(0).sum())),
        ("🌿 ঔষধি", int(df["medicinal_count"].fillna(0).sum())),
    ])
else:
    st.info("এখনো কোনো ডেটা নেই")

# ---- Tab নেভিগেশন ----
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 সব ডেটা", "✏️ সম্পাদনা", "🗑️ ডিলিট", "⬇️ ব্যাকআপ", "⚙️ সিস্টেম"
])

# ============ TAB 1: সব ডেটা ============
with tab1:
    if df.empty:
        st.warning("কোনো ডেটা নেই")
    else:
        search = st.text_input("🔍 সার্চ (বিদ্যালয় / শিক্ষার্থী)", "")
        view = df.copy()
        if search:
            view = view[
                view["school_name"].str.contains(search, case=False, na=False) |
                view["student_name"].str.contains(search, case=False, na=False)
            ]
        st.caption(f"মোট: **{len(view)}** টি")

        display = view[[
            "school_index", "school_name", "union_name",
            "fruit_count", "timber_count", "medicinal_count",
            "student_name", "class_name", "photo_url",
        ]].copy()
        display["school_index"] = display["school_index"] + 1
        display = display.rename(columns={
            "school_index":"ক্রম", "school_name":"বিদ্যালয়",
            "union_name":"ইউনিয়ন", "fruit_count":"ফলদ",
            "timber_count":"বনজ", "medicinal_count":"ঔষধি",
            "student_name":"শিক্ষার্থী", "class_name":"শ্রেণি",
            "photo_url":"ছবি",
        })
        st.dataframe(
            display, use_container_width=True, hide_index=True,
            column_config={"ছবি": st.column_config.ImageColumn("ছবি", width="small")},
        )

# ============ TAB 2: সম্পাদনা ============
with tab2:
    st.markdown("#### ✏️ রেকর্ড সম্পাদনা")
    st.caption("সম্পূর্ণ তথ্য সম্পাদনা করতে **📝 তথ্য সংগ্রহ** পেজে যান")

    if not df.empty:
        # কুইক-এডিট: শুধু সংখ্যা ও মন্তব্য
        idx = st.selectbox(
            "বিদ্যালয় নির্বাচন করুন",
            df["school_index"].tolist(),
            format_func=lambda i: SCHOOLS[int(i)],
            key="edit_select",
        )
        row = df[df["school_index"] == idx].iloc[0]

        with st.form(f"quick_edit_{idx}"):
            section("🌱 চারার সংখ্যা")
            c1, c2, c3 = st.columns(3)
            f = c1.number_input("ফলদ", 0, value=int(row.get("fruit_count") or 0))
            t = c2.number_input("বনজ", 0, value=int(row.get("timber_count") or 0))
            m = c3.number_input("ঔষধি", 0, value=int(row.get("medicinal_count") or 0))

            section("📝 মন্তব্য")
            remarks = st.text_area("মন্তব্য", value=row.get("remarks") or "")

            if st.form_submit_button("💾 আপডেট করুন", type="primary", use_container_width=True):
                from database import get_client
                from datetime import datetime
                try:
                    client = get_client()
                    client.table("plantations").update({
                        "fruit_count": f,
                        "timber_count": t,
                        "medicinal_count": m,
                        "remarks": remarks.strip(),
                        "updated_at": datetime.now().isoformat(),
                    }).eq("school_index", int(idx)).execute()
                    st.success("✅ আপডেট সম্পন্ন")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

# ============ TAB 3: ডিলিট ============
with tab3:
    st.markdown("#### 🗑️ রেকর্ড ডিলিট")
    st.warning("⚠️ ডিলিট করা ডেটা ফেরত আনা যাবে না")

    if not df.empty:
        idx = st.selectbox(
            "মুছে ফেলার জন্য বিদ্যালয়",
            df["school_index"].tolist(),
            format_func=lambda i: SCHOOLS[int(i)],
            key="delete_select",
        )
        row = df[df["school_index"] == idx].iloc[0]

        st.markdown(f"**বিদ্যালয়:** {row['school_name']}")
        st.markdown(f"**শিক্ষার্থী:** {row['student_name']} • শ্রেণি {row['class_name']}")

        confirm = st.text_input(
            "নিশ্চিত করতে `DELETE` লিখুন",
            placeholder="DELETE",
            key="delete_confirm",
        )
        if st.button("🗑️ স্থায়ীভাবে মুছে ফেলুন", type="primary", use_container_width=True):
            if confirm.strip().upper() == "DELETE":
                if delete_record(int(idx)):
                    st.success("✅ মুছে ফেলা হয়েছে")
                    st.rerun()
            else:
                st.error("❌ `DELETE` টাইপ করুন")

# ============ TAB 4: ব্যাকআপ ============
with tab4:
    st.markdown("#### ⬇️ সম্পূর্ণ ব্যাকআপ")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📄 CSV",
                csv,
                file_name=f"backup_{pd.Timestamp.now():%Y%m%d_%H%M}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with c2:
            buf = BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                df.to_excel(w, index=False, sheet_name="সম্পূর্ণ তথ্য")
            st.download_button(
                "📊 Excel",
                buf.getvalue(),
                file_name=f"backup_{pd.Timestamp.now():%Y%m%d_%H%M}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        st.markdown("---")
        st.markdown("**📊 পরিসংখ্যান**")
        c1, c2, c3 = st.columns(3)
        c1.metric("মোট বিদ্যালয়", f"{len(df)}/100")
        c2.metric("সম্পূর্ণ তথ্য", f"{(df['student_name'].notna()).sum()}")
        c3.metric("ছবি আপলোড", f"{df['photo_url'].notna().sum() if 'photo_url' in df else 0}")
    else:
        st.info("ব্যাকআপের জন্য ডেটা নেই")

# ============ TAB 5: সিস্টেম ============
with tab5:
    st.markdown("#### ⚙️ সিস্টেম সেটিংস")

    section("🔌 সংযোগ পরীক্ষা")
    try:
        from database import get_client
        get_client()
        st.success("✅ Supabase সংযোগ সক্রিয়")
    except Exception as e:
        st.error(f"❌ সংযোগ ব্যর্থ: {e}")

    st.markdown("---")
    section("🚨 বিপজ্জনক অপারেশন")
    st.caption("শুধু জরুরি অবস্থায় ব্যবহার করুন")

    with st.expander("🗑️ সব ডেটা মুছে ফেলুন"):
        st.warning("এই অপারেশন সব রেকর্ড মুছে ফেলবে! ফেরত আনা যাবে না।")
        confirm_all = st.text_input("নিশ্চিত করতে `RESET ALL` লিখুন", key="reset_confirm")
        if st.button("সব মুছুন", type="primary"):
            if confirm_all.strip().upper() == "RESET ALL":
                from database import get_client
                try:
                    client = get_client()
                    # সব row delete
                    for school_idx in df["school_index"].tolist():
                        client.table("plantations").delete().eq("school_index", int(school_idx)).execute()
                    st.success("✅ সব ডেটা মুছে ফেলা হয়েছে")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")
            else:
                st.error("❌ `RESET ALL` টাইপ করুন")

    st.markdown("---")
    section("ℹ️ সিস্টেম তথ্য")
    st.markdown(f"""
    - **অ্যাপ সংস্করণ:** 2.0.0
    - **ডেটাবেস:** Supabase PostgreSQL
    - **সঞ্চয়স্থান:** Supabase Storage (`photos` bucket)
    - **বর্তমান সময়:** {pd.Timestamp.now():%Y-%m-%d %H:%M:%S}
    - **মোট রেকর্ড:** {len(df)}
    """)
