"""שכבת מסד הנתונים וניהול המצב (State / Repository).

מודול זה אחראי בלעדית על שליפה, שמירה ועדכון של נתוני המאמנות ולוח השיעורים.
בגרסת ה-MVP המימוש מנוהל בזיכרון, אך הממשק מוגדר כך שניתן יהיה להחליפו
באחסון קבוע (כגון קובץ JSON או מסד נתונים SQLite) מבלי לשנות אף מודול אחר.
"""

try:
    from source.models import GymClass, TimeSlot, Trainer
except ImportError:
    from models import GymClass, TimeSlot, Trainer


def get_trainer_names() -> list[str]:
    """שולף את שמות כל המאמנות הקיימות במערכת לצורך הצגה בתפריט בחירה בממשק."""
    pass


def get_trainer(name: str) -> Trainer:
    """שולף אובייקט מאמנת מלא לפי שמה.

    מעלה KeyError או מחזיר שגיאה אם המאמנת אינה קיימת.
    """
    pass


def get_trainers() -> list[Trainer]:
    """שולף את רשימת כל המאמנות במערכת על כל נתוניהן."""
    pass


def set_availability(name: str, slots: list[TimeSlot]) -> None:
    """מעדכן ומחליף את כל משבצות הזמינות השבועיות של מאמנת ספציפית."""
    pass


def get_schedule() -> list[GymClass]:
    """שולף את רשימת כל השיעורים הקיימים בלוח השיעורים השבועי."""
    pass
