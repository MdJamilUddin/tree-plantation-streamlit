# database.py
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd
from PIL import Image
import io
from schools import SCHOOLS


@st.cache_resource
def get_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


def get_all_records() -> pd.DataFrame:
    """সব রেকর্ড DataFrame আকারে ফেরত দেয়"""
    try:
        client = get_client()
        res = client.table("plantations").select("*").order("school_index").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"ডেটা লোড ব্যর্থ: {e}")
        return pd.DataFrame()


def get_record_by_school(school_index: int) -> dict | None:
    """একটি নির্দিষ্ট বিদ্যালয়ের রেকর্ড"""
    try:
        client = get_client()
        res = client.table("plantations").select("*").eq("school_index", school_index).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        st.error(f"রেকর্ড লোড ব্যর্থ: {e}")
        return None


def upload_photo(file, school_index: int) -> str:
    """ছবি Supabase Storage-এ আপলোড করে URL ফেরত দেয়"""
    try:
        client = get_client()
        # ছবি রিসাইজ (800px)
        img = Image.open(file)
        if img.width > 800:
            ratio = 800 / img.width
            img = img.resize((800, int(img.height * ratio)))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=75)
        buf.seek(0)

        filename = f"school_{school_index+1:03d}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        client.storage.from_("photos").upload(
            path=filename,
            file=buf.getvalue(),
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )
        return client.storage.from_("photos").get_public_url(filename)
    except Exception as e:
        st.error(f"ছবি আপলোড ব্যর্থ: {e}")
        return ""


def save_record(data: dict, school_index: int) -> bool:
    """রেকর্ড সংরক্ষণ (upsert)"""
    try:
        client = get_client()
        data["school_index"] = school_index
        data["school_name"] = SCHOOLS[school_index]
        data["updated_at"] = datetime.now().isoformat()
        client.table("plantations").upsert(data, on_conflict="school_index").execute()
        return True
    except Exception as e:
        st.error(f"সংরক্ষণ ব্যর্থ: {e}")
        return False


def delete_record(school_index: int) -> bool:
    try:
        client = get_client()
        client.table("plantations").delete().eq("school_index", school_index).execute()
        return True
    except Exception as e:
        st.error(f"মুছে ফেলা ব্যর্থ: {e}")
        return False


def get_stats() -> dict:
    """সারসংক্ষেপ পরিসংখ্যান"""
    df = get_all_records()
    if df.empty:
        return {"total_schools": 0, "fruit": 0, "timber": 0, "medicinal": 0}
    return {
        "total_schools": len(df),
        "fruit": int(df["fruit_count"].fillna(0).sum()),
        "timber": int(df["timber_count"].fillna(0).sum()),
        "medicinal": int(df["medicinal_count"].fillna(0).sum()),
    }