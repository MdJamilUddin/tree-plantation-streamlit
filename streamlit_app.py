# streamlit_app.py
import streamlit as st

st.set_page_config(
    page_title="বৃক্ষরোপণ তথ্য সংগ্রহ",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# বাংলা ফন্ট
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Noto Sans Bengali', sans-serif !important;
    }
    .main-title {
        background: linear-gradient(135deg, #2e7d32, #4caf50);
        color: white;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 20px;
    }
    .main-title h1 { margin: 0; font-size: 2.2rem; }
    .main-title p { margin: 8px 0 0; opacity: 0.95; }
    .metric-card {
        background: #f1f8e9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        text-align: center;
    }
    .metric-card h3 { color: #2e7d32; margin: 0; font-size: 1rem; }
    .metric-card h1 { color: #1b5e20; margin: 8px 0 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-title">
    <h1>🌳 বৃক্ষরোপণ তথ্য সংগ্রহ</h1>
    <p>উপজেলা শিক্ষা অফিস, রাণীনগর, নওগাঁ</p>
</div>
""", unsafe_allow_html=True)

# দ্রুত পরিসংখ্যান
try:
    from database import get_stats
    stats = get_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>📋 মোট বিদ্যালয়</h3><h1>{stats["total_schools"]} / ১০০</h1></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>🥭 ফলদ চারা</h3><h1>{stats["fruit"]}</h1></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h3>🌲 বনজ চারা</h3><h1>{stats["timber"]}</h1></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><h3>🌿 ঔষধি চারা</h3><h1>{stats["medicinal"]}</h1></div>', unsafe_allow_html=True)

    st.progress(min(stats["total_schools"] / 100, 1.0),
                text=f"সংগ্রহের অগ্রগতি: {stats['total_schools']}/১০০ বিদ্যালয়")
except Exception as e:
    st.warning("⚠️ ডেটাবেস সংযোগ এখনো সেটআপ করা হয়নি। `.streamlit/secrets.toml` দেখুন।")
    st.code(str(e))

st.markdown("---")
st.markdown("""
### 🧭 ব্যবহার নির্দেশিকা

- **📝 তথ্য সংগ্রহ** — বাম সাইডবার থেকে বিদ্যালয় নির্বাচন করে নতুন তথ্য যোগ করুন বা সম্পাদনা করুন
- **📊 ড্যাশবোর্ড** — সব বিদ্যালয়ের তথ্য, ফিল্টার, চার্ট ও CSV/Excel এক্সপোর্ট
- **⚙️ সেটিংস** — ডেটাবেস সংযোগ, ব্যাকআপ ও রিসেট
""")

st.info("💡 বাম সাইডবার থেকে পেজ নির্বাচন করুন")