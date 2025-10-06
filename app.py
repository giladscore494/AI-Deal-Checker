# -*- coding: utf-8 -*-
# ===========================================================
# AI-Deal-Checker – גרסה 2.5 Flash מאוזנת עם הצלבה חכמה
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

# שימוש במודל Gemini 2.5 Flash
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------- ממשק ----------
st.title("🚗 AI Deal Checker – בדיקת כדאיות חכמה ומאוזנת")
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
אתה אנליסט מומחה לשוק הרכב הישראלי. מטרתך היא לבצע הערכת כדאיות כוללת לרכב משומש
על בסיס טקסט המודעה (שצורף למטה) והתמונות, תוך הצלבה עם נתוני שוק עדכניים ומידע אמינות.

ההערכה שלך חייבת להיות מדויקת, שקולה ומבוססת על עובדות – לא על זהירות יתר.

---

🔹 **שלב 1 – ניתוח תוכן המודעה**
קרא בעיון את הטקסט הבא של המודעה:
\"\"\"{ad_text}\"\"\"
הפק ממנו את הנתונים האפשריים:
יצרן, דגם, גרסה, מחיר, קילומטראז׳, שנה, תיבת הילוכים, סוג מנוע, רמת גימור, יד, צבע, אזור, היסטוריית טיפולים, טסט, בעלות נוכחית וקודמת, מצב כללי, ועוד.
ציין במפורש אילו נתונים הופקו ישירות מהמודעה.

---

🔹 **שלב 2 – נתוני שוק חיצוניים**
חפש באינטרנט מידע על הדגם והשנה:
- מחיר שוק ממוצע (יד 2 / לוי יצחק)
- דירוג אמינות ותחזוקה
- עלויות טיפולים שנתיות
- תקלות ידועות או נקודות חולשה
- ביקוש בשוק, שמירת ערך וזמינות חלקים
- דירוג בטיחות

---

🔹 **שלב 3 – השוואה והצלבה**
השווה בין הנתונים מהמודעה לבין המידע מהשוק:
- האם המחיר המבוקש גבוה, נמוך או תואם?
- האם מצב הרכב במודעה תואם למה שצפוי לפי גיל וק״מ?
- האם יש ניסוחים בעייתיים או הסתרת מידע?

---

🔹 **שלב 4 – שיקולי זהירות צרכנית**
עליך להוריד ציון רק אם מתקיימים תנאים ברורים של סיכון, לפי הכללים הבאים:

✅ **איזון מחיר:**
- אם המחיר נמוך עד 10% ממחיר השוק ואין סימני בעיה (תאונות, ניסוחים מעורפלים, רכב מוזנח) — זה נחשב דיל טוב, אל תוריד ציון.
- אם המחיר נמוך ביותר מ־15% ללא הסבר הגיוני — זה חריג ודורש הורדת ציון.
- אם המחיר גבוה מהשוק ביותר מ־10% ללא הצדקה (גימור, אבזור) — הורד מעט ציון.

✅ **איזון ידיים:**
- רכב בן 5–7 שנים עם יד 3–4 = מצב סביר, לא סיכון.
- רק מעל יד 4, או תדירות מכירה גבוהה (3 ידיים ב־4 שנים), נחשב חריג.

✅ **התרחישים שבהם חובה להזהיר או להוריד ציון:**
1. מחיר נמוך מדי ביחס לשוק (15%+).
2. רכב ישן עם אחזקה יקרה.
3. קילומטראז׳ גבוה (180,000+ ק"מ).
4. אין היסטוריית טיפולים.
5. רכב ליסינג/חברה או השכרה.
6. ניסוח עמום ("מצב טוב מאוד") ללא הוכחות.
7. צבע מוחלף או ציון של פחחות.
8. מנוע טורבו או דיזל ישן.
9. רכב משופר (צ׳יפ, אגזוז וכו׳).
10. ביקוש נמוך בשוק.
11. אין טסט בתוקף.
12. מחיר גבוה לגרסה בסיסית.
13. רכב חשמלי ישן עם סוללה לא נבדקה.
14. בעלות לא ברורה או יד מרובה יחסית לגיל.
15. תאונה/פגיעה בשלדה — ציון לא יעבור 50.

---

🔹 **שלב 5 – חישוב ציון סופי**
חשב את הציון (0–100) לפי המשקלות:
- מחיר מול שוק – 25%
- מצב תחזוקתי ומכאני – 25%
- אמינות דגם – 20%
- גיל וקילומטראז׳ – 15%
- אמינות מוכר – 10%
- ביקוש לדגם – 5%

---

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
    "market_context": "מידע כללי על הדגם – ביקוש, חלקים, חוויית נהיגה"
  }}
}}
אל תכתוב שום טקסט לפני או אחרי ה־JSON.
"""

                # ----- קריאה למודל -----
                inputs = [prompt]
                for img in uploaded_images:
                    inputs.append(Image.open(img))

                response = model.generate_content(inputs, request_options={"timeout": 120})

                # תיקון JSON אוטומטי
                fixed_json = repair_json(response.text)
                data = json.loads(fixed_json)

                # ----- הצגת תוצאות -----
                score = data["deal_score"]
                if score >= 80:
                    color = "#28a745"
                elif score >= 60:
                    color = "#ffc107"
                else:
                    color = "#dc3545"

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

                # מידע נוסף למשתמש
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

                st.caption("© 2025 Car Advisor AI – AI-Deal-Checker | גרסת Gemini 2.5 Flash מאוזנת")

            except Exception as e:
                st.error("❌ שגיאה בעיבוד הפלט או בקריאת המידע מהמודל.")
                st.code(traceback.format_exc())
