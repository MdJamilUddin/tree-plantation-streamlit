# image_utils.py
"""
ছবি আপলোড, প্রিভিউ, ক্রপ, রিসাইজ — সব ইউটিলিটি
"""
from io import BytesIO
from PIL import Image
import streamlit as st
from streamlit_cropper import st_cropper


# ---------- কনফিগারেশন ----------
MAX_UPLOAD_MB = 10
MAX_DISPLAY_WIDTH = 400          # প্রিভিউর প্রস্থ (px)
CROP_TARGET_RATIO = None         # None = ফ্রি ক্রপ; (1,1)=স্কয়ার; (4,3)=৪:৩
OUTPUT_QUALITY = 80              # JPEG কোয়ালিটি (0-100)
OUTPUT_MAX_WIDTH = 1200          # আউটপুট সর্বোচ্চ প্রস্থ


def validate_image(uploaded_file) -> tuple[bool, str]:
    """ফাইল বৈধ কিনা যাচাই"""
    if uploaded_file is None:
        return False, "কোনো ফাইল আপলোড হয়নি"
    if not uploaded_file.type.startswith("image/"):
        return False, "শুধুমাত্র ছবি আপলোড করুন"
    size_mb = uploaded_file.size / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        return False, f"ছবির আকার {size_mb:.1f}MB — সর্বোচ্চ {MAX_UPLOAD_MB}MB অনুমোদিত"
    return True, ""


def show_original_preview(uploaded_file):
    """আপলোড করা আসল ছবির প্রিভিউ"""
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


def crop_image(uploaded_file, ratio=None, key_suffix=""):
    """
    ইউজারকে ব্রাউজারে ছবি ক্রপ করতে দেয়।
    Returns: PIL.Image (ক্রপ করা) অথবা None
    """
    img = Image.open(uploaded_file).convert("RGB")

    # বড় ছবি হলে ডিসপ্লে-সাইজ কমিয়ে দেখাই (দ্রুত লোড)
    if img.width > 1200:
        ratio_scale = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio_scale)))

    st.markdown("**✂️ ছবি ক্রপ করুন** (প্রয়োজনে অপ্রয়োজনীয় অংশ বাদ দিন)")

    cropped = st_cropper(
        img,
        realtime_update=True,
        box_color="#2e7d32",
        aspect_ratio=ratio,
        return_type="image",
        key=f"cropper_{key_suffix}",
    )

    # ক্রপ প্রিভিউ
    st.markdown("**✅ ক্রপ করা ছবি (এটিই সংরক্ষিত হবে)**")
    st.image(cropped, use_container_width=True)

    return cropped


def resize_for_upload(pil_img: Image.Image) -> BytesIO:
    """ক্রপ করা ছবি রিসাইজ + JPEG বাফার"""
    if pil_img.width > OUTPUT_MAX_WIDTH:
        scale = OUTPUT_MAX_WIDTH / pil_img.width
        pil_img = pil_img.resize(
            (OUTPUT_MAX_WIDTH, int(pil_img.height * scale)),
            Image.LANCZOS,
        )
    buf = BytesIO()
    pil_img.convert("RGB").save(buf, format="JPEG", quality=OUTPUT_QUALITY, optimize=True)
    buf.seek(0)
    return buf


def process_upload(uploaded_file, ratio=None, key_suffix=""):
    """
    সম্পূর্ণ প্রসেস: যাচাই → প্রিভিউ → ক্রপ → প্রিভিউ।
    Returns: (PIL.Image|None, str)  -- (ক্রপ করা ছবি, ত্রুটি বার্তা)
    """
    ok, err = validate_image(uploaded_file)
    if not ok:
        return None, err

    show_original_preview(uploaded_file)
    st.markdown("---")
    cropped = crop_image(uploaded_file, ratio=ratio, key_suffix=key_suffix)

    if cropped is None:
        return None, "ক্রপ করা যায়নি"

    return cropped, ""