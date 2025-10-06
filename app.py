# -*- coding: utf-8 -*-
# ===========================================================
# AI-Deal-Checker – גרסת זהירות צרכנית מלאה עם הצלבה חכמה
# ===========================================================

import streamlit as st
import google.generativeai as genai
import json
from json_repair import repair_json
from PIL import Image
import traceback

# ---------- הגדרות כלליות ----------
st.set_page_config(page_title="AI Deal Checker 🚗", page_icon="🚗", layout="centered")

# קריאת מפתח API
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# שימוש במודל המתקדם ביותר
model = genai.GenerativeModel("gemini-2.5-pro")

# ---------- ממשק ----------
st.title("🚗 AI Deal Checker – בדיקת כדאיות חכמה")
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
                # ----- פרומפט -----
                prompt = f"""
אתה אנליסט מומחה לשוק הרכב הישראלי, המנתח מודעות יד שנייה באופן מקצועי, צרכני ומבוסס עובדות.

שלבי הניתוח:

🔹 **שלב 1 – ניתוח תוכן המודעה**
קרא את הטקסט הבא של המודעה:
\"\"\"{ad_text}\"\"\"
והפק ממנו את כל הנתונים הקיימים או המשתמעים: דגם, שנתון, מחיר, קילומטראז׳, סוג מנוע, יד, מצב תחזוקתי, בעלות, סגנון כתיבה וכו׳.
ציין במפורש אילו נתונים הופקו ישירות מהמודעה.

🔹 **שלב 2 – נתוני שוק חיצוניים**
חפש באינטרנט את הנתונים האובייקטיביים על הדגם והשנתון:
- מחיר שוק ממוצע בישראל
- אמינות הדגם ותקלות נפוצות
- צריכת דלק ועלויות תחזוקה ממוצעות
- ביקוש בשוק, זמינות חלקים וירידת ערך
- דירוג בטיחות אם קיים
ציין את הנתונים שמצאת.

🔹 **שלב 3 – הצלבה בין הנתונים**
השווה בין המידע שבמודעה למידע מהאינטרנט:
- האם המחיר המבוקש גבוה/נמוך/תואם למחיר השוק?
- האם הנתונים תואמים לאמינות ולביקוש בפועל?
- האם יש פערים משמעותיים או ניסוחים מטעים?
- האם הרכב מתאים לרוכש ממוצע מבחינת תחזוקה ועלויות?

🔹 **שלב 4 – שיקולי זהירות צרכנית (חובה לבדוק ולציין אם מתקיימים)**
אם אחד מהתרחישים הבאים מתקיים, יש להזהיר במפורש ולהוריד את הציון בהתאם:

1. מחיר נמוך מדי ביחס לשוק – ייתכן נזק או בעיה נסתרת.
2. רכב ישן עם אחזקה יקרה – מחיר מפתה אך הוצאות כבדות צפויות.
3. קילומטראז׳ גבוה (180,000 ק״מ ומעלה).
4. היעדר מידע על טיפולים או היסטוריית מוסך.
5. רכב ליסינג/חברה/השכרה – בלאי גבוה.
6. ניסוח עמום ("שמור מאוד", "מצב טוב" בלי פירוט).
7. צבע מוחלף או לא מקורי.
8. רכב טורבו ישן או דיזל עירוני – חשש לתקלות DPF וטורבו.
9. תוספות לא מקוריות או שיפורים ("צ׳יפ", "אגזוז", "שופר").
10. ביקוש נמוך מאוד – קושי במכירה חוזרת.
11. אין טסט בתוקף – חשש לרכב לא תקין.
12. מחיר גבוה לגרסה בסיסית – חוסר תמורה לכסף.
13. רכב חשמלי ישן – סיכון לסוללה חלשה.
14. בעלות לא ברורה או יד שלישית ומעלה – ירידת ערך.
15. היסטוריית תאונה / שלדה – הרכב מסוכן, הציון לא יעלה על 50.

בכל אחד מהמקרים – ציין זאת במפורש בניתוח והורד את הציון לפי חומרת הסיכון.

🔹 **שלב 5 – חישוב הציון**
חשב ציון סופי (0–100) לפי:
- התאמה בין מחיר מבוקש למחיר שוק – 25%
- התאמה בין מצב נטען למצב צפוי – 25%
- אמינות הדגם ועלויות תחזוקה – 20%
- גיל וקילומטראז׳ יחסית לממוצע – 15%
- אמינות המוכר – 10%
- ביקוש לדגם – 5%
אם קיימים סיכונים מהשלב הקודם, יש להוריד ציון בהתאם.

🔹 **שלב 6 – הפלט**
החזר אך ורק JSON תקני בפורמט הבא:
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
  "key_reasons": ["סיבה 1", "סיבה 2", "סיבה 3"],
  "user_info": {{
    "reliability_summary": "תיאור קצר על אמינות הדגם לפי מקורות ציבוריים",
    "maintenance_tips": ["טיפ 1", "טיפ 2"],
    "common_faults": ["תקלת אלקטרוניקה", "תיבת הילוכים רובוטית רגישה"],
    "market_context": "מידע כללי על הדגם – רמת ביקוש, זמינות חלקים, חוויית נהיגה"
  }}
}}
אל תכתוב שום טקסט לפני או אחרי ה־JSON.
"""

                # ----- קריאה למודל -----
                inputs = [prompt]
                for img in uploaded_images:
                    inputs.append(Image.open(img))

                response = model.generate_content(inputs, request_options={"timeout": 180})

                # תיקון JSON אוטומטי
                fixed_json = repair_json(response.text)
                data = json.loads(fixed_json)

                # ----- הצגת תוצאות -----
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

                # מידע מועשר למשתמש
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
                else:
                    st.info("לא סופק מידע נוסף על הדגם.")

                st.caption("© 2025 Car Advisor AI – AI-Deal-Checker | גרסה עם שיקולי זהירות צרכנית מלאים")

            except Exception as e:
                st.error("❌ שגיאה בעיבוד הפלט או בקריאת המידע מהמודל.")
                st.code(traceback.format_exc())
