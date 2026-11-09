# auth.py
import streamlit as st
import hmac

SESSION_TIMEOUT_MINUTES = 120  # ২ ঘণ্টা পর স্বয়ংক্রিয় লগআউট


def _get_admin_password() -> str:
    try:
        return st.secrets["admin"]["password"]
    except Exception:
        return "admin123"  # ফলব্যাক (ডেভেলপমেন্টের জন্য)


def check_password(password: str) -> bool:
    """Constant-time তুলনা"""
    expected = _get_admin_password()
    return hmac.compare_digest(password.encode(), expected.encode())


def login_form():
    """অ্যাডমিন লগইন UI"""
    st.markdown(
        """
        <div style="max-width:420px; margin:60px auto; padding:32px;
                    background:#fff; border-radius:16px;
                    box-shadow:0 8px 32px rgba(0,0,0,0.08);
                    border-top:6px solid #2e7d32;">
            <h2 style="text-align:center; color:#2e7d32; margin-top:0;">🔐 অ্যাডমিন লগইন</h2>
            <p style="text-align:center; color:#666; font-size:0.9rem;">
                শুধুমাত্র অনুমোদিত ব্যক্তির জন্য
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("admin_login_form"):
        pwd = st.text_input("পাসওয়ার্ড", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("🔓 লগইন করুন", use_container_width=True, type="primary")

        if submitted:
            if check_password(pwd):
                st.session_state["is_admin"] = True
                st.success("✅ সফলভাবে লগইন হয়েছে")
                st.rerun()
            else:
                st.error("❌ ভুল পাসওয়ার্ড")


def is_admin() -> bool:
    return st.session_state.get("is_admin", False)


def require_admin():
    """অ্যাডমিন না হলে থামিয়ে দেয়"""
    if not is_admin():
        login_form()
        st.stop()


def logout_button():
    """সাইডবারে লগআউট বাটন"""
    if is_admin():
        if st.sidebar.button("🚪 লগআউট", use_container_width=True):
            st.session_state["is_admin"] = False
            st.rerun()


def admin_badge():
    """সাইডবারে অ্যাডমিন ব্যাজ"""
    if is_admin():
        st.sidebar.success("👑 অ্যাডমিন মোড চালু")