# -*- coding: utf-8 -*-
# ===========================================================
# AI-Deal-Checker – גרסה לומדת (Gemini 2.5 Flash)
# כולל שלבים 1–7, 18 מקרי קצה, תיקון JSON וגרף מגמה
# ===========================================================

import streamlit as st
import google.generativeai as genai
import json, os
from json_repair import repair_json
from PIL import Image
import traceback
import pandas as pd

# ---------- הגדרות כלליות ----------
st.set_page_config(page_title="AI Deal Checker 🚗", page_icon="🚗", layout="centered")

# ---------- חיבור למודל ----------
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.5-flash")

HISTORY_FILE = "data_history.json"

# ---------- פונקציות עזר ----------
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_to_history(new_entry):
    history = load_history()
    history.append(new_entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_model_avg(brand, model_name):
    history = load_history()
    scores = [
        h["deal_score"] for h in history
        if h["from_ad"].get("brand") == brand and model_name in h["from_ad"].get("model", "")
    ]
    return round(sum(scores) / len(scores), 2) if scores else None

# ---------- ממשק ----------
st.title("🚗 AI Deal Checker – בדיקת כדאיות חכמה ולומדת")
st.write("העתק את טקסט המודעה (כולל מחיר, שנה, ק״מ וכו׳) והעלה תמונות של הרכב לביצוע הצלבה בין נתוני המודעה לנתוני השוק בפועל:")

ad_text = st.text_area("📋 הדבק כאן את טקסט המודעה:", height=250)
uploaded_images = st.file_uploader(
    "📸 העלה תמונות של הרכב (ניתן לבחור כמה):",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

st.markdown(
    """
    <div style='background-color:#fff3cd; border-radius:10px; padding:10px; border:1px solid #ffeeba;'>
    ⚠️ <b>הבהרה:</b> ניתוח זה מבוסס בינה מלאכותית ואינו תחליף לבדיקה מקצועית.
    יש לבקש היסטוריית טיפולים מלאה ולהוציא דו״ח עבר ביטוחי לפני רכישה.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- פעולה ----------
if st.button("חשב ציון כדאיות"):
    if not ad_text.strip() and not uploaded_images:
        st.error("אנא הדבק טקסט או העלה לפחות תמונה אחת.")
    else:
        with st.spinner("🔍 מבצע הצלבה חכמה בין נתוני המודעה לנתוני השוק..."):
            try:
                # ---------- פרומפט מלא ----------
                prompt = f"""
אתה אנליסט מומחה לשוק הרכב הישראלי. עליך להעריך את כדאיות העסקה של רכב משומש לפי טקסט המודעה והתמונות המצורפות.

עליך לספק הערכה **מדויקת, מאוזנת ומבוססת עובדות** — לא אופטימית מדי ולא זהירה מדי.

---

🔹 **שלב 1 – ניתוח תוכן המודעה**
קרא את המודעה:
\"\"\"{ad_text}\"\"\"
הפק ממנה את כל הנתונים (יצרן, דגם, גרסה, שנה, מחיר, ק״מ, דלק, יד, אזור, טסט, היסטוריית טיפולים, תקלות וכו׳)
וציין אילו מהם הופקו ישירות מהמודעה.

---

🔹 **שלב 2 – נתוני שוק חיצוניים**
מצא מידע עדכני באינטרנט על הדגם:
- מחיר שוק ממוצע
- דירוג אמינות
- עלויות תחזוקה
- תקלות ידועות
- ביקוש
- בטיחות

---

🔹 **שלב 3 – הצלבה**
השווה בין הנתונים מהמודעה לנתוני השוק. ציין פערים, בעיות או יתרונות.

---

🔹 **שלב 4 – שיקולי זהירות צרכנית (איזון ריאלי)**
בצע הורדת ציון רק אם קיימים סימני סיכון אמיתיים:
- מחיר נמוך ב־15%+ ללא סיבה
- אין היסטוריית טיפולים
- ק״מ מעל 180K
- יד מרובה (4+)
- צבע מוחלף / שלדה
- רכב ליסינג לא מטופל
- טורבו ישן ולא מתוחזק
- רכב ישן עם תחזוקה יקרה
- בעיות גיר ידועות
- רכב חשמלי ישן עם סוללה לא נבדקה

---

🔹 **שלב 4.5 – מקרי קצה (18 תרחישים שיש לאזן נכון)**
1. אל תוריד ציון על ק״מ מעט גבוה אם יש היסטוריית טיפולים.  
2. מחיר נמוך עד 10% אינו חשוד.  
3. מחיר גבוה ב־15% מוצדק אם גרסה מאובזרת.  
4. קילומטראז׳ גבוה ברכבי שטח תקין.  
5. רכבי נישה (Abarth, Mini, GTI, MX-5) לא נמדדים לפי ביקוש.  
6. ניסוחים רשלניים לא מעידים על בעיה.  
7. מודעה קצרה = השלם מידע מהאינטרנט.  
8. מחיר נמוך ב־50% = חשד להשבתה.  
9. רכב “יבוא אישי” = אל תשווה לשוק רגיל.  
10. רכב אספנות = גיל לא חיסרון.  
11. רכב סוחר = הפחת אמינות.  
12. “מחיר סופי” או “מכירה מהירה” לא בהכרח חשוד.  
13. צבע חריג אינו שלילה אם מקורי.  
14. אין ק״מ במודעה – הערך ממוצע.  
15. אזור לח (אשדוד, אילת) → סכנת חלודה.  
16. חסר מחיר – הערך לפי טווח דגם.  
17. יד ראשונה מליסינג שטופל = תקין.  
18. ניסוחים בשפה זרה → הסתמך רק על נתונים.

---

🔹 **שלב 5 – נוסחת ציון (0–100)**
- מחיר מול שוק – 25%
- תחזוקה ומצב – 25%
- אמינות דגם – 20%
- גיל וק״מ – 15%
- אמינות מוכר – 10%
- ביקוש – 5%

---

🔹 **שלב 6 – הפלט**
החזר **אך ורק JSON תקני** בפורמט הבא:
{{
  "from_ad": {{
    "brand": "",
    "model": "",
    "year": 0,
    "mileage_km": 0,
    "price_nis": 0,
    "ad_claims": []
  }},
  "from_internet": {{
    "market_estimate_nis": 0,
    "reliability_score": 0,
    "avg_maintenance_cost": 0,
    "demand_level": "נמוך" | "בינוני" | "גבוה",
    "known_issues": []
  }},
  "cross_analysis": {{
    "price_alignment": "גבוה" | "נמוך" | "סביר",
    "condition_alignment": "תואם" | "לא תואם",
    "key_differences": []
  }},
  "deal_score": 0,
  "classification": "עסקה מעולה" | "עסקה טובה" | "עסקה סבירה" | "יקרה מדי" | "מסוכנת",
  "short_verdict": "",
  "key_reasons": [],
  "user_info": {{
    "reliability_summary": "",
    "maintenance_tips": [],
    "common_faults": [],
    "market_context": ""
  }}
}}

---

🔹 **שלב 7 – למידת דפוסים מצטברים**
אם יש נתוני היסטוריה על דגם זה (נשלחים בנפרד), השווה את הציון לממוצע ההיסטורי:
- אם הציון שונה ביותר מ־15 נק׳ → בצע תיקון קל כלפי הממוצע.
- אל תשנה טקסט, רק את הערך המספרי של הציון.
"""

                # ---------- קריאה למודל ----------
                inputs = [prompt]
                for img in uploaded_images:
                    inputs.append(Image.open(img))

                response = model.generate_content(inputs, request_options={"timeout": 120})
                fixed_json = repair_json(response.text)
                data = json.loads(fixed_json)

                # ---------- שלב 7 – תיקון שוק ----------
                avg = get_model_avg(data["from_ad"]["brand"], data["from_ad"]["model"])
                if avg:
                    diff = data["deal_score"] - avg
                    if abs(diff) >= 15:
                        correction = -diff * 0.5
                        data["deal_score"] = int(data["deal_score"] + correction)
                        data["short_verdict"] += f" ⚙️ (בוצע תיקון קל לפי ממוצע היסטורי: {avg})"

                # שמירה להיסטוריה
                save_to_history(data)

                # ---------- תצוגה ----------
                score = data["deal_score"]
                if score >= 80: color = "#28a745"
                elif score >= 60: color = "#ffc107"
                else: color = "#dc3545"

                st.markdown(
                    f"<h3 style='color:{color}'>🚦 ציון כדאיות כולל: {score}/100 — {data['classification']}</h3>",
                    unsafe_allow_html=True
                )
                st.write("🧾 **סיכום:**", data["short_verdict"])
                st.divider()

                st.subheader("📋 נתונים מתוך המודעה:")
                st.json(data["from_ad"])

                st.subheader("🌍 נתוני שוק שנמצאו באינטרנט:")
                st.json(data["from_internet"])

                st.subheader("🔍 הצלבה וניתוח פערים:")
                st.json(data["cross_analysis"])

                st.subheader("🧠 סיבות עיקריות לציון:")
                for r in data["key_reasons"]:
                    st.write(f"• {r}")

                st.divider()
                st.subheader("📚 מידע נוסף למשתמש")
                info = data.get("user_info", {})
                if info:
                    st.write(f"**אמינות הדגם:** {info.get('reliability_summary', 'לא צוין')}")
                    if info.get("common_faults"):
                        st.write("**תקלות נפוצות:**")
                        for f in info["common_faults"]:
                            st.write(f"• {f}")
                    if info.get("maintenance_tips"):
                        st.write("**טיפים לתחזוקה:**")
                        for tip in info["maintenance_tips"]:
                            st.write(f"• {tip}")
                    if info.get("market_context"):
                        st.write("**הקשר שוק כללי:**", info["market_context"])

                # ---------- גרף מגמה ----------
                history = load_history()
                model_entries = [
                    h for h in history
                    if h["from_ad"]["brand"] == data["from_ad"]["brand"]
                    and data["from_ad"]["model"] in h["from_ad"]["model"]
                ]
                if len(model_entries) >= 2:
                    df = pd.DataFrame([
                        {"Index": i + 1, "Score": h["deal_score"]}
                        for i, h in enumerate(model_entries)
                    ])
                    st.line_chart(df.set_index("Index"), height=200)
                    st.caption("📈 מגמת ציונים היסטורית לדגם זה")

                st.caption("© 2025 Car Advisor AI – גרסה לומדת עם תיקון שוק ומקרי קצה מלאים")

            except Exception as e:
                st.error("❌ שגיאה בעיבוד הפלט או בקריאת המידע מהמודל.")
                st.code(traceback.format_exc())
