"""רכיב בינה מלאכותית לקליטת זמינות מאמנות בשפה טבעית.

מודול זה מהווה גשר בין טקסט חופשי ולא מובנה של מאמנת לבין משבצות זמן מובנות.
הממשק מוגדר בצורה אחידה הן לשלב הדמה (Stub) והן לשלב ה-LLM המלא (עם Tool Calling / Structured Output)
הנדרש בהמשך ה-MVP.
"""

try:
    from source.models import TimeSlot
except ImportError:
    from models import TimeSlot


def parse_availability(message: str) -> list[TimeSlot]:
    """סטאב (Stub): מחזיר ערך קבוע מראש (Hardcoded) של משבצות זמן עבור הודעת הזמינות.

    מחזיר שתי משבצות:
    - יום רביעי בבוקר
    - יום שלישי בערב
    """
    return [
        TimeSlot(day="רביעי", part="בוקר"),
        TimeSlot(day="שלישי", part="ערב"),
    ]
