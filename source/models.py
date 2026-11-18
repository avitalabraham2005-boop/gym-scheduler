"""טיפוסי הנתונים והישויות המרכזיות של המערכת.

מודול זה מגדיר את מבני הנתונים הטהורים (ללא לוגיקה עסקית וללא תלות במודולים אחרים).
הוא משמש כמקור אמת יחיד (Single Source of Truth) לכל שאר המודולים במערכת ה-MVP.
"""

from dataclasses import dataclass, field

# קבועים עבור ימות השבוע וחלקי היום
DAYS: list[str] = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי"]
PARTS_OF_DAY: list[str] = ["בוקר", "צהריים", "ערב"]


@dataclass(frozen=True)
class TimeSlot:
    """משבצת זמן שבועית.

    מייצגת שילוב חד-ערכי של יום בשבוע וחלק ביום.
    דוגמה: TimeSlot(day="רביעי", part="בוקר").
    """

    day: str
    part: str


@dataclass
class Trainer:
    """מאמנת במכון הכושר.

    מכילה את שם המאמנת, רשימת שמות השיעורים שהיא מוסמכת להעביר,
    וקבוצת משבצות הזמן שבהן היא זמינה לאימון.
    """

    name: str
    classes: list[str]
    availability: set[TimeSlot] = field(default_factory=set)


@dataclass
class GymClass:
    """שיעור בלוח השיעורים השבועי.

    מייצג מופע שיעור ספציפי: שם השיעור, משבצת הזמן השבועית,
    שעת ההתחלה, ושם המאמנת המשובצת להעביר אותו.
    """

    name: str
    slot: TimeSlot
    hour: str
    trainer: str
