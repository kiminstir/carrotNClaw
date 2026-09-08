"""Wrap each image_slider image into the SliderImageBlock struct shape.

0009 changed the block definition so every slide carries an optional caption; this
migration converts the stored data (live pages and every revision) so the old bare image
items load as the new struct, with an empty caption.
"""

from django.db import migrations
from wagtail.blocks.migrations.migrate_operation import MigrateStreamData

from apps.pages.stream_migrations import WrapSliderImagesOperation


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0009_slider_image_captions"),
    ]

    operations = [
        MigrateStreamData(
            app_name="pages",
            model_name="FlexPage",
            field_name="body",
            operations_and_block_paths=[
                (WrapSliderImagesOperation(), ""),
            ],
        ),
    ]
