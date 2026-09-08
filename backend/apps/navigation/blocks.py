from django.core.exceptions import ValidationError
from wagtail import blocks

WEEKDAY_CHOICES = [
    ("0", "Monday"),
    ("1", "Tuesday"),
    ("2", "Wednesday"),
    ("3", "Thursday"),
    ("4", "Friday"),
    ("5", "Saturday"),
    ("6", "Sunday"),
]


class OpeningSlotBlock(blocks.StructBlock):
    """One opening on one weekday. A closing time earlier than the opening time
    means the tavern stays open past midnight into the next day."""

    day = blocks.ChoiceBlock(choices=WEEKDAY_CHOICES)
    opens = blocks.TimeBlock()
    closes = blocks.TimeBlock(
        help_text="Earlier than the opening time means the tavern stays open past midnight."
    )

    class Meta:
        icon = "time"
        label = "Opening"

    def clean(self, value):
        result = super().clean(value)
        if result["opens"] == result["closes"]:
            raise blocks.StructBlockValidationError(
                block_errors={
                    "closes": ValidationError("Closing time must differ from the opening time.")
                }
            )
        return result

    def get_api_representation(self, value, context=None):
        # Weekday as an index (Monday = 0) and times as HH:MM; the frontend does
        # the open/closed arithmetic in UTC, which is what the times are entered in.
        return {
            "day": int(value["day"]),
            "opens": value["opens"].strftime("%H:%M"),
            "closes": value["closes"].strftime("%H:%M"),
        }
