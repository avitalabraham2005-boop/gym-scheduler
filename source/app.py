"""שכבת ממשק המשתמש (Gradio) ותזמור האירועים עבור תרחיש 1.

מודול זה מחליף את ממשק הטרמינל בממשק Web מודרני מבוסס Gradio:
- בחירת מאמנת מתפריט נפתח (Dropdown)
- הזנת הודעת זמינות בשפה חופשית (Textbox)
- כפתור עדכון זמינות
- הצגת טבלת הזמינות הנוכחית של המאמנת
- הצגת לוח השיעורים השבועי עם סימון תקלות וקונפליקטים
- תמיכה מלאה בכיווניות מימין לשמאל (RTL) עבור עברית
"""

import sys
from pathlib import Path
import gradio as gr

# הוספת נתיב השורש ונתיב source ל-sys.path לתמיכה בכל דרכי ההרצה
root_dir = Path(__file__).resolve().parent.parent
source_dir = Path(__file__).resolve().parent
for d in (str(root_dir), str(source_dir)):
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from source import availability_ai, database, scheduling
    from source.models import DAYS
except ImportError:
    import availability_ai
    import database
    import scheduling
    from models import DAYS

SCHEDULE_HEADERS: list[str] = ["יום", "שעה", "שיעור", "מאמנת", "סטטוס"]
AVAILABILITY_HEADERS: list[str] = ["חלק ביום"] + DAYS

CSS: str = """
.gradio-container {
    direction: rtl !important;
    text-align: right !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
th, td {
    text-align: right !important;
}
"""


def show_trainer(name: str) -> list[list[str]]:
    """שולף ומחזיר את טבלת הזמינות הנוכחית של המאמנת שנבחרה בתפריט."""
    trainer = database.get_trainer(name)
    return scheduling.availability_table(trainer.availability)


def update_availability(name: str, message: str) -> tuple[str, list[list[str]], list[list[str]]]:
    """מתזמר את תרחיש עדכון הזמינות של מאמנת:

    1. שולח את הודעת הטקסט החופשית לפענוח במודול availability_ai.
    2. מעדכן את הזמינות במסד הנתונים דרך database.
    3. שולף את נתוני המאמנת, המאמנות ולוח השיעורים המעודכנים.
    4. מפעיל את פונקציות scheduling לחישוב קונפליקטים והפקת טבלאות תצוגה.
    5. מחזיר שלישיית ערכים: הודעת סטטוס טקסטואלית, טבלת זמינות מעודכנת, ולוח שיעורים מעודכן.
    """
    slots = availability_ai.parse_availability(message)
    print(f"[update_availability] מאמנת: {name!r} | הודעה: {message!r} | תוצאת הפענוח: {slots}")
    if not slots:
        status = "לא הצלחתי להבין את ההודעה. נסי לכתוב ימים וחלקי יום, למשל: 'זמינה ברביעי בבוקר ושלישי בערב'."
    else:
        database.set_availability(name, slots)
        status = f"הזמינות של {name} עודכנה בהצלחה ({len(slots)} משבצות)."

    trainer = database.get_trainer(name)
    avail_table = scheduling.availability_table(trainer.availability)
    sched_table = scheduling.schedule_table(database.get_schedule(), database.get_trainers())
    return status, avail_table, sched_table


def create_app() -> gr.Blocks:
    """בונה ומגדיר את ממשק המשתמש הגרפי (Gradio Blocks) בעברית (RTL)."""
    with gr.Blocks(title="מערכת שיבוץ למכון כושר") as demo:
        # הזרקת סגנון RTL ישיר לדף
        gr.HTML(f"<style>{CSS}</style>")

        gr.Markdown("# 🏋️‍♀️ מערכת ניהול ושיבוץ חכמה למכון כושר")
        gr.Markdown("גרסת MVP – עדכון זמינות מאמנות בשפה טבעית ובדיקת לוח שיעורים שבועי.")

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### עדכון זמינות של מאמנת")
                trainer_name = gr.Dropdown(
                    choices=database.get_trainer_names(),
                    value=database.get_trainer_names()[0] if database.get_trainer_names() else None,
                    label="בחירת מאמנת",
                    interactive=True,
                )
                message = gr.Textbox(
                    label="הודעת זמינות בשפה חופשית",
                    placeholder="למשל: זמינה ברביעי בבוקר ושלישי בערב",
                    rtl=True,
                    lines=2,
                )
                send_button = gr.Button("עדכני זמינות", variant="primary")
                status = gr.Textbox(label="סטטוס תוצאה", interactive=False, rtl=True)

            with gr.Column(scale=1):
                gr.Markdown("### הזמינות השבועית הנוכחית")
                default_trainer = database.get_trainer_names()[0] if database.get_trainer_names() else "נועה"
                availability = gr.Dataframe(
                    headers=AVAILABILITY_HEADERS,
                    value=show_trainer(default_trainer),
                    interactive=False,
                    label="טבלת זמינות (V = זמינה, - = לא זמינה)",
                )

        gr.Markdown("### 📅 לוח השיעורים השבועי וסטטוס תקלות")
        schedule = gr.Dataframe(
            headers=SCHEDULE_HEADERS,
            value=scheduling.schedule_table(database.get_schedule(), database.get_trainers()),
            interactive=False,
            label="לוח השיעורים השבועי (כולל התרעות על קונפליקטים ואי-זמינות)",
        )

        # חיבורי אירועים (Event Wiring)
        trainer_name.change(fn=show_trainer, inputs=trainer_name, outputs=availability)
        send_button.click(
            fn=update_availability,
            inputs=[trainer_name, message],
            outputs=[status, availability, schedule],
        )
        message.submit(
            fn=update_availability,
            inputs=[trainer_name, message],
            outputs=[status, availability, schedule],
        )

    return demo


def main() -> None:
    """הפעלת שרת ה-Web של Gradio."""
    demo = create_app()
    demo.launch(css=CSS)


if __name__ == "__main__":
    main()
