"""Wrap plain `rich_text` HTML strings into the StyledRichTextBlock struct shape.

0002 changed the block definition; this migration converts the stored data
(live pages and every revision) so the old string values load as the new struct.
The new style keys are left out on purpose: Wagtail fills them with the block
defaults, which reproduce the previous look.
"""

from django.db import migrations
from wagtail.blocks.migrations.migrate_operation import MigrateStreamData

from apps.pages.stream_migrations import WrapRichTextOperation


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0002_alter_flexpage_body"),
    ]

    operations = [
        MigrateStreamData(
            app_name="pages",
            model_name="FlexPage",
            field_name="body",
            operations_and_block_paths=[
                (WrapRichTextOperation(), ""),
                (WrapRichTextOperation(), "columns.columns.item"),
            ],
        ),
    ]
