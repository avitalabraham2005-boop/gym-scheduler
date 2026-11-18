"""שכבת ממשק המשתמש (Gradio) ותזמור האירועים.

מודול זה אחראי על הצגת הממשק הוויזואלי וקליטת אינטראקציות מהמשתמשת.
הוא מתזמר את הקריאות לפענוח הודעות (availability_ai), לעדכון ושליפת נתונים (database),
ולחישוב טבלאות תקינות (scheduling).
"""

try:
    from source.models import DAYS
except ImportError:
    from models import DAYS


def show_trainer(name: str) -> list[list[str]]:
    """שולף ומחזיר את טבלת הזמינות הנוכחית של המאמנת שנבחרה בתפריט."""
    pass


def update_availability(name: str, message: str) -> tuple[str, list[list[str]], list[list[str]]]:
    """מתזמר את תרחיש עדכון הזמינות של מאמנת:

    1. שולח את הודעת הטקסט החופשית לפענוח במודול availability_ai.
    2. במידה והפענוח הצליח, מעדכן את הזמינות במסד הנתונים דרך database.
    3. שולף את נתוני המאמנת, המאמנות ולוח השיעורים המעודכנים.
    4. מפעיל את פונקציות scheduling לחישוב קונפליקטים והפקת טבלאות תצוגה.
    5. מחזיר שלישיית ערכים: הודעת סטטוס טקסטואלית, טבלת זמינות מעודכנת, ולוח שיעורים מעודכן.
    """
    pass


def create_app():
    """בונה ומגדיר את בלוקי הממשק הגרפי (Gradio Blocks)."""
    pass
