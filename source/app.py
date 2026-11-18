"""שכבת ממשק המשתמש בטרמינל (Terminal UI) ותזמור האירועים עבור תרחיש 1.

מודול זה מנהל את האינטראקציה מול המשתמשת בטרמינל:
- בחירת מאמנת
- קליטת הודעת זמינות חופשית
- הפעלת הפענוח (availability_ai)
- עדכון מסד הנתונים (database)
- בדיקת תקינות והצגת לוח השיעורים וטבלת הזמינות (scheduling)
- חזרה בלולאה עד להקשת Enter על שורה ריקה
"""

import sys
from pathlib import Path

# הוספת נתיב השורש ונתיב source ל-sys.path לתמיכה בכל דרכי ההרצה
root_dir = Path(__file__).resolve().parent.parent
source_dir = Path(__file__).resolve().parent
for d in (str(root_dir), str(source_dir)):
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from source import availability_ai, database, scheduling
    from source.models import DAYS, PARTS_OF_DAY
except ImportError:
    import availability_ai
    import database
    import scheduling
    from models import DAYS, PARTS_OF_DAY

SCHEDULE_HEADERS: list[str] = ["יום", "שעה", "שיעור", "מאמנת", "סטטוס"]
AVAILABILITY_HEADERS: list[str] = ["חלק ביום"] + DAYS


def print_table(headers: list[str], rows: list[list[str]]) -> None:
    """מדפיס טבלה מעוצבת ומיושרת בטרמינל."""
    all_rows = [headers] + rows
    col_widths = [max(len(str(r[i])) for r in all_rows) for i in range(len(headers))]
    col_widths = [max(w, 6) for w in col_widths]

    separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    print(separator)
    header_str = "| " + " | ".join(f"{str(h):<{col_widths[i]}}" for i, h in enumerate(headers)) + " |"
    print(header_str)
    print(separator)
    for row in rows:
        row_str = "| " + " | ".join(f"{str(cell):<{col_widths[i]}}" for i, cell in enumerate(row)) + " |"
        print(row_str)
    print(separator)


def show_trainer(name: str) -> list[list[str]]:
    """שולף ומחזיר את טבלת הזמינות הנוכחית של המאמנת שנבחרה."""
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
    if not slots:
        status = f"לא חולצו משבצות זמינות מההודעה עבור {name}."
    else:
        database.set_availability(name, slots)
        status = f"הזמינות של {name} עודכנה בהצלחה ({len(slots)} משבצות)."

    trainer = database.get_trainer(name)
    avail_tbl = scheduling.availability_table(trainer.availability)
    sched_tbl = scheduling.schedule_table(database.get_schedule(), database.get_trainers())
    return status, avail_tbl, sched_tbl


def main() -> None:
    """לולאת הממשק הראשית בטרמינל עבור תרחיש 1."""
    print("\n" + "=" * 65)
    print("  מערכת ניהול ושיבוץ למכון כושר - ממשק טרמינל (תרחיש 1)  ")
    print("=" * 65)

    trainers = database.get_trainer_names()
    print(f"\nמאמנות רשומות במערכת: {', '.join(trainers)}")

    # בחירת מאמנת ראשונית
    prompt_trainer = input(f"בחרי מאמנת מתוך הרשימה [{trainers[0]}]: ").strip()
    if prompt_trainer in trainers:
        chosen_trainer = prompt_trainer
    else:
        chosen_trainer = trainers[0]

    print(f"\nנבחרה המאמנת: {chosen_trainer}")
    print(f"טבלת הזמינות הנוכחית של {chosen_trainer}:")
    print_table(AVAILABILITY_HEADERS, show_trainer(chosen_trainer))

    print("\nלוח השיעורים השבועי הנוכחי (כולל סטטוס תקלות):")
    print_table(
        SCHEDULE_HEADERS,
        scheduling.schedule_table(database.get_schedule(), database.get_trainers()),
    )

    while True:
        print("\n" + "-" * 65)
        user_input = input(
            f"הזיני הודעת זמינות עבור {chosen_trainer} (או שם מאמנת להחלפה, או Enter לסיום): "
        ).strip()

        # יציאה כאשר המשתמשת לוחצת Enter על שורה ריקה
        if not user_input:
            print("\nהתקבלה שורה ריקה. יציאה מהתוכנית. להתראות!")
            break

        # אם המשתמשת הקלידה שם מאמנת אחרת
        if user_input in trainers:
            chosen_trainer = user_input
            print(f"\nהוחלפה המאמנת הפעילה ל-{chosen_trainer}.")
            print(f"טבלת הזמינות הנוכחית של {chosen_trainer}:")
            print_table(AVAILABILITY_HEADERS, show_trainer(chosen_trainer))
            continue

        # עדכון זמינות על סמך ההודעה
        status_msg, avail_tbl, sched_tbl = update_availability(chosen_trainer, user_input)

        print("\n" + "=" * 65)
        print(f"סטטוס: {status_msg}")
        print("=" * 65)

        print(f"\nהזמינות המעודכנת של {chosen_trainer}:")
        print_table(AVAILABILITY_HEADERS, avail_tbl)

        print("\nלוח השיעורים השבועי המעודכן (עם סימון תקלות):")
        print_table(SCHEDULE_HEADERS, sched_tbl)


if __name__ == "__main__":
    main()
