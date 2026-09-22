from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LogisticRegression, Ridge
import numpy as np
from typing import List, Tuple

class TaskAIEngine:
    def __init__(self):
        self.priority_texts = [
            "fix critical database server crash immediately",
            "urgent security patch for payment gateway",
            "خطای شدید در سرور و دیتابیس اورژانسی",
            "باگ بحرانی در درگاه پرداخت آنلاین فوری",
            "update documentation readme file",
            "change UI button colors and styles",
            "آپدیت فایل توضیحات و مستندات پروژه",
            "تغییر رنگ دکمه‌های صفحه اصلی سایت",
            "review code pull request and write tests",
            "add new feature chart to dashboard",
            "بررسی کدها و اضافه کردن نمودار جدید",
            "تست بخش پروفایل کاربران و بهینه‌سازی"
        ]
        self.priority_labels = [
            "High", "High", "High", "High",
            "Low", "Low", "Low", "Low",
            "Medium", "Medium", "Medium", "Medium"
        ]
        
        self.estimation_texts = [
            "fix critical database server crash immediately", # 8.0 hours
            "urgent security patch for payment gateway",     # 6.0 hours
            "خطای شدید در سرور و دیتابیس اورژانسی",            # 7.5 hours
            "update documentation readme file",              # 1.0 hours
            "change UI button colors and styles",            # 1.5 hours
            "آپدیت فایل توضیحات و مستندات پروژه",              # 1.0 hours
            "review code pull request and write tests",      # 3.0 hours
            "add new feature chart to dashboard",            # 4.0 hours
            "بررسی کدها و اضافه کردن نمودار جدید",              # 3.5 hours
            "refactor entire authentication architecture",   # 12.0 hours
            "بازنویسی کامل معماری دیتابیس و امنیت"             # 10.0 hours
        ]
        self.estimation_targets = [8.0, 6.0, 7.5, 1.0, 1.5, 1.0, 3.0, 4.0, 3.5, 12.0, 10.0]

        self.vectorizer = TfidfVectorizer()
        self.priority_model = LogisticRegression()
        self.estimation_model = Ridge()
        
        self._train_models()

    def _train_models(self):
        X_p = self.vectorizer.fit_transform(self.priority_texts)
        self.priority_model.fit(X_p, self.priority_labels)
        
        X_e = self.vectorizer.transform(self.estimation_texts)
        self.estimation_model.fit(X_e, self.estimation_targets)

    def predict_priority(self, text: str) -> str:
        X_test = self.vectorizer.transform([text])
        return self.priority_model.predict(X_test)[0]

    def predict_estimation(self, text: str) -> float:
        X_test = self.vectorizer.transform([text])
        pred_hours = self.estimation_model.predict(X_test)[0]
        return float(round(max(1.0, pred_hours), 1))

    def check_duplicate(self, new_text: str, existing_texts: List[str]) -> Tuple[bool, str]:
        if not existing_texts:
            return False, ""
        
        all_texts = existing_texts + [new_text]
        tfidf_matrix = TfidfVectorizer().fit_transform(all_texts)
        similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]
        max_sim = max(similarities) if len(similarities) > 0 else 0.0
        
        if max_sim > 0.55:
            return True, f"⚠️ هشدار: شباهت زیاد ({int(max_sim*100)}%) با یک تسک موجود!"
        return False, ""

ai_engine = TaskAIEngine()