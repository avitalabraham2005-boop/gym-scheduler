import unittest
from unittest.mock import patch

from source.availability_ai import parse_availability
from source.models import TimeSlot


class AvailabilityFallbackTests(unittest.TestCase):
    def test_uses_llm_result_when_available(self) -> None:
        llm_result = [TimeSlot(day="שני", part="ערב")]
        with patch(
            "source.availability_ai.availability_llm.parse_availability",
            return_value=llm_result,
        ) as llm:
            self.assertEqual(parse_availability("זמינה בשלישי בבוקר"), llm_result)
        llm.assert_called_once_with("זמינה בשלישי בבוקר")

    def test_falls_back_to_rules_when_llm_returns_no_slots(self) -> None:
        with patch("source.availability_ai.availability_llm.parse_availability", return_value=[]):
            self.assertEqual(
                parse_availability("זמינה ברביעי בבוקר ושלישי בערב"),
                [
                    TimeSlot(day="רביעי", part="בוקר"),
                    TimeSlot(day="שלישי", part="ערב"),
                ],
            )

    def test_falls_back_to_rules_when_llm_raises(self) -> None:
        with patch(
            "source.availability_ai.availability_llm.parse_availability",
            side_effect=RuntimeError("API unavailable"),
        ):
            self.assertEqual(
                parse_availability("זמינה ברביעי בבוקר"),
                [TimeSlot(day="רביעי", part="בוקר")],
            )


if __name__ == "__main__":
    unittest.main()
