"""שכבת מסד הנתונים וניהול המצב (State / Repository).

מודול זה אחראי בלעדית על שליפה, שמירה ועדכון של נתוני המאמנות ולוח השיעורים.
בגרסת ה-MVP המימוש מנוהל בזיכרון, אך הממשק מוגדר כך שניתן יהיה להחליפו
באחסון קבוע (כגון קובץ JSON או מסד נתונים SQLite) מבלי לשנות אף מודול אחר.
"""

try:
    from source.models import GymClass, TimeSlot, Trainer
except ImportError:
    from models import GymClass, TimeSlot, Trainer

# נתוני דוגמה בזיכרון
_trainers: dict[str, Trainer] = {
    "נועה": Trainer(
        name="נועה",
        classes=["פילאטיס", "יוגה"],
        availability={TimeSlot("ראשון", "בוקר"), TimeSlot("שלישי", "בוקר")},
    ),
    "מיכל": Trainer(
        name="מיכל",
        classes=["זומבה", "אירובי"],
        availability={TimeSlot("שני", "ערב"), TimeSlot("רביעי", "ערב")},
    ),
    "שירה": Trainer(
        name="שירה",
        classes=["פילאטיס", "עיצוב"],
        availability={TimeSlot("ראשון", "ערב"), TimeSlot("חמישי", "בוקר")},
    ),
}

_schedule: list[GymClass] = [
    GymClass("פילאטיס", TimeSlot("ראשון", "בוקר"), "09:00", "נועה"),
    GymClass("עיצוב", TimeSlot("ראשון", "ערב"), "19:00", "שירה"),
    GymClass("זומבה", TimeSlot("שני", "ערב"), "20:00", "מיכל"),
    GymClass("יוגה", TimeSlot("שלישי", "בוקר"), "08:00", "נועה"),
    GymClass("אירובי", TimeSlot("רביעי", "ערב"), "19:30", "מיכל"),
    GymClass("פילאטיס", TimeSlot("רביעי", "בוקר"), "10:00", "נועה"),
    GymClass("עיצוב", TimeSlot("חמישי", "בוקר"), "09:30", "שירה"),
]


def get_trainer_names() -> list[str]:
    """שולף את שמות כל המאמנות הקיימות במערכת לצורך הצגה בתפריט בחירה בממשק."""
    return list(_trainers.keys())


def get_trainer(name: str) -> Trainer:
    """שולף אובייקט מאמנת מלא לפי שמה.

    מעלה KeyError אם המאמנת אינה קיימת.
    """
    return _trainers[name]


def get_trainers() -> list[Trainer]:
    """שולף את רשימת כל המאמנות במערכת על כל נתוניהן."""
    return list(_trainers.values())


def set_availability(name: str, slots: list[TimeSlot]) -> None:
    """מעדכן ומחליף את כל משבצות הזמינות השבועיות של מאמנת ספציפית."""
    if name in _trainers:
        _trainers[name].availability = set(slots)
    else:
        raise KeyError(f"מאמנת בשם '{name}' אינה קיימת במערכת.")


def get_schedule() -> list[GymClass]:
    """שולף את רשימת כל השיעורים הקיימים בלוח השיעורים השבועי."""
    return list(_schedule)
