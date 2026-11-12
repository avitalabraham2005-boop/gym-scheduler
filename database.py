"""מסד נתונים פשוט בזיכרון, עם נתוני דוגמה.

בהמשך אפשר להחליף אותו בקובץ JSON או במסד נתונים אמיתי,
בלי לשנות את שאר המודולים - כל עוד הפונקציות כאן נשארות אותו דבר.
"""

from models import GymClass, TimeSlot, Trainer

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
    return list(_trainers)


def get_trainer(name: str) -> Trainer:
    return _trainers[name]


def get_trainers() -> list[Trainer]:
    return list(_trainers.values())


def set_availability(name: str, slots: list[TimeSlot]) -> None:
    """מחליף את כל הזמינות של המאמנת בזמינות החדשה."""
    _trainers[name].availability = set(slots)


def get_schedule() -> list[GymClass]:
    return list(_schedule)