# pages/1_📝_তথ্য_সংগ্রহ.py
"""
বিদ্যালয়ের তথ্য সংগ্রহ — পাবলিক ফর্ম
- বিদ্যালয় নির্বাচন
- ছবি আপলোড + ক্রপ + প্রিভিউ
- ভ্যালিডেশন + সংরক্ষণ
"""

import streamlit as st
from datetime import date

from schools import SCHOOLS
from database import get_record_by_school, save_record, upload_photo
from ui_utils import inject_css, hero, section
from image_utils import process_upload


# ============================================================
# পেজ কনফিগ
# ============================================================
st.set_page_config(
    page_title="তথ্য সংগ্রহ",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()
hero(
    "📝 বিদ্যালয়ের তথ্য সংগ্রহ",
    "প্রতিটি বিদ্যালয় থেকে একবার তথ্য দিন — আগের তথ্য সম্পাদনাও করা যাবে",
)


# ============================================================
# বিদ্যালয় নির্বাচন
# ============================================================
school_index = st.selectbox(
    "🏫 বিদ্যালয় নির্বাচন করুন",
    options=range(len(SCHOOLS)),
    format_func=lambda i: SCHOOLS[i],
    key="school_selector",
)

existing = get_record_by_school(school_index)

if existing:
    st.success(
        f"✅ **{SCHOOLS[school_index]}** — আগের তথ্য পাওয়া গেছে, সম্পাদনা করুন"
    )
else:
    st.info("🆕 নতুন তথ্য — সব প্রয়োজনীয় (*) ফিল্ড পূরণ করুন")


# ============================================================
# ভ্যালিডেশন হেল্পার
# ============================================================
def _v(key: str, default: str = "") -> str:
    """existing থেকে মান নেওয়ার শর্টকাট"""
    if existing:
        val = existing.get(key)
        return "" if val is None else str(val)
    return default


def _vi(key: str, default: int = 0) -> int:
    """existing থেকে integer"""
    if existing:
        val = existing.get(key)
        try:
            return int(val) if val is not None else default
        except (ValueError, TypeError):
            return default
    return default


# ============================================================
# ফর্ম
# ============================================================
with st.form(f"form_{school_index}", clear_on_submit=False):

    # ---- বিদ্যালয়ের তথ্য ----
    section("🏫 বিদ্যালয়ের তথ্য")
    c1, c2 = st.columns(2)
    district = c1.text_input("জেলা", value=_v("district", "নওগাঁ"))
    upazila = c2.text_input("উপজেলা", value=_v("upazila", "রাণীনগর"))
    c1, c2 = st.columns(2)
    union_name = c1.text_input("ইউনিয়ন", value=_v("union_name"))
    village = c2.text_input("গ্রাম", value=_v("village"))

    # ---- বৃক্ষরোপণ ----
    section("🌱 বৃক্ষরোপণের তথ্য")

    c1, c2 = st.columns(2)
    fruit_species = c1.text_input(
        "ফলদ প্রজাতি",
        value=_v("fruit_species"),
        placeholder="যেমন: আম, লিচু",
    )
    fruit_count = c2.number_input(
        "ফলদ চারার সংখ্যা", min_value=0, value=_vi("fruit_count")
    )

    c1, c2 = st.columns(2)
    timber_species = c1.text_input(
        "বনজ প্রজাতি",
        value=_v("timber_species"),
        placeholder="যেমন: সেগুন, মেহগনি",
    )
    timber_count = c2.number_input(
        "বনজ চারার সংখ্যা", min_value=0, value=_vi("timber_count")
    )

    c1, c2 = st.columns(2)
    medicinal_species = c1.text_input(
        "ঔষধি প্রজাতি",
        value=_v("medicinal_species"),
        placeholder="যেমন: নিম, তুলসী",
    )
    medicinal_count = c2.number_input(
        "ঔষধি চারার সংখ্যা", min_value=0, value=_vi("medicinal_count")
    )

    # তারিখ
    planting_date_default = date.today()
    if existing and existing.get("planting_date"):
        try:
            planting_date_default = date.fromisoformat(existing["planting_date"])
        except Exception:
            pass

    planting_date = st.date_input(
        "🗓️ বৃক্ষরোপণের তারিখ", value=planting_date_default
    )
    location = st.text_input(
        "📍 সুনির্দিষ্ট এলাকা (জিও-কোঅর্ডিনেটসহ)",
        value=_v("location"),
        placeholder="যেমন: 24.9876, 88.7654",
    )

    # ---- শিক্ষার্থী ----
    section("🎓 শিক্ষার্থীর তথ্য")
    student_name = st.text_input(
        "শিক্ষার্থীর নাম *", value=_v("student_name")
    )
    c1, c2 = st.columns(2)
    father_name = c1.text_input("পিতার নাম *", value=_v("father_name"))
    mother_name = c2.text_input("মাতার নাম *", value=_v("mother_name"))
    c1, c2 = st.columns(2)
    class_name = c1.text_input("শ্রেণি *", value=_v("class_name"))
    student_mobile = c2.text_input(
        "শিক্ষার্থীর মোবাইল",
        value=_v("student_mobile"),
        placeholder="01XXXXXXXXX",
    )
    student_address = st.text_area(
        "বর্তমান ঠিকানা *", value=_v("student_address"), height=70
    )

    # ---- প্রধান শিক্ষক ----
    section("👨‍🏫 শিক্ষা প্রতিষ্ঠান প্রধানের তথ্য")
    c1, c2 = st.columns(2)
    head_name = c1.text_input("প্রধানের নাম *", value=_v("head_name"))
    head_mobile = c2.text_input(
        "প্রধানের মোবাইল *",
        value=_v("head_mobile"),
        placeholder="01XXXXXXXXX",
    )

    # ---- মন্তব্য ----
    section("📝 মন্তব্য")
    remarks = st.text_area(
        "মন্তব্য (ঐচ্ছিক)", value=_v("remarks"), height=70
    )

    # ---- সাবমিট ----
    submitted = st.form_submit_button(
        "💾 সংরক্ষণ করুন",
        use_container_width=True,
        type="primary",
    )


# ============================================================
# 📷 ছবি (ফর্মের বাইরে — cropper নিজের UI চালায়)
# ============================================================
section("📷 বৃক্ষরোপণের ছবি")

if existing and existing.get("photo_url"):
    st.markdown("**বর্তমান সংরক্ষিত ছবি:**")
    c1, c2 = st.columns([1, 3])
    with c1:
        st.image(existing["photo_url"], caption="সর্বশেষ আপলোড")
    with c2:
        st.markdown(
            """
            - এই ছবিটি ইতিমধ্যে সংরক্ষিত আছে
            - নতুন ছবি আপলোড করলে এটি প্রতিস্থাপিত হবে
            - না করলে পুরনোটি অপরিবর্তিত থাকবে
            """
        )

uploaded = st.file_uploader(
    "নতুন ছবি আপলোড করুন",
    type=["jpg", "jpeg", "png", "webp"],
    key=f"uploader_{school_index}",
    help="JPG/PNG/WEBP • সর্বোচ্চ 10MB • আপলোডের পর ক্রপ করতে পারবেন",
)

cropped_img = None
if uploaded:
    cropped_img, crop_err = process_upload(
        uploaded,
        ratio=None,  # ফ্রি-ক্রপ; চাইলে (4,3) বা (1,1) দিন
        key_suffix=str(school_index),
    )
    if crop_err:
        st.error(f"❌ {crop_err}")


# ============================================================
# সাবমিট হ্যান্ডলিং
# ============================================================
if submitted:
    # ---- ফিল্ড ভ্যালিডেশন ----
    required = [
        (student_name, "শিক্ষার্থীর নাম"),
        (father_name, "পিতার নাম"),
        (mother_name, "মাতার নাম"),
        (class_name, "শ্রেণি"),
        (student_address, "বর্তমান ঠিকানা"),
        (head_name, "প্রধানের নাম"),
        (head_mobile, "প্রধানের মোবাইল"),
    ]
    missing = [label for val, label in required if not val.strip()]

    if missing:
        st.error(f"❌ আবশ্যক ফিল্ড পূরণ করুন: {', '.join(missing)}")
    else:
        # ---- মোবাইল নম্বর যাচাই (ঐচ্ছিক কিন্তু থাকলে সঠিক হতে হবে) ----
        bad_mobile = None
        for val, name in [
            (student_mobile, "শিক্ষার্থীর মোবাইল"),
            (head_mobile, "প্রধানের মোবাইল"),
        ]:
            if val.strip() and (not val.strip().isdigit() or len(val.strip()) != 11):
                bad_mobile = name
                break

        if bad_mobile:
            st.error(f"❌ {bad_mobile} — ১১ ডিজিটের সঠিক নম্বর দিন (01XXXXXXXXX)")
        else:
            with st.spinner("সংরক্ষণ করা হচ্ছে..."):
                # ---- ছবি: ক্রপ করা থাকলে সেটাই আপলোড ----
                photo_url = (existing or {}).get("photo_url", "") or ""
                if cropped_img is not None:
                    photo_url = upload_photo(cropped_img, school_index)

                # ---- ডেটা প্যাক ----
                data = {
                    "district": district.strip(),
                    "upazila": upazila.strip(),
                    "union_name": union_name.strip(),
                    "village": village.strip(),
                    "fruit_species": fruit_species.strip(),
                    "fruit_count": int(fruit_count),
                    "timber_species": timber_species.strip(),
                    "timber_count": int(timber_count),
                    "medicinal_species": medicinal_species.strip(),
                    "medicinal_count": int(medicinal_count),
                    "planting_date": planting_date.isoformat(),
                    "location": location.strip(),
                    "student_name": student_name.strip(),
                    "father_name": father_name.strip(),
                    "mother_name": mother_name.strip(),
                    "class_name": class_name.strip(),
                    "student_address": student_address.strip(),
                    "student_mobile": student_mobile.strip(),
                    "head_name": head_name.strip(),
                    "head_mobile": head_mobile.strip(),
                    "remarks": remarks.strip(),
                    "photo_url": photo_url,
                }

                if save_record(data, school_index):
                    st.success(
                        f"✅ **{SCHOOLS[school_index]}** এর তথ্য সফলভাবে সংরক্ষিত হয়েছে!"
                    )
                    st.balloons()
                    st.rerun()


# ============================================================
# নিচে সহায়ক নোট
# ============================================================
st.markdown("---")
with st.expander("ℹ️ সহায়তা", expanded=False):
    st.markdown(
        """
        **ছবি আপলোডের নিয়ম**
        - ফরম্যাট: JPG / PNG / WEBP
        - সর্বোচ্চ 10 MB
        - আপলোডের পর ব্রাউজারে ক্রপ করে অপ্রয়োজনীয় অংশ বাদ দিন
        - ছবিটি স্বয়ংক্রিয়ভাবে 1200px প্রস্থে রিসাইজ হবে

        **সংরক্ষণ**
        - প্রথমবার = নতুন রেকর্ড তৈরি
        - পরেরবার = আগের রেকর্ড আপডেট
        - একটি বিদ্যালয়ে একবারই তথ্য রাখা যায়

        **সমস্যা হলে**
        - সাইডবার → ⚙️ সেটিংসে যান
        - সংযোগ পরীক্ষা করুন
        """
    )