"""קליטת זמינות מהודעה חופשית של מאמנת.

כרגע זו *פונקציית דמה*: היא מזהה מילים קבועות (ימים וחלקי יום) בלי AI.
במודול 3 נחליף אותה בקריאה אמיתית ל-LLM, עם אותו ממשק בדיוק:
מקבלת טקסט ומחזירה רשימה של TimeSlot.
"""

from models import DAYS, PARTS_OF_DAY, TimeSlot


def _normalize(word: str, vocabulary: list[str]) -> str | None:
    """מוריד אותיות שימוש בתחילת מילה (ו, ב, ה) ומחפש אותה ברשימה."""
    word = word.strip(".,!?:;\"'")
    for start in range(3):
        if word[start:] in vocabulary:
            return word[start:]
    return None


def parse_availability(message: str) -> list[TimeSlot]:
    """למשל: 'זמינה ברביעי בבוקר ושלישי בערב' -> [רביעי/בוקר, שלישי/ערב].

    יום בלי חלק יום אחריו נחשב כיום שלם.
    """
    slots: list[TimeSlot] = []
    pending_days: list[str] = []

    for word in message.split():
        day = _normalize(word, DAYS)
        part = _normalize(word, PARTS_OF_DAY)
        if day:
            pending_days.append(day)
        elif part and pending_days:
            slots += [TimeSlot(d, part) for d in pending_days]
            pending_days = []

    for d in pending_days:
        slots += [TimeSlot(d, p) for p in PARTS_OF_DAY]

    return slots