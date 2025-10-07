# -*- coding: utf-8 -*-
# ===========================================================
# AI-Deal-Checker – גרסה לומדת עם תיקון עקביות (Gemini 2.5 Flash)
# כולל שלבים 1–7, מקרי קצה, תיקון JSON וגרף מגמה
# ===========================================================

import streamlit as st
import google.generativeai as genai
import json, os, traceback
from json_repair import repair_json
from PIL import Image
import pandas as pd

# ---------- הגדרות כלליות ----------
st.set_page_config(page_title="AI Deal Checker 🚗", page_icon="🚗", layout="centered")

API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

HISTORY_FILE = "data_history.json"
STABILITY_DIFF_THRESHOLD = 12  # פער נקודות שמפעיל אזהרת עקביות

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
                # מפתח מודעה ייחודי
                temp_key = ad_text.strip()[:80].lower().replace(" ", "_")

                # --- בדיקת עקביות בין ציונים קודמים ---
                history = load_history()
                recent_entries = [
                    {"score": h["deal_score"], "classification": h.get("classification", "לא צוין")}
                    for h in history if h.get("_ad_key") == temp_key
                ]
                recent_scores = [r["score"] for r in recent_entries]

                if len(recent_scores) >= 2:
                    avg_prev = round(sum(recent_scores) / len(recent_scores), 1)
                    diff = max(recent_scores) - min(recent_scores)
                    if diff > STABILITY_DIFF_THRESHOLD:
                        consistency_note = f"""
                        📊 בבדיקות קודמות לאותו רכב התקבלו תוצאות שונות:
                        {json.dumps(recent_entries, ensure_ascii=False, indent=2)}
                        הממוצע ההיסטורי עומד על כ-{avg_prev} נק׳.
                        אנא הפעם היה עקבי וחשב ציון מאוזן, קרוב לממוצע ההיסטורי.
                        שמור על ציון בתחום {avg_prev - 5:.0f}–{avg_prev + 5:.0f} אלא אם קיימים נתונים חדשים לחלוטין.
                        """
                    else:
                        consistency_note = ""
                else:
                    consistency_note = ""

                # ---------- פרומפט מלא ----------
                prompt = f"""
אתה אנליסט מומחה לשוק הרכב הישראלי. עליך להעריך את כדאיות העסקה של רכב משומש לפי טקסט המודעה והתמונות המצורפות.

{consistency_note}

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

🔹 **שלב 4 – שיקולי זהירות צרכנית**
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

🔹 **שלב 4.5 – מקרי קצה**
1. ק״מ מעט גבוה ≠ שלילה אם יש היסטוריית טיפולים.  
2. מחיר נמוך עד 10% ≠ חשוד.  
3. מחיר גבוה מוצדק אם רמת גימור גבוהה.  
4. רכבי נישה (Abarth, Mini, GTI) נמדדים לפי תחזוקה ולא ביקוש.  
5. אזור חוף = שקול לסיכון חלודה.  
6. מחיר נמוך ב־50% → חשד לרכב מושבת.  
7. סוחר → הפחת אמינות.  
8. “מחיר סופי” ≠ בעיה.  
9. רכב אספנות ≠ שלילה.  
10. אין ק״מ = הערך ממוצע.  
11. יד ראשונה ליסינג שטופלה = תקין.  
12. טורבו ישן = סיכון.  
13. חסר מחיר = הערך לפי טווח.  
14. ניסוחים רשלניים ≠ בהכרח בעיה.  
15. נתונים מהתמונות גוברים על טקסט המודעה.

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
החזר JSON תקני בלבד:
{{
  "from_ad": {{"brand":"", "model":"", "year":0, "mileage_km":0, "price_nis":0, "ad_claims":[]}},
  "from_internet": {{"market_estimate_nis":0, "reliability_score":0, "avg_maintenance_cost":0, "demand_level":"", "known_issues":[]}},
  "cross_analysis": {{"price_alignment":"", "condition_alignment":"", "key_differences":[]}},
  "deal_score":0,
  "classification":"",
  "short_verdict":"",
  "key_reasons":[],
  "user_info": {{"reliability_summary":"", "maintenance_tips":[], "common_faults":[], "market_context":""}}
}}

---

🔹 **שלב 7 – למידת דפוסים מצטברים**
אם הציון שונה ביותר מ־15 נק׳ מהממוצע ההיסטורי של הדגם → בצע תיקון קל כלפי הממוצע.
"""

                # ---------- קריאה למודל ----------
                inputs = [prompt]
                for img in uploaded_images:
                    inputs.append(Image.open(img))

                response = model.generate_content(inputs, request_options={"timeout": 120})
                fixed_json = repair_json(response.text)
                data = json.loads(fixed_json)
                data["_ad_key"] = temp_key  # שמירת מזהה מודעה

                # ---------- תיקון שוק ----------
                avg = get_model_avg(data["from_ad"]["brand"], data["from_ad"]["model"])
                if avg:
                    diff = data["deal_score"] - avg
                    if abs(diff) >= 15:
                        correction = -diff * 0.5
                        data["deal_score"] = int(data["deal_score"] + correction)
                        data["short_verdict"] += f" ⚙️ (בוצע תיקון קל לפי ממוצע היסטורי: {avg})"

                save_to_history(data)

                # ---------- תצוגה ----------
                score = data["deal_score"]
                color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"

                st.markdown(f"<h3 style='color:{color}'>🚦 ציון כדאיות כולל: {score}/100 — {data['classification']}</h3>", unsafe_allow_html=True)
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
                        for f in info["common_faults"]: st.write(f"• {f}")
                    if info.get("maintenance_tips"):
                        st.write("**טיפים לתחזוקה:**")
                        for tip in info["maintenance_tips"]: st.write(f"• {tip}")
                    if info.get("market_context"):
                        st.write("**הקשר שוק כללי:**", info["market_context"])

                # גרף מגמה
                model_entries = [h for h in history if h.get("_ad_key") == temp_key]
                if len(model_entries) >= 2:
                    df = pd.DataFrame([{"Index": i + 1, "Score": h["deal_score"]} for i, h in enumerate(model_entries)])
                    st.line_chart(df.set_index("Index"), height=200)
                    st.caption("📈 מגמת ציונים היסטורית למודעה זו")

                st.caption("© 2025 Car Advisor AI – גרסה עם תיקון עקביות וסיווגים היסטוריים")

            except Exception as e:
                st.error("❌ שגיאה בעיבוד הפלט או בקריאת המידע מהמודל.")
                st.code(traceback.format_exc())