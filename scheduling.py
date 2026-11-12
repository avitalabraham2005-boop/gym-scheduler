"""קוד רגיל: בדיקת תקלות בלוח השעות והכנת טבלאות לתצוגה."""

from models import DAYS, PARTS_OF_DAY, GymClass, TimeSlot, Trainer


def find_problems(schedule: list[GymClass], trainers: list[Trainer]) -> dict[int, str]:
    """מחזיר מילון: מספר השיעור בלוח -> תיאור הבעיה. שיעור תקין לא מופיע."""
    by_name = {t.name: t for t in trainers}
    problems: dict[int, str] = {}
    seen: dict[tuple[str, str, str], int] = {}

    for i, c in enumerate(schedule):
        trainer = by_name.get(c.trainer)
        if trainer is None:
            problems[i] = "המאמנת לא קיימת במערכת"
        elif c.slot not in trainer.availability:
            problems[i] = "המאמנת לא זמינה בזמן הזה"
        elif c.name not in trainer.classes:
            problems[i] = "המאמנת לא מעבירה שיעור מהסוג הזה"

        key = (c.trainer, c.slot.day, c.hour)
        if key in seen:
            problems[i] = "המאמנת משובצת לשני שיעורים באותה שעה"
        seen[key] = i

    return problems


def schedule_table(schedule: list[GymClass], trainers: list[Trainer]) -> list[list[str]]:
    """טבלת הלוח השבועי, ממוינת לפי יום ושעה, עם עמודת סטטוס."""
    problems = find_problems(schedule, trainers)
    order = sorted(range(len(schedule)), key=lambda i: (DAYS.index(schedule[i].slot.day), schedule[i].hour))
    return [
        [
            schedule[i].slot.day,
            schedule[i].hour,
            schedule[i].name,
            schedule[i].trainer,
            problems.get(i, "תקין"),
        ]
        for i in order
    ]


def availability_table(slots: set[TimeSlot]) -> list[list[str]]:
    """טבלה של מאמנת אחת: שורה לכל חלק ביום, עמודה לכל יום. V = זמינה."""
    return [[part] + ["V" if TimeSlot(day, part) in slots else "" for day in DAYS] for part in PARTS_OF_DAY]