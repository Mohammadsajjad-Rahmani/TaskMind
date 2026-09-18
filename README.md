# 🧠 TaskMind AI
> A simple, machine learning-powered task management copilot built with Python.

Hi there! This project is a task management app built using FastAPI and Streamlit. It leverages Scikit-Learn for smart task priority prediction and realistic time estimation.

My main goal in building this project was to gain hands-on experience in API architecture, database integration, and applying foundational Machine Learning algorithms to a real-world project.

---

## 🛠️ Tech Stack

- Backend: FastAPI (Python)
- Database: SQLite with SQLAlchemy ORM
- Machine Learning & NLP: Scikit-Learn (LogisticRegression, Ridge, TfidfVectorizer)
- Frontend UI: Streamlit
- Package Management: uv

---

## 💡 Core Features

1. Smart Priority Prediction: Automatically categorizes tasks (High, Medium, Low) based on text context.
2. ML Time Estimation: Predicts estimated completion time (in hours) using regression.
3. Duplicate Task Detection: Flags highly similar tasks using Cosine Similarity to avoid duplicates.
4. Task Management (CRUD): Supports creating, completing/toggling status, and deleting tasks.
5. Daily Standup Summary: Generates a Markdown report summarizing total, completed, and pending tasks.

---

## 🚀 How to Run Locally

1. Clone the repository:
git clone https://github.com/your-username/taskmind-ai.git
cd taskmind-ai

2. Install dependencies automatically using uv:
uv sync

3. Start the FastAPI Backend:
uv run uvicorn main:app --reload

(Swagger Docs available at http://127.0.0.1:8000/docs)

4. Start the Streamlit UI (in a separate terminal):
uv run streamlit run app_ui.py

(Dashboard available at http://localhost:8501)