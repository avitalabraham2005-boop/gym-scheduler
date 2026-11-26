"""רכיב LLM לפענוח זמינות מאמנות בשפה טבעית באמצעות לקוח ה-LLM המרכזי."""

import json
from openai import APIStatusError

try:
    from source.llm_client import MODEL, PROVIDER, get_client
    from source.models import DAYS, PARTS_OF_DAY, TimeSlot
except ImportError:
    from llm_client import MODEL, PROVIDER, get_client
    from models import DAYS, PARTS_OF_DAY, TimeSlot

DEVELOPER_INSTRUCTIONS: str = f"""אתה רכיב AI במערכת ניהול ושיבוץ למכון כושר.

המשימה:
לפענח הודעות זמינות בעברית חופשית שנכתבו על ידי מאמנות, ולחלץ מהן את משבצות הזמן שבהן המאמנת זמינה לאמן.

רשימת הימים התקינים (ראשון עד שישי):
{', '.join(DAYS)}

חלקי היום וטווחי השעות שלהם:
- בוקר: 06-12
- צהריים: 12-17
- ערב: 17-22
בשדה "part" יש להחזיר אך ורק אחד מהערכים: {', '.join(PARTS_OF_DAY)}.

כללים:
1. יום בלי ציון חלק יום משמעותו כל היום – יש לכלול עבורו את כל שלושת חלקי היום (בוקר, צהריים, ערב).
2. ביטויי החרגה כגון "חוץ מ..." או "למעט..." מוציאים את הימים או חלקי היום שהוחרגו מתוך הטווח שצוין (למשל "כל השבוע" פירושו ראשון עד שישי בכל חלקי היום, ללא המשבצות שהוחרגו).
3. אם מצוינת שעה, יש לשייך אותה לחלק היום המתאים (בוקר 06-12, צהריים 12-17, ערב 17-22).
4. אם אין זמינות בהודעה (או שההודעה אינה מתארת זמינות), יש להחזיר רשימה ריקה: [].

פורמט פלט:
החזר JSON תקין בלבד (ללא טקסט נוסף וללא סימני Markdown), כרשימה של אובייקטים שכל אחד מהם מכיל את השדות "day" ו-"part" בלבד:
[{{"day": "<יום>", "part": "<חלק_ביום>"}}]
"""

FEW_SHOT_EXAMPLES: list[dict[str, str]] = [
    {
        "role": "user",
        "content": "זמינה ברביעי בבוקר ושלישי בערב",
    },
    {
        "role": "assistant",
        "content": json.dumps(
            [
                {"day": "רביעי", "part": "בוקר"},
                {"day": "שלישי", "part": "ערב"},
            ],
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
            [
                {"day": "ראשון", "part": "בוקר"},
                {"day": "ראשון", "part": "צהריים"},
                {"day": "ראשון", "part": "ערב"},
                {"day": "שני", "part": "ערב"},
            ],
            ensure_ascii=False,
        ),
    },
    {
        "role": "user",
        "content": "זמינה כל השבוע בבוקר חוץ משני ושישי",
    },
    {
        "role": "assistant",
        "content": json.dumps(
            [
                {"day": "ראשון", "part": "בוקר"},
                {"day": "שלישי", "part": "בוקר"},
                {"day": "רביעי", "part": "בוקר"},
                {"day": "חמישי", "part": "בוקר"},
            ],
            ensure_ascii=False,
        ),
    },
    {
        "role": "user",
        "content": "השבוע אני בחופשה ולא זמינה בכלל",
    },
    {
        "role": "assistant",
        "content": "[]",
    },
]


def _parse_json_list(content: str) -> list[object]:
    """מנקה גדרות קוד במידת הצורך ומפענח את תשובת המודל כרשימת JSON."""
    cleaned = content.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    data = json.loads(cleaned)
    if not isinstance(data, list):
        raise ValueError("Expected JSON list of slot objects from LLM")
    return data


def parse_availability(message: str) -> list[TimeSlot]:
    """מפענח הודעת טקסט חופשית של מאמנת לרשימת משבצות זמן (TimeSlot) באמצעות קריאה ל-LLM."""
    if not message or not message.strip():
        return []

    client = get_client()
    instruction_role = "developer" if PROVIDER == "openai" else "system"
    messages = [
        {"role": instruction_role, "content": DEVELOPER_INSTRUCTIONS},
        *FEW_SHOT_EXAMPLES,
        {"role": "user", "content": message.strip()},
    ]

    request_kwargs: dict[str, object] = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
    }
    if PROVIDER == "openai":
        request_kwargs["seed"] = 42

    try:
        response = client.chat.completions.create(**request_kwargs)
    except APIStatusError as exc:
        response_text = exc.response.text if getattr(exc, "response", None) is not None else ""
        full_error = response_text or (
            json.dumps(exc.body, ensure_ascii=False) if exc.body is not None else str(exc)
        )
        print(
            f"[availability_llm] שגיאת שרת מלאה ({type(exc).__name__}, status={exc.status_code}):\n{full_error}"
        )
        raise
    except Exception as exc:
        print(f"[availability_llm] שגיאה בקריאה ל-LLM ({type(exc).__name__}): {exc}")
        raise

    usage = response.usage
    if usage is not None:
        input_tokens = usage.prompt_tokens or 0
        output_tokens = usage.completion_tokens or 0
        details = getattr(usage, "prompt_tokens_details", None)
        cached_tokens = (getattr(details, "cached_tokens", 0) if details else 0) or 0
        print(
            f"[availability_llm] tokens - input: {input_tokens}, "
            f"output: {output_tokens}, cached: {cached_tokens}"
        )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Empty response content from LLM")

    raw_slots = _parse_json_list(content)
    slots: list[TimeSlot] = []
    seen: set[TimeSlot] = set()
    for item in raw_slots:
        if not isinstance(item, dict):
            raise ValueError(f"Expected object in JSON list, got {type(item).__name__}")
        day = item.get("day")
        part = item.get("part")
        if day in DAYS and part in PARTS_OF_DAY:
            slot = TimeSlot(day=day, part=part)
            if slot not in seen:
                seen.add(slot)
                slots.append(slot)

    return slots
