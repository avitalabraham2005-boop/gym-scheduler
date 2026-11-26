"""רכיב LLM לפענוח זמינות מאמנות בשפה טבעית דרך API תואם OpenAI."""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

try:
    from source.models import DAYS, PARTS_OF_DAY, TimeSlot
except ImportError:
    from models import DAYS, PARTS_OF_DAY, TimeSlot

PROVIDER: str = "gemini"
MODEL: str = "gemini-3.5-flash"

_PROVIDER_CONFIG: dict[str, tuple[str, str]] = {
    "gemini": (
        "GEMINI_API_KEY",
        "https://generativelanguage.googleapis.com/v1beta/openai/",
    ),
    "openai": ("OPENAI_API_KEY", "https://api.openai.com/v1"),
}
_API_KEY_ENV, _BASE_URL = _PROVIDER_CONFIG[PROVIDER]

# טעינת מפתח ה-API מתוך קובץ .env (בתיקיית הפרויקט או בתיקיות אב)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
if not os.getenv(_API_KEY_ENV):
    load_dotenv()

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

    משתמש במודל ובספק שמוגדרים בראש הקובץ דרך Chat Completions API תואם OpenAI.
    במידה והפענוח נכשל או שהתרחשה שגיאת תקשורת, מוחזרת רשימה ריקה כדי למנוע קריסה.
    """
    if not message or not message.strip():
        return []

    try:
        api_key = os.getenv(_API_KEY_ENV)
        if not api_key:
            raise RuntimeError(f"Missing API key environment variable: {_API_KEY_ENV}")
        client = OpenAI(api_key=api_key, base_url=_BASE_URL)

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
        if not isinstance(raw_slots, list):
            return []

        slots: list[TimeSlot] = []
        for item in raw_slots:
            if not isinstance(item, dict):
                continue
            day = item.get("day")
            part = item.get("part")
            if day in DAYS and part in PARTS_OF_DAY:
                slot = TimeSlot(day=day, part=part)
                if slot not in slots:
                    slots.append(slot)

        return slots

    except Exception as exc:
        # הדפסת השגיאה לטרמינל והחזרת תוצאה ריקה כדי למנוע קריסת הממשק
        print(f"[availability_llm] שגיאה בפענוח הזמינות: {type(exc).__name__}: {exc}")
        return []
