"""סקריפט בדיקה לפענוח הודעות זמינות מול תוצאות צפויות והדפסת טבלת השוואה."""

import sys

try:
    from source.availability_ai import parse_availability
    from source.models import DAYS, PARTS_OF_DAY, TimeSlot
except ImportError:
    from availability_ai import parse_availability
    from models import DAYS, PARTS_OF_DAY, TimeSlot

TEST_CASES: list[tuple[str, list[TimeSlot]]] = [
    (
        "זמינה ברביעי בבוקר ושלישי בערב",
        [
            TimeSlot(day="רביעי", part="בוקר"),
            TimeSlot(day="שלישי", part="ערב"),
        ],
    ),
    (
        "זמינה ביון רביעי בבוקר",
        [
            TimeSlot(day="רביעי", part="בוקר"),
        ],
    ),
    (
        "כל השבוע חוץ משישי, רק בערבים",
        [
            TimeSlot(day="ראשון", part="ערב"),
            TimeSlot(day="שני", part="ערב"),
            TimeSlot(day="שלישי", part="ערב"),
            TimeSlot(day="רביעי", part="ערב"),
            TimeSlot(day="חמישי", part="ערב"),
        ],
    ),
]


def _sort_slots(slots: list[TimeSlot]) -> list[TimeSlot]:
    """ממיין משבצות זמן לפי סדר ימות השבוע וחלקי היום לתצוגה אחידה."""
    day_order = {day: idx for idx, day in enumerate(DAYS)}
    part_order = {part: idx for idx, part in enumerate(PARTS_OF_DAY)}
    return sorted(
        slots,
        key=lambda s: (day_order.get(s.day, 99), part_order.get(s.part, 99)),
    )


def _format_slots(slots: list[TimeSlot]) -> str:
    """ממיר רשימת משבצות זמן למחרוזת קריאה לתצוגה בטבלה."""
    ordered = _sort_slots(slots)
    if not ordered:
        return "[]"
    return ", ".join(f"({slot.day}, {slot.part})" for slot in ordered)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    rows: list[tuple[str, str, str, str]] = []
    for message, expected in TEST_CASES:
        actual = parse_availability(message)
        is_match = set(actual) == set(expected)
        rows.append(
            (
                message,
                _format_slots(expected),
                _format_slots(actual),
                "תואם" if is_match else "לא תואם",
            )
        )

    headers = ("הודעה", "תוצאה צפויה", "תוצאה בפועל", "תואם או לא")
    col_widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    def format_row(cols: tuple[str, str, str, str]) -> str:
        return " | ".join(col.ljust(col_widths[i]) for i, col in enumerate(cols))

    separator = "-+-".join("-" * w for w in col_widths)
    print("\n" + format_row(headers))
    print(separator)
    for row in rows:
        print(format_row(row))


if __name__ == "__main__":
    main()
