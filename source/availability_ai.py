"""רכיב בינה מלאכותית לקליטת זמינות מאמנות בשפה טבעית.

מודול זה מהווה גשר בין טקסט חופשי ולא מובנה של מאמנת לבין משבצות זמן מובנות,
באמצעות קריאה למודל השפה gpt-5.6-luna דרך ה-Chat Completions API של OpenAI.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

try:
    from source.models import DAYS, PARTS_OF_DAY, TimeSlot
except ImportError:
    from models import DAYS, PARTS_OF_DAY, TimeSlot

# טעינת מפתח ה-API מתוך קובץ .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

MODEL: str = "gpt-5.6-luna"

DEVELOPER_INSTRUCTIONS: str = f"""אתה מנוע AI למערכת ניהול ושיבוץ במכון כושר.
תפקידך: לפענח הודעות זמינות בשפה חופשית שנכתבו על ידי מאמנות, ולחלץ מתוכן רשימה מובנית של משבצות זמן שבהן המאמנת זמינה לאמן.

1. רשימת ימים תקינים:
{', '.join(DAYS)}

2. רשימת חלקי יום תקינים:
{', '.join(PARTS_OF_DAY)}

3. כלל מנחה ליום ללא ציון חלק ביום:
אם המאמנת מציינת יום ללא פירוט חלק ביום (למשל: "זמינה ברביעי", "פנויה בראשון"), יש לכלול את כל חלקי אותו יום: בוקר, צהריים, ערב.

4. פורמט הפלט:
עליך להחזיר אך ורק אובייקט JSON תקין במבנה הבא:
{{"slots": [{{"day": "<שם_יום>", "part": "<חלק_ביום>"}}]}}

אם ההודעה אינה מכילה מידע על זמינות או שלא ניתן לפענח ימים, החזר:
{{"slots": []}}
"""

FEW_SHOT_EXAMPLES: list[dict[str, str]] = [
    {
        "role": "user",
        "content": "זמינה ברביעי בבוקר ושלישי בערב",
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "slots": [
                    {"day": "רביעי", "part": "בוקר"},
                    {"day": "שלישי", "part": "ערב"},
                ]
            },
            ensure_ascii=False,
        ),
    },
    {
        "role": "user",
        "content": "בשבוע הבא פנויה רק בראשון ושני בערב",
    },
    {
        "role": "assistant",
        "content": json.dumps(
            {
                "slots": [
                    {"day": "ראשון", "part": "בוקר"},
                    {"day": "ראשון", "part": "צהריים"},
                    {"day": "ראשון", "part": "ערב"},
                    {"day": "שני", "part": "ערב"},
                ]
            },
            ensure_ascii=False,
        ),
    },
]


def parse_availability(message: str) -> list[TimeSlot]:
    """מפענח הודעת טקסט חופשית של מאמנת לרשימת משבצות זמן (TimeSlot) באמצעות קריאה ל-LLM.

    משתמש ב-Chat Completions API של OpenAI עם המודל gpt-5.6-luna.
    במידה והפענוח נכשל או שהתרחשה שגיאת תקשורת, מוחזרת רשימה ריקה כדי למנוע קריסה.
    """
    if not message or not message.strip():
        return []

    try:
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        messages = [
            {"role": "developer", "content": DEVELOPER_INSTRUCTIONS},
            *FEW_SHOT_EXAMPLES,
            {"role": "user", "content": message.strip()},
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            return []

        data = json.loads(content)
        raw_slots = data.get("slots", [])

        slots: list[TimeSlot] = []
        for item in raw_slots:
            day = item.get("day")
            part = item.get("part")
            if day in DAYS and part in PARTS_OF_DAY:
                slot = TimeSlot(day=day, part=part)
                if slot not in slots:
                    slots.append(slot)

        return slots

    except Exception:
        # החזרת תוצאה ריקה במקרה של שגיאת פענוח, שגיאת רשת, או מפתח API שאינו מוגדר
        return []
