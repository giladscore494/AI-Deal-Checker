# -*- coding: utf-8 -*-
# ===========================================================
# AI-Deal-Checker – גרסה יציבה להזנת טקסט ומספר תמונות
# ===========================================================

import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import traceback

# ---------- הגדרות ----------
st.set_page_config(page_title="AI Deal Checker 🚗", page_icon="🚗", layout="centered")

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-pro")

# ---------- ממשק ----------
st.title("🚗 AI Deal Checker – בדיקת כדאיות מודעת רכב")
st.write("העתק את כל טקסט המודעה (כולל מחיר, ק״מ, שנה, ועוד) והעלה כמה תמונות שתרצה לניתוח חכם של מצב הרכב:")

ad_text = st.text_area("📋 הדבק כאן את טקסט המודעה:", height=250)
uploaded_images = st.file_uploader(
    "📸 העלה תמונות של הרכב (ניתן לבחור כמה תמונות):",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

st.markdown(
    """
    <div style='background-color:#fff3cd; border-radius:10px; padding:10px; border:1px solid #ffeeba;'>
    ⚠️ <b>הבהרה חשובה:</b> כלי זה מספק הערכה מבוססת בינה מלאכותית בלבד ואינו מהווה תחליף לבדיקה במכון מורשה.
    <br>יש לבקש מהמוכר היסטוריית טיפולים מלאה ולהוציא דו״ח עבר ביטוחי לפני רכישה.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- פעולה ----------
if st.button("חשב ציון כדאיות"):
    if not ad_text.strip() and not uploaded_images:
        st.error("אנא הדבק טקסט או העלה לפחות תמונה אחת.")
    else:
        with st.spinner("🔍 מחשב את הציון..."):
            try:
                prompt = f"""
אתה אנליסט מומחה לשוק הרכב הישראלי.
קיבלנו את תיאור המודעה הבאה לרכב יד שנייה:

\"\"\"{ad_text}\"\"\"

אם צורפו תמונות, נתח אותן כדי לזהות מצב חיצוני, תחזוקה, ותיאום מול הנתונים בטקסט.
השתמש במידע מעודכן ממקורות ציבוריים (מחירונים, ביקוש בשוק, אמינות, תקלות ידועות) כדי לקבוע אם העסקה משתלמת.

חשב ציון אטרקטיביות סופי (0–100) לפי:
- מחיר ביחס לשוק (35%)
- קילומטראז׳ וגיל (20%)
- אמינות ותחזוקה (20%)
- איכות תיאור ותמונות (10%)
- אמינות המוכר (10%)
- ביקוש לדגם בשוק (5%)

החזר אך ורק JSON מדויק בפורמט הבא:
{{
  "brand": "",
  "model": "",
  "year": 0,
  "mileage_km": 0,
  "price_nis": 0,
  "market_estimate_nis": 0,
  "deal_score": 0,
  "classification": "עסקה מעולה" | "עסקה טובה" | "עסקה סבירה" | "יקרה מדי" | "מסוכנת",
  "short_verdict": "משפט קצר בעברית המסכם אם העסקה שווה את זה או לא",
  "key_reasons": ["סיבה 1", "סיבה 2", "סיבה 3"]
}}
אל תכתוב שום דבר מחוץ ל-JSON.
"""

                # יצירת רשימת קלט: פרומפט + כל התמונות
                inputs = [prompt]
                for img_file in uploaded_images:
                    img = Image.open(img_file)
                    inputs.append(img)

                response = model.generate_content(inputs, request_options={"timeout": 120})

                # ניקוי תווים בעייתיים
                raw = response.text.strip()
                raw = raw.replace('```json', '').replace('```', '').replace('\n', '').replace('\r', '')
                raw = raw.replace('\\"', '"').replace("”", '"').replace("“", '"')

                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    st.warning("בוצעה התאמה אוטומטית לפלט JSON לא תקין.")
                    fixed = raw[raw.find('{'):raw.rfind('}') + 1]
                    data = json.loads(fixed)

                # הצגת התוצאות
                st.success(f"🚦 ציון כדאיות: {data['deal_score']}/100 — {data['classification']}")
                st.write("🧾 **סיכום:**", data["short_verdict"])
                st.write("🔍 **סיבות עיקריות:**")
                for r in data["key_reasons"]:
                    st.write(f"• {r}")

                st.divider()
                st.caption("© 2025 Car Advisor AI – AI-Deal-Checker | גרסה עם תמונות מרובות")

            except Exception:
                st.error("❌ לא ניתן היה לעבד את הפלט.")
                st.code(traceback.format_exc())
