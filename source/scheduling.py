"""מנוע שיבוץ ובדיקת תקינות דטרמיניסטי (Scheduling & Validation Engine).

מודול זה מיישם קוד רגיל (דטרמיניסטי) לבדיקת חוקי שיבוץ והכנת טבלאות נתונים
לתצוגה בממשק המשתמש.
"""

try:
    from source.models import DAYS, PARTS_OF_DAY, GymClass, TimeSlot, Trainer
except ImportError:
    from models import DAYS, PARTS_OF_DAY, GymClass, TimeSlot, Trainer


def find_problems(schedule: list[GymClass], trainers: list[Trainer]) -> dict[int, str]:
    """מאתר בעיות וקונפליקטים בלוח השיעורים מול זמינות והסמכות המאמנות.

    בדיקות התקינות כוללות:
    1. מאמנת שאינה קיימת במערכת.
    2. מאמנת שאינה זמינה במשבצת השיעור.
    3. מאמנת המשובצת לשיעור שהיא אינה מוסמכת להעביר.
    4. כפל שיבוץ: מאמנת המשובצת לשני שיעורים שונים באותה שעה.

    מחזיר מילון שבו המפתח הוא אינדקס השיעור בלוח והערך הוא תיאור התקלה.
    שיעורים תקינים לחלוטין אינם מופיעים במילון.
    """
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
            problems[seen[key]] = "המאמנת משובצת לשני שיעורים באותה שעה"
        seen[key] = i

    return problems


def schedule_table(schedule: list[GymClass], trainers: list[Trainer]) -> list[list[str]]:
    """מייצר את נתוני לוח השיעורים השבועי כטבלה דו-ממדית ממוינת עם עמודת סטטוס.

    ממיין לפי יום ושעה, ומוסיף עמודת סטטוס ("תקין" או תיאור הבעיה מ-find_problems).
    """
    problems = find_problems(schedule, trainers)
    order = sorted(
        range(len(schedule)),
        key=lambda i: (
            DAYS.index(schedule[i].slot.day) if schedule[i].slot.day in DAYS else 99,
            schedule[i].hour,
        ),
    )
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
    """מייצר מטריצת זמינות שבועית עבור מאמנת יחידה.

    בונה טבלה שבה השורות הן חלקי היום (בוקר, צהריים, ערב)
    והעמודות הן ימות השבוע, כאשר משבצות זמינות מסומנות ב-"V" ולא זמינות ב-"-".
    """
    return [
        [part] + ["V" if TimeSlot(day, part) in slots else "-" for day in DAYS]
        for part in PARTS_OF_DAY
    ]
