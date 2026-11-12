"""טיפוסי הנתונים של המערכת: משבצת זמן, מאמנת ושיעור."""

from dataclasses import dataclass, field

DAYS = ["ראשון", "שני", "שלישי", "רביעי", "חמישי", "שישי"]
PARTS_OF_DAY = ["בוקר", "צהריים", "ערב"]


@dataclass(frozen=True)
class TimeSlot:
    """משבצת זמן: יום בשבוע + חלק ביום. למשל: רביעי, בוקר."""

    day: str
    part: str


@dataclass
class Trainer:
    """מאמנת: השם שלה, אילו שיעורים היא מעבירה, ומתי היא זמינה."""

    name: str
    classes: list[str]
    availability: set[TimeSlot] = field(default_factory=set)


@dataclass
class GymClass:
    """שיעור קבוע בלוח השבועי."""

    name: str
    slot: TimeSlot
    hour: str
    trainer: str