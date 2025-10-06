# -*- coding: utf-8 -*-
# ===========================================================
# AI-Deal-Checker – Car Advisor AI Extension
# גרסה 2.1 – תומכת בלינקים חסומים (Yad2 / Facebook)
# ===========================================================

import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# ---------- הגדרות כלליות ----------
st.set_page_config(page_title="AI Deal Checker 🚗", page_icon="🚗", layout="centered")

# קריאת מפתח מ-secrets
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# המודל המתקדם ביותר של Gemini
model = genai.GenerativeModel("gemini-2.5-pro")

# ---------- כותרת ----------
st.title("🚗 AI Deal Checker – בדיקת כדאיות מודעת רכב")
st.write("הדבק קישור למודעה או העלה צילום מסך, והמערכת תחשב עבורך ציון אטרקטיביות חכם:")

# ---------- קלט ----------
url = st.text_input("🔗 הדבק כאן קישור למודעה (יד2, פייסבוק וכו׳):")
uploaded_image = st.file_uploader("📸 או העלה צילום מסך של המודעה:", type=["jpg", "jpeg", "png"])

# ---------- דיסקליימר ----------
st.markdown(
    """
    <div style='background-color:#fff3cd; border-radius:10px; padding:10px; border:1px solid #ffeeba;'>
    ⚠️ <b>הבהרה חשובה:</b> כלי זה מספק הערכה מבוססת בינה מלאכותית בלבד ואינו מהווה תחליף לבדיקה במכון מורשה.
    <br>יש לבקש מהמוכר היסטוריית טיפולים מלאה ולהוציא דו״ח עבר ביטוחי (למשל דרך <i>CarVertical</i> או <i>אוטודאטה</i>) לפני רכישה.
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- פעולה ----------
if st.button("חשב ציון כדאיות"):
    if not url and not uploaded_image:
        st.error("אנא הדבק קישור או העלה תמונה של המודעה.")
    else:
        with st.spinner("🔍 מנתח את הנתונים..."):

            prompt = f"""
אתה משמש כאנליסט מומחה לשוק הרכב הישראלי בתחום רכבים יד שנייה.
אם הקישור המצורף חסום או שלא נפתח, השתמש בתוכן הידוע עליו ממקורות פתוחים באינטרנט (למשל Yad2, יד2, CarGuru, מחירון לוי יצחק) כדי להעריך את הנתונים של הדגם.

נתון לך קישור או טקסט של מודעת רכב. עליך לנתח את העסקה ולחשב עד כמה היא אטרקטיבית מבחינת מחיר, תחזוקה, אמינות וביקוש בשוק.

קישור או תוכן המודעה:
{url if url else "ראה תמונה מצורפת"}

⚠️ חובה עליך להשתמש במידע זמין באינטרנט כדי לוודא שכל הנתונים מבוססים על עובדות אמיתיות:
- בדוק את המחירון המשוער של הדגם והשנתון בישראל.
- בדוק אם הדגם ידוע כאמין או בעייתי.
- בדוק אם יש בעיות תחזוקה מוכרות, עלויות טיפולים ממוצעות וביקוש בשוק.
- אם מידע חסר במודעה – השלם אותו מהאינטרנט.
- אם הנתונים במודעה נראים חשודים – ציין זאת בנימוקיך.

חשב ציון אטרקטיביות סופי (0–100) לפי:
מחיר ביחס לשוק (35%), קילומטראז׳ וגיל (20%), אמינות ותחזוקה (20%), איכות תיאור ותמונות (10%), אמינות המוכר (10%), ביקוש בשוק (5%).

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
אל תכתוב טקסט לפני או אחרי ה-JSON.
"""

            try:
                # הפעלת המודל עם timeout מוגדל
                if uploaded_image:
                    image = Image.open(uploaded_image)
                    response = model.generate_content(
                        [prompt, image],
                        request_options={"timeout": 120}
                    )
                else:
                    response = model.generate_content(
                        prompt,
                        request_options={"timeout": 120}
                    )

                # ניתוח פלט JSON
                data = json.loads(response.text)

                st.success(f"🚦 ציון כדאיות: {data['deal_score']}/100 — {data['classification']}")
                st.write("🧾 **סיכום:**", data["short_verdict"])
                st.write("🔍 **סיבות עיקריות:**")
                for r in data["key_reasons"]:
                    st.write(f"• {r}")

                st.divider()
                st.caption("© 2025 Car Advisor AI – AI-Deal-Checker | כל הזכויות שמורות.")
            except Exception as e:
                st.error("❌ לא הצלחנו לעבד את התוצאה. ייתכן שהמודעה חסומה או שהתוכן לא זמין כרגע.")
                st.caption("נסה שוב בעוד מספר שניות או העלה צילום מסך של המודעה.")
