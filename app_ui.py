import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="TaskMind AI Copilot", page_icon="🧠", layout="wide")

st.title("🧠 TaskMind AI - مدیریت هوشمند تسک‌ها")
st.caption("سرویس هوشمند مدیریت کارهای روزانه با FastAPI و Scikit-Learn")

with st.sidebar:
    st.header("➕ افزودن تسک جدید")
    title = st.text_input("عنوان تسک (Title)")
    description = st.text_area("توضیحات (Description)")
    
    if st.button("ثبت تسک", type="primary"):
        if title and description:
            try:
                res = requests.post(f"{API_URL}/tasks", json={"title": title, "description": description})
                if res.status_code == 200:
                    st.success("تسک با موفقیت ایجاد شد!")
                    st.rerun()
                else:
                    st.error(f"خطا: {res.text}")
            except Exception as e:
                st.error(f"عدم اتصال به سرور: {e}")
        else:
            st.warning("لطفاً تمامی فیلدها را پر کنید.")

tab1, tab2 = st.tabs(["📋 لیست تسک‌ها", "📊 گزارش روزانه"])

with tab1:
    st.subheader("تسک‌های ذخیره شده در دیتابیس")
    try:
        res = requests.get(f"{API_URL}/tasks")
        if res.status_code == 200:
            tasks = res.json()
            if not tasks:
                st.info("هنوز تسکی ثبت نشده است.")
            for t in tasks:
                status_icon = "✅" if t['is_completed'] else "⏳"
                with st.expander(f"{status_icon} [{t['priority']}] {t['title']} (~{t['estimated_hours']}h)"):
                    st.write(f"**توضیحات:** {t['description']}")
                    if t.get('duplicate_warning'):
                        st.warning(t['duplicate_warning'])
                    
                    st.write("**زیرمجموعه کارهای پیشنهادی:**")
                    for sub in t.get('suggested_subtasks', []):
                        st.write(f"- {sub}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        btn_label = "علامت‌گذاری به عنوان انجام‌نشده" if t['is_completed'] else "علامت‌گذاری به عنوان انجام‌شده ✅"
                        if st.button(btn_label, key=f"toggle_{t['id']}"):
                            requests.patch(f"{API_URL}/tasks/{t['id']}/toggle")
                            st.rerun()
                    with col2:
                        if st.button("حذف تسک 🗑️", key=f"del_{t['id']}"):
                            requests.delete(f"{API_URL}/tasks/{t['id']}")
                            st.rerun()
    except Exception as e:
        st.error(f"خطا در دریافت لیست تسک‌ها: {e}")

with tab2:
    st.subheader("گزارش Standup روزانه")
    if st.button("تولید گزارش جدید"):
        try:
            res = requests.get(f"{API_URL}/daily-summary")
            if res.status_code == 200:
                data = res.json()
                st.markdown(data['summary_markdown'])
        except Exception as e:
            st.error(f"خطا: {e}")