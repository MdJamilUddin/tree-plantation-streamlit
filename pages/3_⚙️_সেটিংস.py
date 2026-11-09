# pages/3_⚙️_সেটিংস.py
from auth import require_admin, admin_badge
require_admin()   # অ্যাডমিন ছাড়া ঢুকতে পারবে না
admin_badge()
import streamlit as st
from database import get_all_records, get_client

st.set_page_config(page_title="সেটিংস", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Sans Bengali', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

st.title("⚙️ সেটিংস ও ডায়াগনস্টিকস")

# ===== সংযোগ পরীক্ষা =====
st.subheader("🔌 ডেটাবেস সংযোগ")
try:
    client = get_client()
    df = get_all_records()
    st.success(f"✅ Supabase সংযোগ সক্রিয় — {len(df)} টি রেকর্ড পাওয়া গেছে")
except Exception as e:
    st.error(f"❌ সংযোগ ব্যর্থ: {e}")
    st.code("""
# .streamlit/secrets.toml
[supabase]
url = "https://YOUR-PROJECT.supabase.co"
key = "YOUR-ANON-KEY"
""")

# ===== ডেটা ব্যাকআপ =====
st.divider()
st.subheader("💾 সম্পূর্ণ ব্যাকআপ")
df = get_all_records()
if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 সব ডেটার CSV ব্যাকআপ",
        data=csv,
        file_name=f"backup_full_{pd.Timestamp.now():%Y%m%d_%H%M}.csv" if (pd := __import__("pandas")) else "backup.csv",
        mime="text/csv",
    )
    st.caption(f"মোট {len(df)} টি রেকর্ড ব্যাকআপ করা যাবে")
else:
    st.info("ব্যাকআপ করার মতো কোনো ডেটা নেই")

# ===== তথ্য =====
st.divider()
st.subheader("ℹ️ অ্যাপ তথ্য")
st.markdown("""
- **অ্যাপ সংস্করণ:** 1.0.0
- **ডেটাবেস:** Supabase PostgreSQL
- **ছবি স্টোরেজ:** Supabase Storage (bucket: `photos`)
- **হোস্টিং:** Streamlit Community Cloud
- **উপজেলা:** রাণীনগর, নওগাঁ
""")