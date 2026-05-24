from __future__ import annotations
import streamlit as st
from src.utils.supabase_client import get_supabase


def login(username: str, password: str) -> tuple[bool, str]:
    try:
        db = get_supabase()

        row = db.table("user_roles").select("user_id, role, username")\
            .eq("username", username.strip())\
            .execute()

        if not row.data:
            return False, "Tên đăng nhập không tồn tại."

        user_id = row.data[0]["user_id"]
        role    = row.data[0]["role"]

        user_info = db.auth.admin.get_user_by_id(user_id)
        email     = user_info.user.email

        res = db.auth.sign_in_with_password({"email": email, "password": password})

        if res.user is None:
            return False, "Mật khẩu không đúng."

        st.session_state["auth_user"] = {
            "id":       res.user.id,
            "email":    res.user.email,
            "username": username,
        }
        st.session_state["auth_token"] = res.session.access_token
        st.session_state["auth_role"]  = role
        return True, "Đăng nhập thành công!"

    except Exception as e:
        msg = str(e)
        if "Invalid login credentials" in msg:
            return False, "Mật khẩu không đúng."
        return False, f"Lỗi: {msg}"


def logout():
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    for key in ["auth_user", "auth_token", "auth_role"]:
        st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return "auth_user" in st.session_state


def is_admin() -> bool:
    return st.session_state.get("auth_role") == "admin"


def get_current_role() -> str | None:
    return st.session_state.get("auth_role")
