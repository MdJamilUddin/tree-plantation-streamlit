# image_utils.py
"""
ছবি আপলোড, প্রিভিউ, ক্রপ, রিসাইজ — সব ইউটিলিটি
"""

from io import BytesIO
from PIL import Image
import streamlit as st
from streamlit_cropper import st_cropper
import streamlit.components.v1 as components

# ============================================================
# কনফিগারেশন
# ============================================================
MAX_UPLOAD_MB = 10
OUTPUT_QUALITY = 80
OUTPUT_MAX_WIDTH = 1200


# ============================================================
# কাস্টম CSS/JS: Drag Handle হলুদ, Box লাল
# ============================================================
def inject_cropper_styles():
    """iframe-এর ভেতরে Cropper-এর ড্র্যাগ হ্যান্ডেল ও বর্ডার কাস্টমাইজ"""
    js = """
    <script>
    // Cropper iframe-টি লোড হওয়া পর্যন্ত অপেক্ষা করুন
    function styleCropper() {
        const iframes = document.querySelectorAll('iframe');
        iframes.forEach(iframe => {
            try {
                const doc = iframe.contentDocument || iframe.contentWindow.document;
                if (!doc) return;
                // Cropper-এর CSS যোগ করা
                const style = doc.createElement('style');
                style.textContent = `
                    /* ক্রপ বর্ডার লাল */
                    .reactEasyCrop_CropArea, 
                    .reactEasyCrop_CropAreaRound {
                        border: 2px solid #FF0000 !important;
                        box-shadow: 0 0 0 1px #FF0000 !important;
                    }
                    /* ড্র্যাগ হ্যান্ডেল হলুদ */
                    .reactEasyCrop_CropArea::before,
                    .reactEasyCrop_CropArea::after,
                    .reactEasyCrop_CropArea > div {
                        background-color: #FFD700 !important;
                        border-color: #FFD700 !important;
                        border-radius: 50% !important;
                    }
                    /* কর্নার হ্যান্ডেল */
                    .reactEasyCrop_CropArea > div::before,
                    .reactEasyCrop_CropArea > div::after {
                        background-color: #FFD700 !important;
                        border-color: #FFD700 !important;
                    }
                `;
                doc.head.appendChild(style);
            } catch (e) {
                // Cross-origin iframe হলে এটি কাজ করবে না, তবে streamlit-এ সাধারণত কাজ করে
                console.log("Cropper style inject failed", e);
            }
        });
    }
    // প্রতি ১ সেকেন্ডে চেক করুন (Cropper লোড হতে দেরি হলে)
    setTimeout(styleCropper, 500);
    setInterval(styleCropper, 1000);
    </script>
    """
    components.html(js, height=0)


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
# ক্রপিং
# ============================================================
def crop_image(uploaded_file, ratio=None, key_suffix=""):
    img = Image.open(uploaded_file).convert("RGB")

    if img.width > 1200:
        ratio_scale = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio_scale)))

    st.markdown("**✂️ ছবি ক্রপ করুন** (প্রয়োজনে অপ্রয়োজনীয় অংশ বাদ দিন)")

    # 🔴 বক্সের রঙ লাল সেট করা হচ্ছে 🔴
    cropped = st_cropper(
        img,
        realtime_update=True,
        box_color="#FF0000",  # বর্ডার লাল
        aspect_ratio=ratio,
        return_type="image",
        key=f"cropper_{key_suffix}",
    )

    # Cropper-এর ওপর কাস্টম স্টাইল প্রয়োগ (হ্যান্ডেল হলুদ)
    inject_cropper_styles()

    st.markdown("**✅ ক্রপ করা ছবি (এটিই সংরক্ষিত হবে)**")
    st.image(cropped, use_container_width=True)

    return cropped


# ============================================================
# রিসাইজ ও বাফার
# ============================================================
def resize_for_upload(pil_img: Image.Image) -> BytesIO:
    if pil_img.width > OUTPUT_MAX_WIDTH:
        scale = OUTPUT_MAX_WIDTH / pil_img.width
        pil_img = pil_img.resize(
            (OUTPUT_MAX_WIDTH, int(pil_img.height * scale)),
            Image.LANCZOS,
        )
    buf = BytesIO()
    pil_img.convert("RGB").save(
        buf, format="JPEG", quality=OUTPUT_QUALITY, optimize=True
    )
    buf.seek(0)
    return buf


# ============================================================
# সম্পূর্ণ প্রসেস
# ============================================================
def process_upload(uploaded_file, ratio=None, key_suffix=""):
    ok, err = validate_image(uploaded_file)
    if not ok:
        return None, err

    show_original_preview(uploaded_file)
    st.markdown("---")
    cropped = crop_image(uploaded_file, ratio=ratio, key_suffix=key_suffix)

    if cropped is None:
        return None, "ক্রপ করা যায়নি"

    return cropped, ""
