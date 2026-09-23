import streamlit as st
import httpx

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="TaskMind AI", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------- استایل‌دهی مینیمال و RTL اصلاح‌شده -----------------
st.markdown("""
<style>
    /* تنظیم جهت متن و فونت بدون خرابی Sidebar */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    
    /* رفع مشکل بیرون زدن متن هنگام بستن Sidebar */
    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
        overflow-x: hidden !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        overflow-x: hidden !important;
    }

    /* فاصله بالای صفحه برای تمرکز روی مرکز */
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 2rem !important;
        max-width: 1000px !important;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* استایل ورودی‌ها و دکمه‌ها */
    input, textarea {
        text-align: right;
        border-radius: 10px !important;
    }

    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        height: 2.8rem;
        transition: all 0.2s ease;
    }

    /* استایل زبانه (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 8px;
        padding: 0px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- مدیریت Session State -----------------
if "token" not in st.session_state:
    st.session_state.token = None

def get_auth_headers():
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

# ----------------- بخش ورود و ثبت‌نام مینیمال -----------------
if not st.session_state.token:
    _, col_center, _ = st.columns([1, 2, 1])

    with col_center:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 25px;">
                <h1 style="font-size: 3rem; margin-bottom: 5px;">🧠</h1>
                <h2 style="font-weight: 700; margin-bottom: 5px;">TaskMind AI</h2>
                <p style="color: #64748b; font-size: 0.95rem;">مدیریت هوشمند پروژه‌ها و تسک‌های روزانه</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        tab_login, tab_register = st.tabs(["🔒 ورود به حساب", "📝 ثبت‌نام کاربر جدید"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("نام کاربری", key="login_user", placeholder="نام کاربری خود را وارد کنید")
                password = st.text_input("رمز عبور", type="password", key="login_pass", placeholder="رمز عبور")
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("ورود به حساب 🚀", use_container_width=True, type="primary")

                if submit_login:
                    if not username or not password:
                        st.warning("لطفاً نام کاربری و رمز عبور را وارد کنید.")
                    else:
                        try:
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
                        except Exception as e:
                            st.error(f"خطا در ارتباط با سرور: {e}")

        with tab_register:
            with st.form("register_form", clear_on_submit=False):
                reg_username = st.text_input("نام کاربری جدید", key="reg_user", placeholder="یک نام کاربری انتخاب کنید")
                reg_password = st.text_input("رمز عبور جدید", type="password", key="reg_pass", placeholder="یک رمز عبور قوی وارد کنید")
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                submit_reg = st.form_submit_button("ساخت حساب جدید ✨", use_container_width=True, type="primary")

                if submit_reg:
                    if not reg_username or not reg_password:
                        st.warning("لطفاً تمامی اطلاعات را تکمیل کنید.")
                    else:
                        try:
                            response = httpx.post(
                                f"{API_URL}/register",
                                json={"username": reg_username, "password": reg_password}
                            )
                            if response.status_code == 201:
                                st.success("حساب کاربری شما با موفقیت ساخته شد! اکنون وارد شوید.")
                            else:
                                st.error(response.json().get("detail", "خطا در ثبت‌نام"))
                        except Exception as e:
                            st.error(f"خطا در ارتباط با سرور: {e}")

# ----------------- بخش اصلی برنامه (داشبورد بعد از ورود) -----------------
else:
    col_logo, col_title = st.columns([1, 8])
    with col_logo:
        st.title("🧠")
    with col_title:
        st.title("TaskMind AI Dashboard")
        st.caption("مدیریت هوشمند کارهای روزانه با تحلیل خودکار اولویت و زمان")

    st.divider()

    with st.sidebar:
        st.header("👤 حساب کاربری")
        st.success("نشست شما فعال است")
        if st.button("خروج از حساب", use_container_width=True, type="secondary"):
            st.session_state.token = None
            st.rerun()

    headers = get_auth_headers()
    tab1, tab2 = st.tabs(["📋 مدیریت تسک‌ها", "📊 گزارش Standup"])

    # ---------- تب اول: ثبت و نمایش تسک‌ها ----------
    with tab1:
        st.subheader("➕ ثبت تسک جدید")

        with st.form("create_task_form", clear_on_submit=True):
            title = st.text_input("عنوان تسک", placeholder="مثال: پیاده‌سازی اندپوینت لاگین...")
            description = st.text_area("توضیحات", placeholder="جزئیات تسک را بنویسید...")
            submitted = st.form_submit_button("🚀 ایجاد و پردازش با هوش مصنوعی", use_container_width=True)

            if submitted:
                if not title.strip():
                    st.warning("لطفاً عنوان تسک را وارد کنید.")
                else:
                    try:
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
                            st.rerun()
                        else:
                            st.error(f"خطا: {res.text}")
                    except Exception as e:
                        st.error(f"خطا در ارسال اطلاعات: {e}")

        st.divider()

        # دریافت لیست تسک‌ها
        try:
            res = httpx.get(f"{API_URL}/tasks", headers=headers)
            if res.status_code == 200:
                tasks = res.json()

                total_tasks = len(tasks)
                completed_tasks = sum(1 for t in tasks if t['is_completed'])
                pending_tasks = total_tasks - completed_tasks

                m1, m2, m3 = st.columns(3)
                m1.metric("کل تسک‌ها", total_tasks)
                m2.metric("انجام‌شده ✅", completed_tasks)
                m3.metric("در حال انجام ⏳", pending_tasks)

                st.subheader("📋 لیست تسک‌های فعال")

                if not tasks:
                    st.info("هیچ تسکی ثبت نشده است. از فرم بالا اولین تسک خود را بسازید!")

                for task in tasks:
                    status_icon = "✅" if task['is_completed'] else "⏳"
                    priority_color = "🔴" if task['priority'] == "High" else ("🟡" if task['priority'] == "Medium" else "🟢")

                    with st.expander(f"{status_icon} {priority_color} [{task['priority']}] {task['title']} (~{task['estimated_hours']}h)"):
                        st.write(f"**توضیحات:** {task['description'] if task['description'] else 'بدون توضیحات'}")

                        if task.get('duplicate_warning'):
                            st.warning(f"⚠️ {task['duplicate_warning']}")

                        col1, col2 = st.columns(2)
                        with col1:
                            btn_label = "علامت‌گذاری به عنوان انجام نشده ↩️" if task['is_completed'] else "علامت‌گذاری به عنوان انجام‌شده ✅"
                            if st.button(btn_label, key=f"toggle_{task['id']}", use_container_width=True):
                                httpx.patch(f"{API_URL}/tasks/{task['id']}/toggle", headers=headers)
                                st.rerun()
                        with col2:
                            if st.button("حذف تسک 🗑️", key=f"del_{task['id']}", use_container_width=True, type="secondary"):
                                httpx.delete(f"{API_URL}/tasks/{task['id']}", headers=headers)
                                st.rerun()

            elif res.status_code == 401:
                st.error("نشست شما منقضی شده است. لطفاً دوباره لاگین کنید.")
                st.session_state.token = None
            else:
                st.error("خطا در دریافت تسک‌ها.")
        except Exception as e:
            st.error(f"خطا در ارتباط با بک‌اند: {e}")

    # ---------- تب دوم: گزارش Standup روزانه ----------
    with tab2:
        st.subheader("📊 گزارش Standup روزانه")
        st.caption("گزارش خلاصه وضعیت تسک‌های شما همراه با تحلیل هوش مصنوعی")

        if st.button("تولید / به‌روزرسانی گزارش 🔄", type="primary"):
            try:
                with st.spinner("در حال تحلیل داده‌ها و ساخت گزارش..."):
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