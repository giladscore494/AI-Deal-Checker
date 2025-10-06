# -*- coding: utf-8 -*-
# ===========================================================
# AI-Deal-Checker – גרסת הצלבה חכמה: מודעה + נתוני שוק
# ===========================================================

import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import traceback

# ---------- הגדרות כלליות ----------
st.set_page_config(page_title="AI Deal Checker 🚗", page_icon="🚗", layout="centered")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-pro")

# ---------- ממשק ----------
st.title("🚗 AI Deal Checker – בדיקת כדאיות חכמה")
st.write("העתק את טקסט המודעה (כולל מחיר, שנה, ק״מ וכו׳) והעלה תמונות של הרכב לביצוע הצלבה בין הנתונים במודעה לנתונים האמיתיים מהאינטרנט:")

ad_text = st.text_area("📋 הדבק כאן את טקסט המודעה:", height=250)
uploaded_images = st.file_uploader(
    "📸 העלה תמונות של הרכב (ניתן לבחור כמה):",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

st.markdown(
    """
    <div style='background-color:#fff3cd; border-radius:10px; padding:10px; border:1px solid #ffeeba;'>
    ⚠️ <b>הבהרה חשובה:</b> זהו ניתוח חכם אך אינו מהווה תחליף לבדיקה במכון מורשה.
    <br>יש לבקש היסטוריית טיפולים מלאה ולהוציא דו״ח עבר ביטוחי לפני רכישה.
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
                prompt = f"""
אתה אנליסט מומחה לשוק הרכב הישראלי, המנתח מודעות יד שנייה באופן מקצועי ומבוסס עובדות.

🔹 **שלב 1 – ניתוח תוכן המודעה**
קרא את הטקסט הבא של המודעה:
\"\"\"{ad_text}\"\"\"
והפק ממנו את כל הנתונים הקיימים או המשתמעים: דגם, שנתון, מחיר, קילומטראז׳, סוג מנוע, יד, מצב תחזוקתי, בעלות, סגנון כתיבה וכו׳.
ציין במפורש אילו נתונים הופקו ישירות מהמודעה.

🔹 **שלב 2 – נתוני שוק חיצוניים**
חפש באינטרנט את הנתונים האובייקטיביים על הדגם והשנתון שנמצאו:
- מחיר שוק ממוצע בישראל
- אמינות הדגם ותקלות נפוצות
- צריכת דלק ועלויות תחזוקה ממוצעות
- ביקוש בשוק, זמינות חלקים וירידת ערך
- דירוג בטיחות אם רלוונטי
ציין את הנתונים שמצאת.

🔹 **שלב 3 – הצלבה בין הנתונים**
השווה בין המידע שבמודעה למידע מהאינטרנט:
- האם המחיר המבוקש גבוה/נמוך/תואם למחיר השוק?
- האם הנתונים תואמים לאמינות ולביקוש בפועל?
- האם תיאורי המוכר נראים אמינים לפי הנתונים?
- האם יש פערים מובהקים?

🔹 **שלב 4 – חישוב הציון**
חשב ציון סופי (0–100) לפי:
- התאמה בין מחיר מבוקש למחיר שוק – 25%
- התאמה בין מצב נטען למצב הצפוי – 25%
- אמינות הדגם ועלויות תחזוקה – 20%
- גיל וקילומטראז׳ יחסית לממוצע – 15%
- אמינות המוכר – 10%
- ביקוש לדגם – 5%

🔹 **שלב 5 – הפלט**
החזר אך ורק JSON מדויק בפורמט:
{{
  "from_ad": {{
    "brand": "",
    "model": "",
    "year": 0,
    "mileage_km": 0,
    "price_nis": 0,
    "ad_claims": ["פרט 1", "פרט 2"]
  }},
  "from_internet": {{
    "market_estimate_nis": 0,
    "reliability_score": 0,
    "avg_maintenance_cost": 0,
    "demand_level": "נמוך" | "בינוני" | "גבוה",
    "known_issues": ["בעיה 1", "בעיה 2"]
  }},
  "cross_analysis": {{
    "price_alignment": "גבוה" | "נמוך" | "סביר",
    "condition_alignment": "תואם" | "לא תואם",
    "key_differences": ["פער 1", "פער 2"]
  }},
  "deal_score": 0,
  "classification": "עסקה מעולה" | "עסקה טובה" | "עסקה סבירה" | "יקרה מדי" | "מסוכנת",
  "short_verdict": "סיכום אנליטי קצר בעברית",
  "key_reasons": ["סיבה 1", "סיבה 2", "סיבה 3"]
}}
אל תכתוב טקסט נוסף מחוץ ל-JSON.
הציון חייב לשקף הצלבה אמיתית בין נתוני המודעה לנתוני השוק האובייקטיביים.
"""

                # קלט משולב של טקסט ותמונות
                inputs = [prompt]
                for img in uploaded_images:
                    inputs.append(Image.open(img))

                response = model.generate_content(inputs, request_options={"timeout": 180})

                # ניקוי פלט
                raw = response.text.strip()
                for token in ['```json', '```', '\n', '\r']:
                    raw = raw.replace(token, '')
                raw = raw.replace('\\"', '"').replace("”", '"').replace("“", '"')

                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    st.warning("בוצעה התאמה אוטומטית לפלט JSON לא תקין.")
                    fixed = raw[raw.find('{'):raw.rfind('}') + 1]
                    data = json.loads(fixed)

                # ---------- הצגת תוצאות ----------
                st.subheader(f"🚦 ציון כדאיות כולל: {data['deal_score']}/100 — {data['classification']}")
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

                st.caption("© 2025 Car Advisor AI – AI-Deal-Checker | גרסת הצלבה חכמה")

            except Exception:
                st.error("❌ לא ניתן היה לעבד את הפלט.")
                st.code(traceback.format_exc())
