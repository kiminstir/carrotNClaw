"""Turn each card's single pop-up image into the `detail_images` list.

0011 replaced `detail_image` with a `detail_images` ListBlock so the pop-up can show a
slider; this migration converts the stored data (live pages and every revision) so an
existing pop-up image becomes a one-item list and an empty slot an empty list.
"""

from django.db import migrations
from wagtail.blocks.migrations.migrate_operation import MigrateStreamData

from apps.pages.stream_migrations import WrapCardDetailImageOperation


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0011_card_detail_images"),
    ]

    operations = [
        MigrateStreamData(
            app_name="pages",
            model_name="FlexPage",
            field_name="body",
            operations_and_block_paths=[
                (WrapCardDetailImageOperation(), ""),
            ],
        ),
    ]
