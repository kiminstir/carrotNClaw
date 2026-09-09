"""StreamField data-migration operations for `wagtail.blocks.migrations.MigrateStreamData`.

Kept outside the migration files so they can be unit tested and reused.
"""

import uuid

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


@deconstructible
class WrapSliderImagesOperation(BaseBlockOperation):
    """Turn each bare image item of an `image_slider` into the `SliderImageBlock` struct shape.

    Old items hold the ImageBlock dict (or, older still, a plain image pk); new items are
    `{"image": <that>, "caption": ""}`. Items already carrying a `caption` are left alone.
    Point `block_path_str` at the StreamBlock that contains the sliders ("" for the page body).
    """

    def apply(self, block_value):
        wrapped = []
        for child in block_value:
            if child.get("type") != "image_slider" or not isinstance(child.get("value"), dict):
                wrapped.append(child)
                continue
            items = []
            for item in child["value"].get("images", []):
                value = item.get("value")
                if isinstance(value, dict) and "caption" in value:
                    items.append(item)
                    continue
                image = {"image": value} if isinstance(value, int) else value
                items.append({**item, "value": {"image": image, "caption": ""}})
            wrapped.append({**child, "value": {**child["value"], "images": items}})
        return wrapped

    @property
    def operation_name_fragment(self):
        return "wrap_slider_images_in_struct"


@deconstructible
class WrapCardDetailImageOperation(BaseBlockOperation):
    """Turn each card's single `detail_image` into the `detail_images` ListBlock shape.

    A set image becomes a one-item list, an empty slot an empty list. Cards may be stored
    with the ListBlock item wrapper or, in seeds, as bare dicts; both are handled. Cards that
    already carry `detail_images` are left alone. Point `block_path_str` at the StreamBlock
    that contains the card grids ("" for the page body).
    """

    def apply(self, block_value):
        wrapped = []
        for child in block_value:
            if child.get("type") != "card_grid" or not isinstance(child.get("value"), dict):
                wrapped.append(child)
                continue
            cards = [self._migrate_card(card) for card in child["value"].get("cards", [])]
            wrapped.append({**child, "value": {**child["value"], "cards": cards}})
        return wrapped

    def _migrate_card(self, card):
        if not isinstance(card, dict):
            return card
        is_item = card.get("type") == "item" and isinstance(card.get("value"), dict)
        value = card["value"] if is_item else card
        if "detail_images" in value:
            return card
        rest = {k: v for k, v in value.items() if k != "detail_image"}
        image = value.get("detail_image")
        if isinstance(image, int):
            image = {"image": image}
        photos = [{"type": "item", "id": str(uuid.uuid4()), "value": image}] if image else []
        migrated = {**rest, "detail_images": photos}
        return {**card, "value": migrated} if is_item else migrated

    @property
    def operation_name_fragment(self):
        return "wrap_card_detail_image_in_list"
