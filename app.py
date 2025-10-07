# -*- coding: utf-8 -*-
# ===========================================================
# AI Deal Checker – גרסה מלאה, יציבה ומסחרית (Gemini 2.5 Flash)
# Hybrid 70/30 + Learning + Market Correction + Full Prompt
# ===========================================================

import streamlit as st
import google.generativeai as genai
import json, os, traceback
from json_repair import repair_json
from PIL import Image
import pandas as pd
from datetime import datetime

# ---------- הגדרות כלליות ----------
st.set_page_config(page_title="🚗 AI Deal Checker", page_icon="🚗", layout="centered")

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

def calculate_rule_based_score(market_price, ad_price, mileage, year, is_taxi=False, private_owner=True):
    """חישוב קשיח לפי נוסחה מסחרית מדויקת"""
    try:
        score = 70
        if market_price and ad_price:
            deviation = (market_price - ad_price) / market_price
            score += deviation * 100 * 0.55  # משקל מחיר

        if mileage and mileage > 100_000:
            score -= (mileage - 100_000) / 10_000 * 1.5

        if is_taxi:
            score -= 25
        elif not private_owner:
            score -= 10

        age = datetime.now().year - year if year else 0
        if age > 5:
            score -= (age - 5) * 2

        return max(0, min(100, round(score)))
    except Exception:
        return 50

# ---------- ממשק ----------
st.title("🚗 AI Deal Checker – בדיקת כדאיות חכמה ולומדת")
st.write("הדבק טקסט של מודעת רכב יד 2 והעלה תמונות במידת הצורך, כדי לבדוק את כדאיות העסקה לעומק:")

ad_text = st.text_area("📋 הדבק כאן את טקסט המודעה:", height=250)
uploaded_images = st.file_uploader(
    "📸 העלה תמונות של הרכב (ניתן לבחור כמה):",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

st.markdown("""
<div style='background-color:#fff3cd;border-radius:10px;padding:10px;border:1px solid #ffeeba;'>
⚠️ <b>הבהרה:</b> הניתוח מבוסס בינה מלאכותית ואינו תחליף לבדיקה מקצועית.  
יש לבקש היסטוריית טיפולים מלאה ולהוציא דו״ח עבר ביטוחי לפני רכישה.
</div>
""", unsafe_allow_html=True)

# ---------- פעולה ----------
if st.button("חשב ציון כדאיות"):
    if not ad_text.strip() and not uploaded_images:
        st.error("אנא הדבק טקסט או העלה לפחות תמונה אחת.")
    else:
        with st.spinner("🔍 מבצע הצלבה חכמה בין נתוני המודעה לנתוני השוק..."):
            try:
                # ---------- פרומפט מלא ----------
                prompt = f"""
אתה אנליסט מומחה לשוק הרכב הישראלי. תפקידך להעריך את כדאיות העסקה של רכב משומש לפי טקסט המודעה והתמונות המצורפות.

עליך לפעול באופן אנליטי ומאוזן, ללא תנודתיות בין הרצות זהות, ולתת הערכה מדויקת ככל האפשר.

---

🔹 **שלב 1 – ניתוח טקסט המודעה**
קרא את הטקסט הבא:
\"\"\"{ad_text}\"\"\"
הפק את הנתונים הבאים: יצרן, דגם, גרסה, שנה, ק״מ, מחיר, סוג דלק, יד, בעלות, טסט, תקלות או שיפורים, אזור, הצהרות המוכר.

ציין במפורש מהם נתונים שהופקו ישירות מהמודעה, ומה חסר.

---

🔹 **שלב 2 – חיפוש נתוני שוק אמינים**
השלם מידע ממקורות ציבוריים מוכרים (כמו yad2, לוי יצחק, iCar, Edmunds, CarBuzz וכו׳):
- מחיר שוק ממוצע (₪)
- דירוג אמינות (0–100)
- עלות תחזוקה שנתית ממוצעת (₪)
- תקלות ידועות
- רמת ביקוש
- נתוני בטיחות

---

🔹 **שלב 3 – הצלבה לוגית**
השווה בין הנתונים שהמוכר מסר לבין נתוני השוק:
- האם המחיר נמוך, גבוה או תואם?
- האם הק״מ מתאים לשנה?
- האם חסרים פרטים חשובים?
- האם יש פערים לא הגיוניים?

---

🔹 **שלב 4 – שיקולי זהירות צרכנית**
הורד ציון במקרים:
- מחיר נמוך מ־15% מהשוק ללא סיבה.
- אין היסטוריית טיפולים.
- ק״מ מעל 180,000.
- יד 4 ומעלה.
- שלדה / צבע מוחלף.
- רכב ישן עם תחזוקה יקרה.
- תקלות ידועות בגיר / טורבו.
- רכב חשמלי ישן עם סוללה לא נבדקה.

---

🔹 **שלב 4.5 – איזון מקרי קצה (18 סיטואציות חובה)**
1. אל תוריד ציון על ק״מ גבוה אם יש טיפולים מוכחים.  
2. מחיר נמוך עד 10% = תקין.  
3. מחיר גבוה עד 15% = מוצדק אם רמת גימור גבוהה.  
4. ק״מ גבוה ברכבי שטח = תקין.  
5. רכבי נישה (Abarth, Mini, GTI, MX-5) לא נמדדים לפי ביקוש.  
6. ניסוחים רשלניים לא בהכרח חשודים.  
7. מודעה קצרה → השלם מידע חסר מהשוק.  
8. מחיר נמוך ב־50% → ייתכן רכב מושבת / הונאה.  
9. יבוא אישי = אל תשווה לשוק רגיל.  
10. רכב אספנות = גיל לא חיסרון.  
11. רכב סוחר = הפחת אמינות.  
12. “מחיר סופי” או “מכירה מהירה” לא בהכרח חשד.  
13. צבע חריג מקורי = לא חיסרון.  
14. אין ק״מ במודעה → הערך ממוצע 18K לשנה.  
15. אזור לח (אשדוד, אילת) → סיכון חלודה קל.  
16. חסר מחיר → הערך לפי טווח מודעות דומות.  
17. ליסינג שטופל = תקין.  
18. ניסוחים בשפה זרה → התייחס רק לנתונים אמינים.

---

🔹 **שלב 5 – חישוב הציון (0–100)**
שקלול מלא:
- מחיר מול שוק – 25%
- תחזוקה ומצב כללי – 25%
- אמינות דגם – 20%
- גיל וק״מ – 15%
- אמינות מוכר – 10%
- ביקוש – 5%

---

🔹 **שלב 6 – פלט JSON**
החזר אך ורק JSON תקני בפורמט הבא:
{{
  "from_ad": {{
    "brand": "",
    "model": "",
    "year": 0,
    "mileage_km": 0,
    "price_nis": 0,
    "is_taxi": false,
    "is_private": true,
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
  "ai_confidence": 0.0,
  "user_info": {{
    "reliability_summary": "",
    "common_faults": [],
    "maintenance_tips": [],
    "market_context": ""
  }}
}}

---

🔹 **שלב 7 – תיקון למידה**
אם יש נתוני היסטוריה על הדגם – השווה את הציון לממוצע ההיסטורי.
אם יש הבדל של מעל 15 נק׳, בצע תיקון מתון לכיוון הממוצע.
"""

                # ---------- קריאה למודל ----------
                inputs = [prompt]
                for img in uploaded_images:
                    inputs.append(Image.open(img))

                response = model.generate_content(inputs, request_options={"timeout": 120})
                fixed_json = repair_json(response.text)
                data = json.loads(fixed_json)

                # ---------- Hybrid 70/30 ----------
                rule_score = calculate_rule_based_score(
                    data["from_internet"]["market_estimate_nis"],
                    data["from_ad"]["price_nis"],
                    data["from_ad"]["mileage_km"],
                    data["from_ad"]["year"],
                    is_taxi=data["from_ad"].get("is_taxi", False),
                    private_owner=data["from_ad"].get("is_private", True)
                )

                ai_score = data["deal_score"]
                ai_confidence = data.get("ai_confidence", 0.8)
                final_score = round((rule_score * 0.7) + (ai_score * 0.3))

                data["rule_score"] = rule_score
                data["ai_score"] = ai_score
                data["deal_score"] = final_score
                data["ai_confidence"] = ai_confidence

                # ---------- תיקון ממוצע היסטורי ----------
                avg = get_model_avg(data["from_ad"]["brand"], data["from_ad"]["model"])
                if avg:
                    diff = final_score - avg
                    if abs(diff) >= 15:
                        correction = -diff * 0.5
                        data["deal_score"] = int(final_score + correction)
                        data["short_verdict"] += f" ⚙️ (תיקון קל לפי ממוצע היסטורי: {avg})"

                save_to_history(data)

                # ---------- תצוגה ----------
                score = data["deal_score"]
                if score >= 80: color = "#28a745"
                elif score >= 60: color = "#ffc107"
                else: color = "#dc3545"

                st.markdown(f"<h3 style='color:{color}'>🚦 ציון כדאיות כולל: {score}/100 — {data['classification']}</h3>", unsafe_allow_html=True)
                st.write(f"**AI:** {ai_score} ({int(ai_confidence*100)}% ביטחון) | **קוד:** {rule_score}")
                st.divider()

                st.write("🧾 **סיכום:**", data["short_verdict"])
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

                st.caption("© 2025 Car Advisor AI – גרסה מסחרית מלאה • Gemini 2.5 Flash • Hybrid 70/30")

            except Exception as e:
                st.error("❌ שגיאה בעיבוד הפלט או בקריאת המידע מהמודל.")
                st.code(traceback.format_exc())