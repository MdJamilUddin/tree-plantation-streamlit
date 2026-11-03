# pages/1_📝_তথ্য_সংগ্রহ.py
import streamlit as st
from datetime import date
from schools import SCHOOLS
from database import get_record_by_school, save_record, upload_photo

st.set_page_config(page_title="তথ্য সংগ্রহ", page_icon="📝", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Bengali:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Noto Sans Bengali', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

st.title("📝 বিদ্যালয়ের তথ্য সংগ্রহ")
st.caption("প্রতিটি বিদ্যালয় থেকে একবার তথ্য যোগ করুন। আগের তথ্য থাকলে সম্পাদনা করা যাবে।")

# বিদ্যালয় নির্বাচন
school_index = st.selectbox(
    "🏫 বিদ্যালয় নির্বাচন করুন",
    options=range(len(SCHOOLS)),
    format_func=lambda i: SCHOOLS[i],
    key="school_selector",
)

# আগের রেকর্ড লোড
existing = get_record_by_school(school_index)

if existing:
    st.success(f"✅ এই বিদ্যালয়ের তথ্য আগে থেকেই সংরক্ষিত আছে — সম্পাদনা করুন")
else:
    st.info("🆕 নতুন তথ্য — সব ফিল্ড পূরণ করুন")

# ===== ফর্ম =====
with st.form(f"form_{school_index}", clear_on_submit=False):

    # ---- বিদ্যালয়ের তথ্য ----
    st.subheader("🏫 বিদ্যালয়ের তথ্য")
    col1, col2, col3 = st.columns(3)
    district = col1.text_input("জেলা", value=(existing or {}).get("district", "নওগাঁ"))
    upazila = col2.text_input("উপজেলা", value=(existing or {}).get("upazila", "রাণীনগর"))
    union_name = col3.text_input("ইউনিয়ন", value=(existing or {}).get("union_name", ""))
    village = st.text_input("গ্রাম", value=(existing or {}).get("village", ""))

    st.divider()

    # ---- বৃক্ষরোপণের তথ্য ----
    st.subheader("🌱 বৃক্ষরোপণের তথ্য")
    c1, c2 = st.columns(2)
    with c1:
        fruit_species = st.text_input("ফলদ প্রজাতি", value=(existing or {}).get("fruit_species", ""),
                                       placeholder="যেমন: আম, লিচু")
        timber_species = st.text_input("বনজ প্রজাতি", value=(existing or {}).get("timber_species", ""),
                                        placeholder="যেমন: সেগুন, মেহগনি")
        medicinal_species = st.text_input("ঔষধি প্রজাতি", value=(existing or {}).get("medicinal_species", ""),
                                           placeholder="যেমন: নিম, তুলসী")
    with c2:
        fruit_count = st.number_input("ফলদ চারার সংখ্যা", min_value=0,
                                       value=int((existing or {}).get("fruit_count", 0)))
        timber_count = st.number_input("বনজ চারার সংখ্যা", min_value=0,
                                        value=int((existing or {}).get("timber_count", 0)))
        medicinal_count = st.number_input("ঔষধি চারার সংখ্যা", min_value=0,
                                           value=int((existing or {}).get("medicinal_count", 0)))

    col1, col2 = st.columns(2)
    planting_date_default = date.today()
    if existing and existing.get("planting_date"):
        try:
            planting_date_default = date.fromisoformat(existing["planting_date"])
        except Exception:
            pass
    planting_date = col1.date_input("বৃক্ষরোপণের তারিখ", value=planting_date_default)
    location = col2.text_input("সুনির্দিষ্ট এলাকা (জিও-কোঅর্ডিনেটসহ)",
                                value=(existing or {}).get("location", ""),
                                placeholder="যেমন: 24.9876, 88.7654")

    st.divider()

    # ---- শিক্ষার্থীর তথ্য ----
    st.subheader("🎓 শিক্ষার্থীর তথ্য")
    c1, c2, c3 = st.columns(3)
    student_name = c1.text_input("শিক্ষার্থীর নাম *", value=(existing or {}).get("student_name", ""))
    father_name = c2.text_input("পিতার নাম *", value=(existing or {}).get("father_name", ""))
    mother_name = c3.text_input("মাতার নাম *", value=(existing or {}).get("mother_name", ""))

    c1, c2 = st.columns([1, 2])
    class_name = c1.text_input("শ্রেণি *", value=(existing or {}).get("class_name", ""))
    student_mobile = c2.text_input("শিক্ষার্থীর মোবাইল", value=(existing or {}).get("student_mobile", ""),
                                    placeholder="01XXXXXXXXX")

    student_address = st.text_area("বর্তমান ঠিকানা *", value=(existing or {}).get("student_address", ""), height=80)

    st.divider()

    # ---- প্রধান শিক্ষকের তথ্য ----
    st.subheader("👨‍🏫 শিক্ষা প্রতিষ্ঠান প্রধানের তথ্য")
    c1, c2 = st.columns(2)
    head_name = c1.text_input("প্রধানের নাম *", value=(existing or {}).get("head_name", ""))
    head_mobile = c2.text_input("প্রধানের মোবাইল *", value=(existing or {}).get("head_mobile", ""),
                                 placeholder="01XXXXXXXXX")

    st.divider()

    # ---- ছবি ----
    st.subheader("📷 বৃক্ষরোপণের ছবি")
    if existing and existing.get("photo_url"):
        st.image(existing["photo_url"], width=250, caption="বর্তমান ছবি")

    photo_file = st.file_uploader("নতুন ছবি আপলোড (ঐচ্ছিক — পুরনোটি থাকলে রাখা যাবে)",
                                    type=["jpg", "jpeg", "png", "webp"])

    st.divider()

    # ---- মন্তব্য ----
    remarks = st.text_area("মন্তব্য (ঐচ্ছিক)", value=(existing or {}).get("remarks", ""), height=80)

    submitted = st.form_submit_button("💾 সংরক্ষণ করুন", use_container_width=True, type="primary")

# ===== সাবমিট হ্যান্ডলিং =====
if submitted:
    # ভ্যালিডেশন
    errors = []
    if not student_name.strip(): errors.append("শিক্ষার্থীর নাম")
    if not father_name.strip(): errors.append("পিতার নাম")
    if not mother_name.strip(): errors.append("মাতার নাম")
    if not class_name.strip(): errors.append("শ্রেণি")
    if not student_address.strip(): errors.append("ঠিকানা")
    if not head_name.strip(): errors.append("প্রধানের নাম")
    if not head_mobile.strip(): errors.append("প্রধানের মোবাইল")

    if errors:
        st.error(f"❌ আবশ্যক ফিল্ড পূরণ করুন: {', '.join(errors)}")
    else:
        with st.spinner("সংরক্ষণ করা হচ্ছে..."):
            photo_url = (existing or {}).get("photo_url", "")
            if photo_file is not None:
                photo_url = upload_photo(photo_file, school_index)

            data = {
                "district": district.strip(),
                "upazila": upazila.strip(),
                "union_name": union_name.strip(),
                "village": village.strip(),
                "fruit_species": fruit_species.strip(),
                "fruit_count": fruit_count,
                "timber_species": timber_species.strip(),
                "timber_count": timber_count,
                "medicinal_species": medicinal_species.strip(),
                "medicinal_count": medicinal_count,
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
                st.success(f"✅ {SCHOOLS[school_index]} এর তথ্য সফলভাবে সংরক্ষিত হয়েছে!")
                st.balloons()
                st.rerun()