"""רכיב פענוח זמינות מאמנות בשפה טבעית (מימוש דטרמיניסטי מבוסס חוקים).

מודול זה מהווה גשר בין טקסט חופשי של מאמנת לבין משבצות זמן מובנות (TimeSlot)
באמצעות חוקי טקסט בעברית, ללא קריאות חיצוניות ל-OpenAI בשלב זה.
המימוש של OpenAI נשמר בנפרד בקובץ source/availability_llm.py.
"""

import re

try:
    from source.models import DAYS, PARTS_OF_DAY, TimeSlot
except ImportError:
    from models import DAYS, PARTS_OF_DAY, TimeSlot

# תחיליות נפוצות בעברית שעשויות להופיע לפני מילות יום או חלק ביום
_PREFIX_PATTERN = r"[ובהלמ]*"

_DAY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(rf"^{_PREFIX_PATTERN}({day})$"), day) for day in DAYS
]

_PART_ALIASES: dict[str, str] = {
    "בוקר": "בוקר",
    "צהריים": "צהריים",
    "צהרים": "צהריים",
    "ערב": "ערב",
}

_PART_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(rf"^{_PREFIX_PATTERN}({alias})$"), canonical)
    for alias, canonical in _PART_ALIASES.items()
]

_SINGULAR_DAY_WORD = re.compile(rf"^{_PREFIX_PATTERN}יום$")
_PLURAL_DAY_WORD = re.compile(rf"^{_PREFIX_PATTERN}ימים$")
_ALL_WORD = re.compile(r"^[ובהל]?כל$")
_WEEK_WORD = re.compile(r"^[ובהל]?ה?שבוע$")
_EXCEPT_WORD = re.compile(r"^[ובהל]?חוץ$")
_EXCEPT_ALT_WORD = re.compile(r"^[ובהל]?למעט$")
_MEM_WORD = re.compile(r"^מ$")
_TOKEN_RE = re.compile(r"[,.;\n]|[\u0590-\u05FF]+")


def _tokenize(text: str) -> list[str]:
    """מפרק את הטקסט לרשימת מילים בעברית וסימני הפרדה."""
    return _TOKEN_RE.findall(text)


def _match_day(token: str) -> str | None:
    """מחזיר את שם היום התקני אם המילה מייצגת יום בשבוע (כולל תחיליות)."""
    for pattern, day in _DAY_PATTERNS:
        if pattern.fullmatch(token):
            return day
    return None


def _match_part(token: str) -> str | None:
    """מחזיר את חלק היום התקני אם המילה מייצגת חלק ביום (כולל תחיליות)."""
    for pattern, part in _PART_PATTERNS:
        if pattern.fullmatch(token):
            return part
    return None


def _append_unique(slots: list[TimeSlot], seen: set[TimeSlot], slot: TimeSlot) -> None:
    """מוסיף משבצת לרשימה רק אם טרם הופיעה."""
    if slot not in seen:
        seen.add(slot)
        slots.append(slot)


def _flush_days(
    days_buffer: list[str],
    has_parts: bool,
    slots: list[TimeSlot],
    seen: set[TimeSlot],
) -> None:
    """משלים ימים ללא חלק יום מוגדר לכל חלקי היום (בוקר, צהריים, ערב)."""
    if days_buffer and not has_parts:
        for day in days_buffer:
            for part in PARTS_OF_DAY:
                _append_unique(slots, seen, TimeSlot(day=day, part=part))


def _parse_tokens(tokens: list[str]) -> list[TimeSlot]:
    """מפענח רשימת טוקנים מפורשת של ימים וחלקי יום למשבצות TimeSlot."""
    slots: list[TimeSlot] = []
    seen: set[TimeSlot] = set()

    current_days: list[str] = []
    current_has_parts = False
    multi_day_group = False

    for token in tokens:
        if token in {",", ".", ";", "\n"}:
            multi_day_group = False
            if token in {".", ";", "\n"}:
                _flush_days(current_days, current_has_parts, slots, seen)
                current_days = []
                current_has_parts = False
            continue

        if _PLURAL_DAY_WORD.fullmatch(token):
            _flush_days(current_days, current_has_parts, slots, seen)
            current_days = []
            current_has_parts = False
            multi_day_group = True
            continue

        if _SINGULAR_DAY_WORD.fullmatch(token):
            _flush_days(current_days, current_has_parts, slots, seen)
            current_days = []
            current_has_parts = False
            multi_day_group = False
            continue

        day = _match_day(token)
        if day is not None:
            if current_has_parts or not multi_day_group:
                _flush_days(current_days, current_has_parts, slots, seen)
                current_days = [day]
                current_has_parts = False
            else:
                if day not in current_days:
                    current_days.append(day)
            continue

        part = _match_part(token)
        if part is not None and current_days:
            for active_day in current_days:
                _append_unique(slots, seen, TimeSlot(day=active_day, part=part))
            current_has_parts = True

    _flush_days(current_days, current_has_parts, slots, seen)
    return slots


def _find_all_week_range(tokens: list[str]) -> int | None:
    """מחזיר את האינדקס שממנו מתחיל 'כל השבוע', או None אם אינו מופיע."""
    for i in range(len(tokens) - 1):
        if _ALL_WORD.fullmatch(tokens[i]) and _WEEK_WORD.fullmatch(tokens[i + 1]):
            return i
    return None


def _find_exception_start(tokens: list[str], start_idx: int) -> int | None:
    """מאתר תחילת ביטוי החרגה ('חוץ מ...' / 'למעט ...') ומחזיר את אינדקס הטוקנים שאחריו."""
    for i in range(start_idx, len(tokens)):
        if _EXCEPT_WORD.fullmatch(tokens[i]):
            if i + 1 < len(tokens) and _MEM_WORD.fullmatch(tokens[i + 1]):
                return i + 2
            return i + 1
        if _EXCEPT_ALT_WORD.fullmatch(tokens[i]):
            return i + 1
    return None


def parse_availability(message: str) -> list[TimeSlot]:
    """מפענח הודעת טקסט חופשית של מאמנת לרשימת משבצות זמן (TimeSlot) באמצעות חוקים.

    תומך בין היתר בביטויים:
    - "ברביעי", "ביום רביעי", "בימים שני ורביעי"
    - "בבוקר", "בצהריים", "בערב", "בבוקר ובערב"
    - יום ללא חלק יום -> כל חלקי היום (בוקר, צהריים, ערב)
    - "כל השבוע" ו-"כל השבוע חוץ מ..."
    """
    if not message or not message.strip():
        return []

    tokens = _tokenize(message.strip())
    if not tokens:
        return []

    all_week_idx = _find_all_week_range(tokens)
    if all_week_idx is not None:
        all_slots = [TimeSlot(day=day, part=part) for day in DAYS for part in PARTS_OF_DAY]
        exc_idx = _find_exception_start(tokens, all_week_idx + 2)
        if exc_idx is None:
            return all_slots
        excluded = set(_parse_tokens(tokens[exc_idx:]))
        return [slot for slot in all_slots if slot not in excluded]

    return _parse_tokens(tokens)
