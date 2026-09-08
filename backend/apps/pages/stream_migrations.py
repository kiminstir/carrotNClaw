"""StreamField data-migration operations for `wagtail.blocks.migrations.MigrateStreamData`.

Kept outside the migration files so they can be unit tested and reused.
"""

from django.utils.deconstruct import deconstructible
from wagtail.blocks.migrations.operations import BaseBlockOperation


@deconstructible
class WrapRichTextOperation(BaseBlockOperation):
    """Turn a plain `rich_text` string child into the `StyledRichTextBlock` struct shape.

    Only the `text` key is written; the missing style keys fall back to the
    block defaults when Wagtail loads the value. Point `block_path_str` at the
    StreamBlock that contains the rich_text children ("" for the page body,
    "columns.columns.item" for text inside the Columns block).
    """

    def apply(self, block_value):
        wrapped = []
        for child in block_value:
            if child.get("type") == "rich_text" and isinstance(child.get("value"), str):
                wrapped.append({**child, "value": {"text": child["value"]}})
            else:
                wrapped.append(child)
        return wrapped

    @property
    def operation_name_fragment(self):
        return "wrap_rich_text_in_struct"
