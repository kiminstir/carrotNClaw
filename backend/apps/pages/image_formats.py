"""Image formats used by images inserted into rich text.

Wagtail stores one ``format`` name per rich text image. The editor dialog
(see ``RichTextImageInsertionForm`` in forms.py) shows two fields, alignment
and width, and combines them into a name like ``center-50``; one Format is
registered for every combination. Wagtail discovers this module by name
(``image_formats``).

The classname ends up on the ``<img>`` in the expanded HTML the API returns;
frontend/src/app.css styles ``.prose img.richtext-image.align-*`` and
``.pct-*``; keep both in sync.

The stock formats ("fullwidth", "left", "right") stay registered so content
saved before this module existed keeps rendering; ``split_format_name`` maps
them onto the nearest alignment/width pair when such an image is re-edited.
"""

from wagtail.images.formats import Format, register_image_format

ALIGNMENTS = ["left", "center", "right"]
WIDTHS = list(range(10, 101, 10))

ALIGNMENT_CHOICES = [("left", "Left"), ("center", "Center"), ("right", "Right")]
WIDTH_CHOICES = [(str(width), f"{width}%") for width in WIDTHS]

DEFAULT_ALIGNMENT = "center"
DEFAULT_WIDTH = 100

# The prose column is 48rem (768px); render at roughly 2x the chosen fraction
# so images stay sharp on high-density screens.
_PIXELS_PER_PERCENT = 16

# Names that content may still reference but the dialog no longer offers:
# Wagtail's stock formats, and the centered percent presets that briefly
# existed before alignment and width became separate fields. Each maps to the
# nearest alignment/width pair and is registered as an alias of that format.
LEGACY_FORMATS = {
    "fullwidth": ("center", 100),
    "left": ("left", 50),
    "right": ("right", 50),
    "pct75": ("center", 80),
    "pct50": ("center", 50),
    "pct33": ("center", 30),
    "pct25": ("center", 20),
}


def format_name(align, width):
    return f"{align}-{int(width)}"


def split_format_name(name):
    """Return ``(align, width)`` for a format name, or ``None`` if unknown."""
    if not name:
        return None
    if name in LEGACY_FORMATS:
        return LEGACY_FORMATS[name]
    align, _, width = name.rpartition("-")
    if align in ALIGNMENTS and width.isdigit() and int(width) in WIDTHS:
        return align, int(width)
    return None


def _format(name, align, width):
    return Format(
        name,
        f"{align.capitalize()}, {width}%",
        f"richtext-image align-{align} pct-{width}",
        f"width-{width * _PIXELS_PER_PERCENT}",
    )


for _align in ALIGNMENTS:
    for _width in WIDTHS:
        register_image_format(_format(format_name(_align, _width), _align, _width))

for _name, (_align, _width) in LEGACY_FORMATS.items():
    if _name not in {"fullwidth", "left", "right"}:  # those three are registered by Wagtail
        register_image_format(_format(_name, _align, _width))
