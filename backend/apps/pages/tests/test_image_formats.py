import pytest
from django.urls import reverse
from wagtail.images.formats import get_image_format, get_image_formats
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.rich_text import expand_db_html

from apps.pages.blocks import StyledRichTextBlock
from apps.pages.forms import RichTextImageInsertionForm
from apps.pages.image_formats import ALIGNMENTS, WIDTHS, format_name, split_format_name


@pytest.fixture
def image(db):
    return Image.objects.create(title="Hall", file=get_test_image_file(size=(1200, 800)))


def test_every_alignment_and_width_combination_is_registered():
    names = {fmt.name for fmt in get_image_formats()}
    expected = {format_name(align, width) for align in ALIGNMENTS for width in WIDTHS}
    assert expected <= names
    assert len(expected) == 30
    # Stock formats stay registered so existing content keeps rendering.
    assert {"fullwidth", "left", "right"} <= names


def test_widths_run_from_10_to_100_in_steps_of_10():
    assert WIDTHS == list(range(10, 101, 10))
    assert ALIGNMENTS == ["left", "center", "right"]


@pytest.mark.parametrize("align", ["left", "center", "right"])
@pytest.mark.parametrize("width", [10, 50, 100])
def test_format_classname_matches_frontend_css(align, width):
    fmt = get_image_format(format_name(align, width))
    assert fmt.classname == f"richtext-image align-{align} pct-{width}"
    assert fmt.filter_spec.startswith("width-")


LEGACY_PERCENT_FORMATS = {"pct75": 80, "pct50": 50, "pct33": 30, "pct25": 20}


@pytest.mark.parametrize(("legacy", "width"), LEGACY_PERCENT_FORMATS.items())
def test_legacy_percent_formats_alias_the_nearest_new_format(legacy, width):
    # Drafts saved with the short-lived pct* formats must still open and render.
    assert get_image_format(legacy).classname == f"richtext-image align-center pct-{width}"
    assert split_format_name(legacy) == ("center", width)


def test_editor_opens_rich_text_with_a_legacy_percent_image(image):
    from wagtail.admin.rich_text.converters.contentstate import ContentstateConverter

    from apps.pages.blocks import RICH_TEXT_FEATURES

    converter = ContentstateConverter(features=RICH_TEXT_FEATURES)
    db_html = f'<embed embedtype="image" id="{image.pk}" format="pct33" alt="Hall"/>'
    contentstate = converter.from_database_format(db_html)
    assert '"format": "pct33"' in contentstate


def test_split_format_name_round_trips_and_maps_stock_formats():
    assert split_format_name("right-70") == ("right", 70)
    assert split_format_name("fullwidth") == ("center", 100)
    assert split_format_name("left") == ("left", 50)
    assert split_format_name("right") == ("right", 50)
    assert split_format_name("bogus") is None
    assert split_format_name(None) is None


def test_insertion_form_shows_align_and_width_instead_of_format():
    form = RichTextImageInsertionForm(prefix="image-chooser-insertion")
    assert "format" not in form.fields
    assert list(form.fields) == ["align", "width", "image_is_decorative", "alt_text"]
    assert [value for value, _ in form.fields["width"].choices] == [str(w) for w in WIDTHS]


def test_insertion_form_combines_fields_into_a_format_name():
    form = RichTextImageInsertionForm(
        {
            "image-chooser-insertion-align": "left",
            "image-chooser-insertion-width": "30",
            "image-chooser-insertion-alt_text": "Hall",
        },
        prefix="image-chooser-insertion",
    )
    assert form.is_valid(), form.errors
    assert form.cleaned_data["format"] == "left-30"


def test_insertion_form_defaults_to_centered_full_width():
    form = RichTextImageInsertionForm(prefix="image-chooser-insertion")
    assert form["align"].value() == "center"
    assert form["width"].value() == "100"


def test_insertion_form_preselects_fields_when_editing_an_existing_image():
    form = RichTextImageInsertionForm(initial={"format": "right-70", "alt_text": "x"})
    assert form["align"].value() == "right"
    assert form["width"].value() == "70"

    legacy = RichTextImageInsertionForm(initial={"format": "left", "alt_text": "x"})
    assert (legacy["align"].value(), legacy["width"].value()) == ("left", "50")


@pytest.mark.django_db
def test_admin_select_format_dialog_uses_the_two_field_form(client, django_user_model, image):
    admin = django_user_model.objects.create_superuser("admin", "a@example.com", "pw")
    client.force_login(admin)
    url = reverse("wagtailimages_chooser:select_format", args=(image.pk,))
    response = client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 200
    body = response.content.decode()
    assert 'name="image-chooser-insertion-align"' in body.replace("\\", "")
    assert 'name="image-chooser-insertion-width"' in body.replace("\\", "")
    assert 'name="image-chooser-insertion-format"' not in body.replace("\\", "")


@pytest.mark.django_db
def test_admin_select_format_post_returns_combined_format(client, django_user_model, image):
    admin = django_user_model.objects.create_superuser("admin", "a@example.com", "pw")
    client.force_login(admin)
    url = reverse("wagtailimages_chooser:select_format", args=(image.pk,))
    response = client.post(
        url,
        {
            "image-chooser-insertion-align": "right",
            "image-chooser-insertion-width": "40",
            "image-chooser-insertion-alt_text": "Hall",
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["step"] == "chosen"
    assert data["result"]["format"] == "right-40"
    assert data["result"]["class"] == "richtext-image align-right pct-40"


def test_rich_text_image_embed_expands_with_align_and_width_classes(image):
    db_html = f'<p>Hi</p><embed embedtype="image" id="{image.pk}" format="center-50" alt="Hall"/>'
    html = expand_db_html(db_html)
    assert 'class="richtext-image align-center pct-50"' in html
    assert 'alt="Hall"' in html


def test_rich_text_block_api_output_carries_the_classes(image):
    block = StyledRichTextBlock()
    value = block.to_python(
        {"text": f'<embed embedtype="image" id="{image.pk}" format="left-20" alt="Hall"/>'}
    )
    assert "richtext-image align-left pct-20" in block.get_api_representation(value)["text"]
