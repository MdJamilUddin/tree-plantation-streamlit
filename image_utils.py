def crop_image(uploaded_file, ratio=None, key_suffix=""):
    """
    ইউজারকে ব্রাউজারে ছবি ক্রপ করতে দেয়।
    Returns: PIL.Image (ক্রপ করা) অথবা None
    """
    img = Image.open(uploaded_file).convert("RGB")

    # বড় ছবি হলে রিসাইজ
    if img.width > 1200:
        ratio_scale = 1200 / img.width
        img = img.resize((1200, int(img.height * ratio_scale)))

    st.markdown("**✂️ ছবি ক্রপ করুন** (প্রয়োজনে অপ্রয়োজনীয় অংশ বাদ দিন)")

    # কাস্টম CSS: Cropper-এর ড্র্যাগ হ্যান্ডেলগুলো হলুদ রঙ করা
    st.markdown("""
        <style>
        /* Cropper-এর কর্নার হ্যান্ডেলগুলো হলুদ রঙ */
        .reactEasyCrop_CropAreaRound,
        .reactEasyCrop_CropArea,
        .reactEasyCrop_CropArea > div {
            border-color: #FFD700 !important;
            box-shadow: 0 0 0 1px #FFD700 !important;
        }
        
        /* ড্র্যাগ হ্যান্ডেলগুলো হলুদ রঙ */
        .reactEasyCrop_CropArea > div {
            background-color: #FFD700 !important;
            border-radius: 50% !important;
        }

        /* Cropper-এর ওভারলে হালকা কমলা করা */
        .reactEasyCrop_CropArea {
            border: 2px solid #FFD700 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Cropper রেন্ডার
    cropped = st_cropper(
        img,
        realtime_update=True,
        box_color="#FFD700",  # বর্ডার হলুদ
        aspect_ratio=ratio,
        return_type="image",
        key=f"cropper_{key_suffix}",
    )

    st.markdown("**✅ ক্রপ করা ছবি (এটিই সংরক্ষিত হবে)**")
    st.image(cropped, use_container_width=True)

    return cropped
