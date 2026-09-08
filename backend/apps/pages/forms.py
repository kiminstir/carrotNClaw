from django import forms
from wagtail.images.forms import ImageInsertionForm

from apps.pages.image_formats import (
    ALIGNMENT_CHOICES,
    DEFAULT_ALIGNMENT,
    DEFAULT_WIDTH,
    WIDTH_CHOICES,
    format_name,
    split_format_name,
)


class RichTextImageInsertionForm(ImageInsertionForm):
    """Rich text image dialog with separate alignment and width fields.

    Wagtail's own form exposes one "Format" radio list. This form replaces it
    with alignment and width and writes the combined format name back into
    ``cleaned_data["format"]``, which is what the chooser view reads.
    Installed by wagtail_hooks.py.
    """

    format = None  # drop the inherited field
    align = forms.ChoiceField(
        label="Alignment",
        choices=ALIGNMENT_CHOICES,
        initial=DEFAULT_ALIGNMENT,
        widget=forms.RadioSelect,
    )
    width = forms.ChoiceField(label="Width", choices=WIDTH_CHOICES, initial=str(DEFAULT_WIDTH))

    field_order = ["align", "width", "image_is_decorative", "alt_text"]

    def __init__(self, *args, **kwargs):
        # When an existing image is edited the chooser passes its current
        # format name as initial data; show it as the two fields.
        initial = dict(kwargs.get("initial") or {})
        parts = split_format_name(initial.pop("format", None))
        if parts is not None:
            initial.setdefault("align", parts[0])
            initial.setdefault("width", str(parts[1]))
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("align") and cleaned.get("width"):
            cleaned["format"] = format_name(cleaned["align"], cleaned["width"])
        return cleaned
