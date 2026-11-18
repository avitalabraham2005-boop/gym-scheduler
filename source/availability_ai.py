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
    """מפענח הודעת טקסט חופשית של מאמנת ומחלץ מתוכה רשימת משבצות זמן.

    דוגמה לקלט: "זמינה ברביעי בבוקר ושלישי בערב"
    דוגמה לפלט: [TimeSlot(day="רביעי", part="בוקר"), TimeSlot(day="שלישי", part="ערב")]
    אם ההודעה אינה מובנת או שאין בה ימים, תוחזר רשימה ריקה.
    """
    pass
