import streamlit as st
import httpx

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="TaskMind AI", page_icon="🧠", layout="wide")

# ۱. مدیریت Session State برای توکن
if "token" not in st.session_state:
    st.session_state.token = None

# تابع کمکی برای ساخت هدر احراز هویت
def get_auth_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

st.title("🧠 TaskMind AI Dashboard")
st.caption("سرویس هوشمند مدیریت کارهای روزانه با FastAPI و Scikit-Learn")

# ----------------- بخش ورود و ثبت‌نام -----------------
if not st.session_state.token:
    st.subheader("🔑 ورود / ثبت‌نام")
    tab_login, tab_register = st.tabs(["ورود", "ثبت‌نام"])

    with tab_login:
        username = st.text_input("نام کاربری", key="login_user")
        password = st.text_input("رمز عبور", type="password", key="login_pass")
        if st.button("ورود به سیستم"):
            response = httpx.post(
                f"{API_URL}/login",
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.token = data["access_token"]
                st.success("با موفقیت وارد شدید!")
                st.rerun()
            else:
                st.error("نام کاربری یا رمز عبور اشتباه است.")

    with tab_register:
        reg_username = st.text_input("نام کاربری جدید", key="reg_user")
        reg_password = st.text_input("رمز عبور جدید", type="password", key="reg_pass")
        if st.button("ایجاد حساب"):
            response = httpx.post(
                f"{API_URL}/register",
                json={"username": reg_username, "password": reg_password}
            )
            if response.status_code == 201:
                st.success("حساب با موفقیت ساخته شد. حالا وارد شوید.")
            else:
                st.error(response.json().get("detail", "خطا در ثبت‌نام"))

# ----------------- بخش اصلی برنامه (تسک‌ها و گزارش) -----------------
else:
    # دکمه خروج در نوار کناری
    with st.sidebar:
        st.header("👤 حساب کاربری")
        if st.button("خروج از حساب"):
            st.session_state.token = None
            st.rerun()

    headers = get_auth_headers()

    # ایجاد تب‌های اصلی برنامه
    tab1, tab2 = st.tabs(["📋 مدیریت تسک‌ها", "📊 گزارش روزانه"])

    # ---------- تب اول: ثبت و نمایش تسک‌ها ----------
    with tab1:
        st.subheader("➕ ثبت تسک جدید")
        with st.form("create_task_form"):
            title = st.text_input("عنوان تسک")
            description = st.text_area("توضیحات")
            submitted = st.form_submit_button("ایجاد تسک با هوش مصنوعی")

            if submitted:
                if not title:
                    st.warning("لطفاً عنوان تسک را وارد کنید.")
                else:
                    res = httpx.post(
                        f"{API_URL}/tasks",
                        json={"title": title, "description": description},
                        headers=headers
                    )
                    if res.status_code == 200:
                        st.success("تسک با موفقیت ایجاد و توسط AI پردازش شد!")
                        st.rerun()
                    elif res.status_code == 401:
                        st.error("اعتبار توکن شما تمام شده است. دوباره لاگین کنید.")
                        st.session_state.token = None
                    else:
                        st.error(f"خطا: {res.text}")

        st.divider()

        st.subheader("📋 تسک‌های شما")
        res = httpx.get(f"{API_URL}/tasks", headers=headers)

        if res.status_code == 200:
            tasks = res.json()
            if not tasks:
                st.info("هیچ تسکی ثبت نشده است.")
            for task in tasks:
                with st.expander(f"{'✅' if task['is_completed'] else '⏳'} [{task['priority']}] {task['title']} (~{task['estimated_hours']}h)"):
                    st.write(f"**توضیحات:** {task['description']}")
                    if task.get('duplicate_warning'):
                        st.warning(task['duplicate_warning'])
                    
                    st.write("**زیرتسک‌های پیشنهادی AI:**")
                    for sub in task.get('suggested_subtasks', []):
                        st.write(f"- {sub}")

                    col1, col2 = st.columns(2)
                    with col1:
                        btn_label = "علامت‌گذاری به عنوان انجام نشده" if task['is_completed'] else "علامت‌گذاری به عنوان انجام‌شده ✅"
                        if st.button(btn_label, key=f"toggle_{task['id']}"):
                            httpx.patch(f"{API_URL}/tasks/{task['id']}/toggle", headers=headers)
                            st.rerun()
                    with col2:
                        if st.button("حذف تسک 🗑️", key=f"del_{task['id']}"):
                            httpx.delete(f"{API_URL}/tasks/{task['id']}", headers=headers)
                            st.rerun()
        elif res.status_code == 401:
            st.error("نشست شما منقضی شده است. لطفاً دوباره لاگین کنید.")
            st.session_state.token = None
        else:
            st.error("خطا در دریافت تسک‌ها.")

    # ---------- تب دوم: گزارش Standup روزانه ----------
    with tab2:
        st.subheader("📊 گزارش Standup روزانه")
        st.caption("گزارش خلاصه وضعیت تسک‌های شما همراه با تحلیل هوش مصنوعی")

        if st.button("تولید / به‌روزرسانی گزارش"):
            try:
                res = httpx.get(f"{API_URL}/daily-summary", headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    st.markdown(data.get('summary_markdown', 'گزارشی دریافت نشد.'))
                elif res.status_code == 401:
                    st.error("نشست شما منقضی شده است.")
                    st.session_state.token = None
                else:
                    st.error(f"خطا در دریافت گزارش: {res.text}")
            except Exception as e:
                st.error(f"خطا در ارتباط با سرور: {e}")