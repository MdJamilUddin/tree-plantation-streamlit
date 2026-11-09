# streamlit_app.py
"""
বৃক্ষরোপণ তথ্য সংগ্রহ — মূল এন্ট্রি পয়েন্ট (Landing Page)
উপজেলা শিক্ষা অফিস, রাণীনগর, নওগাঁ
"""

import streamlit as st

# ============================================================
# পেজ কনফিগারেশন (সবার আগে থাকতে হবে)
# ============================================================
st.set_page_config(
    page_title="বৃক্ষরোপণ তথ্য সংগ্রহ",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "বৃক্ষরোপণ তথ্য সংগ্রহ অ্যাপ — উপজেলা শিক্ষা অফিস, রাণীনগর, নওগাঁ",
    },
)

# ============================================================
# ইমপোর্ট
# ============================================================
from ui_utils import inject_css, hero, metric_cards, section
from auth import is_admin, admin_badge, logout_button

# ============================================================
# স্টাইল ও সাইডবার
# ============================================================
inject_css()
admin_badge()
logout_button()

# সাইডবারে সংক্ষিপ্ত ব্র্যান্ডিং
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding:10px 0 16px;">
            <div style="font-size:2.4rem;">🌳</div>
            <div style="font-weight:700; color:#2e7d32; font-size:1.05rem;">
                বৃক্ষরোপণ তথ্য সংগ্রহ
            </div>
            <div style="font-size:0.8rem; color:#666; margin-top:4px;">
                রাণীনগর, নওগাঁ
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("📌 বাম মেনু থেকে পেজ বেছে নিন")
    st.markdown("---")
    if is_admin():
        st.success("👑 আপনি অ্যাডমিন হিসেবে লগইন করেছেন")
    else:
        st.info("ℹ️ সাধারণ ব্যবহারকারী মোড")

# ============================================================
# হিরো হেডার
# ============================================================
hero(
    "🌳 বৃক্ষরোপণ তথ্য সংগ্রহ",
    "উপজেলা শিক্ষা অফিস, রাণীনগর, নওগাঁ",
)

# ============================================================
# পরিসংখ্যান (ডেটাবেস থেকে)
# ============================================================
stats = None
db_error = None

try:
    from database import get_stats
    stats = get_stats()
except Exception as e:
    db_error = str(e)

if stats:
    metric_cards([
        ("📋 মোট বিদ্যালয়", f"{stats['total_schools']} / 100"),
        ("🥭 ফলদ চারা", stats["fruit"]),
        ("🌲 বনজ চারা", stats["timber"]),
        ("🌿 ঔষধি চারা", stats["medicinal"]),
    ])

    # অগ্রগতি বার
    progress = min(stats["total_schools"] / 100, 1.0)
    st.progress(
        progress,
        text=f"সংগ্রহের অগ্রগতি: {stats['total_schools']}/১০০ বিদ্যালয়",
    )
else:
    st.warning("⚠️ ডেটাবেস সংযোগ এখনো সেটআপ করা হয়নি বা ত্রুটি রয়েছে।")
    if db_error:
        with st.expander("🔧 ত্রুটির বিবরণ দেখুন"):
            st.code(db_error)
            st.markdown(
                """
                **সমাধান:**
                1. `.streamlit/secrets.toml`-এ Supabase URL/key ঠিক আছে কিনা দেখুন
                2. Supabase-এ `plantations` টেবিল ও `photos` bucket আছে কিনা যাচাই করুন
                3. Streamlit Cloud → Settings → Secrets আপডেট করুন
                """
            )

st.markdown("---")

# ============================================================
# দ্রুত নেভিগেশন
# ============================================================
st.markdown("### 🧭 শুরু করুন")

col1, col2, col3, col4 = st.columns(4, gap="medium")

with col1:
    if st.button("📝 তথ্য সংগ্রহ", use_container_width=True, type="primary"):
        st.switch_page("pages/1_📝_তথ্য_সংগ্রহ.py")

with col2:
    if st.button("📊 ড্যাশবোর্ড", use_container_width=True):
        st.switch_page("pages/2_📊_ড্যাশবোর্ড.py")

with col3:
    if st.button("📄 রিপোর্ট", use_container_width=True):
        st.switch_page("pages/4_📄_রিপোর্ট.py")

with col4:
    if st.button("🔐 অ্যাডমিন", use_container_width=True):
        st.switch_page("pages/5_🔐_Admin.py")

# ============================================================
# অ্যাডমিন লগইন অবস্থা অনুযায়ী নোট
# ============================================================
if not is_admin():
    st.info(
        "🔒 **ড্যাশবোর্ড, রিপোর্ট ও অ্যাডমিন প্যানেল** দেখতে অ্যাডমিন হিসেবে লগইন করুন। "
        "**তথ্য সংগ্রহ** পেজ সবার জন্য খোলা।"
    )
else:
    st.success(
        "✅ আপনি অ্যাডমিন মোডে আছেন। সব পেজে সম্পূর্ণ অ্যাক্সেস রয়েছে।"
    )

st.markdown("---")

# ============================================================
# নির্দেশিকা / হেল্প সেকশন
# ============================================================
st.markdown("### 📖 ব্যবহার নির্দেশিকা")

with st.expander("🆕 প্রথমবার ব্যবহারকারীর জন্য", expanded=False):
    st.markdown(
        """
        1. **📝 তথ্য সংগ্রহ** পেজে যান
        2. ড্রপডাউন থেকে আপনার বিদ্যালয় বেছে নিন
        3. সব প্রয়োজনীয় ফিল্ড পূরণ করুন (তারকা * চিহ্নিত)
        4. বৃক্ষরোপণের একটি ছবি আপলোড করুন
        5. **💾 সংরক্ষণ করুন** বাটনে ক্লিক করুন
        6. সফল হলে সবুজ বার্তা দেখবেন
        """
    )

with st.expander("✏️ আগের তথ্য সম্পাদনা", expanded=False):
    st.markdown(
        """
        1. **📝 তথ্য সংগ্রহ** পেজে যান
        2. আগে যেটি সংরক্ষণ করেছিলেন সেই বিদ্যালয় বেছে নিন
        3. সব ফিল্ডে আগের তথ্য লোড হয়ে যাবে
        4. যেটা পরিবর্তন করতে চান সেটা এডিট করুন
        5. আবার **💾 সংরক্ষণ করুন** ক্লিক করুন
        """
    )

with st.expander("📷 ছবি আপলোডের নিয়ম", expanded=False):
    st.markdown(
        """
        - **ফরম্যাট:** JPG, JPEG, PNG, WEBP
        - **সর্বোচ্চ সাইজ:** ১০ MB
        - ছবি স্বয়ংক্রিয়ভাবে রিসাইজ হবে (৮০০px প্রস্থ)
        - একটি বিদ্যালয়ের জন্য একটি ছবি (পুরনো ছবি থাকলে নতুন দিয়ে রিপ্লেস হবে)
        - ছবি তোলার সময় বৃক্ষ ও শিক্ষার্থী একসাথে থাকলে ভালো
        """
    )

with st.expander("🔐 অ্যাডমিন অ্যাক্সেস", expanded=False):
    st.markdown(
        """
        **অ্যাডমিন হিসেবে যা করতে পারবেন:**
        - 📊 সব বিদ্যালয়ের ডেটা দেখা ও ফিল্টার
        - ✏️ যেকোনো রেকর্ডের তথ্য সম্পাদনা
        - 🗑️ ভুল রেকর্ড ডিলিট
        - 📄 অফিসিয়াল ফরম্যাটে Word/Excel রিপোর্ট তৈরি
        - 💾 সম্পূর্ণ ব্যাকআপ ডাউনলোড

        **লগইন:** 🔐 অ্যাডমিন পেজে গিয়ে পাসওয়ার্ড দিন
        """
    )

st.markdown("---")

# ============================================================
# ফুটার
# ============================================================
import pandas as pd

st.markdown(
    f"""
    <div style="text-align:center; padding:24px 12px; color:#666;
                font-size:0.82rem; line-height:1.8;">
        <div style="font-size:1.5rem; margin-bottom:6px;">🌱</div>
        <div><strong>বৃক্ষরোপণ তথ্য সংগ্রহ অ্যাপ</strong></div>
        <div>উপজেলা শিক্ষা অফিস, রাণীনগর, নওগাঁ</div>
        <div style="margin-top:8px; opacity:0.75;">
            © {pd.Timestamp.now().year} • সর্বস্বত্ব সংরক্ষিত
        </div>
        <div style="margin-top:6px; font-size:0.75rem; opacity:0.6;">
            Streamlit • Supabase • Made with ❤️ for রাণীনগর
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)