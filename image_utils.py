# image_utils.py
"""
ছবি আপলোড ও প্রিভিউ — সব ইউটিলিটি
"""

from PIL import Image
import streamlit as st

# ============================================================
# কনফিগারেশন
# ============================================================
MAX_UPLOAD_MB = 10


# ============================================================
# ভ্যালিডেশন
# ============================================================
def validate_image(uploaded_file) -> tuple[bool, str]:
    if uploaded_file is None:
        return False, "কোনো ফাইল আপলোড হয়নি"
    if not uploaded_file.type.startswith("image/"):
        return False, "শুধুমাত্র ছবি আপলোড করুন"
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        return False, f"ছবির আকার {size_mb:.1f}MB — সর্বোচ্চ {MAX_UPLOAD_MB}MB অনুমোদিত"
    return True, ""


# ============================================================
# মূল ছবির প্রিভিউ
# ============================================================
def show_original_preview(uploaded_file):
    img = Image.open(uploaded_file)
    st.markdown("**📷 মূল ছবি**")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(img, use_container_width=True)
    with c2:
        w, h = img.size
        size_mb = uploaded_file.size / (1024 * 1024)
        st.markdown(f"""
        - **মাপ:** {w} × {h} px
        - **ফাইল সাইজ:** {size_mb:.2f} MB
        - **ফরম্যাট:** {img.format or 'JPEG'}
        """)


# ============================================================
# সম্পূর্ণ প্রসেস (ক্রপ ও রিসাইজ ছাড়া)
# ============================================================
def process_upload(uploaded_file):
    ok, err = validate_image(uploaded_file)
    if not ok:
        return None, err

    show_original_preview(uploaded_file)
    st.markdown("---")

    img = Image.open(uploaded_file).convert("RGB")
    return img, ""
