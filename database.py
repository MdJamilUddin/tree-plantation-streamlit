# database.py
"""
Supabase ডেটাবেস ও Storage লজিক
- plantations টেবিল: বিদ্যালয়ভিত্তিক ডেটা (upsert on school_index)
- photos bucket: ক্রপ-করা ছবি সংরক্ষণ
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from io import BytesIO
from PIL import Image
import pandas as pd

from schools import SCHOOLS


# ============================================================
# ক্লায়েন্ট (ক্যাশড)
# ============================================================
@st.cache_resource(show_spinner=False)
def get_client() -> Client:
    """Supabase ক্লায়েন্ট একবারই তৈরি হয়, সব পেজে শেয়ার হয়"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


# ============================================================
# রিড অপারেশন
# ============================================================
def get_all_records() -> pd.DataFrame:
    """সব রেকর্ড DataFrame আকারে (school_index অনুসারে সাজানো)"""
    try:
        client = get_client()
        res = (
            client.table("plantations")
            .select("*")
            .order("school_index")
            .execute()
        )
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        st.error(f"ডেটা লোড ব্যর্থ: {e}")
        return pd.DataFrame()


def get_record_by_school(school_index: int) -> dict | None:
    """একটি নির্দিষ্ট বিদ্যালয়ের রেকর্ড (না থাকলে None)"""
    try:
        client = get_client()
        res = (
            client.table("plantations")
            .select("*")
            .eq("school_index", school_index)
            .execute()
        )
        return res.data[0] if res.data else None
    except Exception as e:
        st.error(f"রেকর্ড লোড ব্যর্থ: {e}")
        return None


def get_stats() -> dict:
    """সারসংক্ষেপ পরিসংখ্যান — ল্যান্ডিং পেজে ব্যবহার"""
    try:
        df = get_all_records()
        if df.empty:
            return {"total_schools": 0, "fruit": 0, "timber": 0, "medicinal": 0}
        return {
            "total_schools": len(df),
            "fruit": int(df["fruit_count"].fillna(0).sum()),
            "timber": int(df["timber_count"].fillna(0).sum()),
            "medicinal": int(df["medicinal_count"].fillna(0).sum()),
        }
    except Exception:
        return {"total_schools": 0, "fruit": 0, "timber": 0, "medicinal": 0}


# ============================================================
# স্টোরেজ — ছবি আপলোড
# ============================================================
def upload_photo(pil_img: Image.Image, school_index: int) -> str:
    """
    PIL.Image → Supabase Storage (`photos` bucket) → public URL

    - স্বয়ংক্রিয় রিসাইজ: সর্বোচ্চ 1200px প্রস্থ
    - JPEG quality 80 (ভালো ভারসাম্য)
    - upsert বাদ (Storage RLS এরর এড়াতে)
    """
    try:
        client = get_client()

        # ---- রিসাইজ ----
        if pil_img.width > 1200:
            scale = 1200 / pil_img.width
            pil_img = pil_img.resize(
                (1200, int(pil_img.height * scale)),
                Image.LANCZOS,
            )

        # ---- বাফারে সেভ ----
        buf = BytesIO()
        pil_img.convert("RGB").save(
            buf, format="JPEG", quality=80, optimize=True
        )
        buf.seek(0)

        # ---- ফাইলনাম (ইউনিক) ----
        filename = (
            f"school_{school_index + 1:03d}_"
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        )

        # ---- আপলোড (upsert ছাড়া) ----
        client.storage.from_("photos").upload(
            path=filename,
            file=buf.getvalue(),
            file_options={"content-type": "image/jpeg"},
        )

        # ---- পাবলিক URL ----
        return client.storage.from_("photos").get_public_url(filename)
    except Exception as e:
        st.error(f"ছবি আপলোড ব্যর্থ: {e}")
        return ""


# ============================================================
# রাইট অপারেশন
# ============================================================
def save_record(data: dict, school_index: int) -> bool:
    """
    রেকর্ড সংরক্ষণ (upsert on `school_index`)।
    - আগের তথ্য থাকলে আপডেট হবে
    - না থাকলে নতুন তৈরি হবে
    """
    try:
        client = get_client()
        data = dict(data)  # কপি — অরিজিনাল ডিক্ট না বদলাতে
        data["school_index"] = school_index
        data["school_name"] = SCHOOLS[school_index]
        data["updated_at"] = datetime.now().isoformat()

        client.table("plantations").upsert(
            data, on_conflict="school_index"
        ).execute()
        return True
    except Exception as e:
        st.error(f"সংরক্ষণ ব্যর্থ: {e}")
        return False


def delete_record(school_index: int) -> bool:
    """একটি রেকর্ড স্থায়ীভাবে মুছে ফেলুন"""
    try:
        client = get_client()
        client.table("plantations").delete().eq(
            "school_index", school_index
        ).execute()
        return True
    except Exception as e:
        st.error(f"মুছে ফেলা ব্যর্থ: {e}")
        return False


def update_counters(school_index: int, fruit: int, timber: int,
                     medicinal: int, remarks: str = "") -> bool:
    """অ্যাডমিন প্যানেল থেকে কুইক-এডিট (শুধু সংখ্যা ও মন্তব্য)"""
    try:
        client = get_client()
        client.table("plantations").update({
            "fruit_count": fruit,
            "timber_count": timber,
            "medicinal_count": medicinal,
            "remarks": remarks.strip(),
            "updated_at": datetime.now().isoformat(),
        }).eq("school_index", school_index).execute()
        return True
    except Exception as e:
        st.error(f"আপডেট ব্যর্থ: {e}")
        return False


def reset_all_records() -> bool:
    """⚠️ সব ডেটা মুছে ফেলা (অ্যাডমিন-শুধু)"""
    try:
        client = get_client()
        # সব row একসাথে delete
        client.table("plantations").delete().neq(
            "school_index", -999
        ).execute()
        return True
    except Exception as e:
        st.error(f"রিসেট ব্যর্থ: {e}")
        return False


# ============================================================
# হেলথ-চেক (ডায়াগনস্টিক)
# ============================================================
def health_check() -> dict:
    """সংযোগ, টেবিল ও bucket যাচাই"""
    status = {"client": False, "table": False, "bucket": False, "error": None}
    try:
        client = get_client()
        status["client"] = True

        # টেবিল
        try:
            client.table("plantations").select("id").limit(1).execute()
            status["table"] = True
        except Exception as e:
            status["error"] = f"টেবিল: {e}"

        # bucket
        try:
            client.storage.get_bucket("photos")
            status["bucket"] = True
        except Exception as e:
            status["error"] = (status["error"] or "") + f" | Bucket: {e}"

    except Exception as e:
        status["error"] = str(e)

    return status
