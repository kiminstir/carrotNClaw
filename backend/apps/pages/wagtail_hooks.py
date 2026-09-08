"""Admin customisations for the pages app."""

from wagtail.images.views import chooser as image_chooser_views

from apps.pages.forms import RichTextImageInsertionForm

# The image chooser views instantiate ``ImageInsertionForm`` by name from their
# module at request time and offer no setting to swap it, so replace it there.
# This module is imported by Wagtail's hook discovery before any admin request.
image_chooser_views.ImageInsertionForm = RichTextImageInsertionForm
