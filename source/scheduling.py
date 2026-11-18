"""מנוע שיבוץ ובדיקת תקינות דטרמיניסטי (Scheduling & Validation Engine).

מודול זה מיישם קוד רגיל (דטרמיניסטי) לבדיקת חוקי שיבוץ והכנת טבלאות נתונים
לתצוגה בממשק המשתמש.
"""

try:
    from source.models import GymClass, TimeSlot, Trainer
except ImportError:
    from models import GymClass, TimeSlot, Trainer


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
    pass


def schedule_table(schedule: list[GymClass], trainers: list[Trainer]) -> list[list[str]]:
    """מייצר את נתוני לוח השיעורים השבועי כטבלה דו-ממדית ממוינת עם עמודת סטטוס.

    ממיין לפי יום ושעה, ומוסיף עמודת סטטוס ("תקין" או תיאור הבעיה מ-find_problems).
    התוצאה מוכנה להזנה ישירה לרכיב gr.Dataframe של Gradio.
    """
    pass


def availability_table(slots: set[TimeSlot]) -> list[list[str]]:
    """מייצר מטריצת זמינות שבועית עבור מאמנת יחידה.

    בונה טבלה שבה השורות הן חלקי היום (בוקר, צהריים, ערב)
    והעמודות הן ימות השבוע, כאשר משבצות זמינות מסומנות ב-"V".
    התוצאה מוכנה להזנה ישירה לרכיב gr.Dataframe של Gradio.
    """
    pass
