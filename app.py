"""ממשק המשתמש (Gradio): המאמנת כותבת זמינות, והלוח מתעדכן."""

import gradio as gr

import database
from availability_ai import parse_availability
from models import DAYS
from scheduling import availability_table, schedule_table

SCHEDULE_HEADERS = ["יום", "שעה", "שיעור", "מאמנת", "סטטוס"]
AVAILABILITY_HEADERS = ["חלק ביום"] + DAYS

CSS = """
.gradio-container { direction: rtl; text-align: right; }
"""


def show_trainer(name: str):
    trainer = database.get_trainer(name)
    return availability_table(trainer.availability)


def update_availability(name: str, message: str):
    slots = parse_availability(message)
    if not slots:
        status = "לא הצלחתי להבין את ההודעה. נסי לכתוב ימים וחלקי יום, למשל: 'זמינה ברביעי בבוקר'."
    else:
        database.set_availability(name, slots)
        status = f"הזמינות של {name} עודכנה ({len(slots)} משבצות)."
    trainer = database.get_trainer(name)
    table = schedule_table(database.get_schedule(), database.get_trainers())
    return status, availability_table(trainer.availability), table


with gr.Blocks(title="מערכת שיבוץ למכון כושר") as demo:
    gr.Markdown("# מערכת ניהול ושיבוץ חכמה למכון כושר")

    with gr.Row():
        with gr.Column():
            gr.Markdown("## עדכון זמינות של מאמנת")
            trainer_name = gr.Dropdown(database.get_trainer_names(), value="נועה", label="מאמנת")
            message = gr.Textbox(label="הודעת זמינות", placeholder="למשל: זמינה ברביעי בבוקר ושלישי בערב", rtl=True)
            send = gr.Button("עדכני זמינות", variant="primary")
            status = gr.Textbox(label="תוצאה", interactive=False, rtl=True)
        with gr.Column():
            gr.Markdown("## הזמינות הנוכחית")
            availability = gr.Dataframe(
                headers=AVAILABILITY_HEADERS,
                value=availability_table(database.get_trainer("נועה").availability),
                interactive=False,
            )

    gr.Markdown("## לוח השיעורים השבועי")
    schedule = gr.Dataframe(
        headers=SCHEDULE_HEADERS,
        value=schedule_table(database.get_schedule(), database.get_trainers()),
        interactive=False,
    )

    trainer_name.change(fn=show_trainer, inputs=trainer_name, outputs=availability)
    send.click(fn=update_availability, inputs=[trainer_name, message], outputs=[status, availability, schedule])


if __name__ == "__main__":
    demo.launch(css=CSS)