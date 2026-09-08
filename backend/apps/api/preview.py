"""Vendored preview API viewset.

The installed `wagtail-headless-preview` (0.9.0) ships `HeadlessMixin` /
`PagePreview` (see `wagtail_headless_preview.models`) but no longer ships an
importable `wagtail_headless_preview.api` module — its README instead
documents this exact viewset for projects to copy into their own codebase.
Vendored here per the project's Wagtail 8.0 API viewset conventions, with
`get_object`/`detail_view` unchanged from the upstream recipe.
"""

from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from rest_framework.response import Response
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail_headless_preview.models import PagePreview


class PagePreviewAPIViewSet(PagesAPIViewSet):
    known_query_parameters = PagesAPIViewSet.known_query_parameters.union(["content_type", "token"])

    def listing_view(self, request):
        # Delegate to detail_view, specifically so there's no
        # difference between serialization formats.
        self.action = "detail_view"
        return self.detail_view(request, 0)

    def detail_view(self, request, pk):
        page = self.get_object()
        serializer = self.get_serializer(page)
        return Response(serializer.data)

    def get_object(self):
        try:
            app_label, model = self.request.GET["content_type"].split(".")
        except ValueError as exc:
            raise Http404("Malformed content_type.") from exc

        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist as exc:
            raise Http404("Unknown content_type.") from exc

        try:
            page_preview = PagePreview.objects.get(
                content_type=content_type, token=self.request.GET["token"]
            )
        except PagePreview.DoesNotExist as exc:
            raise Http404("Unknown or expired preview token.") from exc

        page = page_preview.as_page()
        if not page.pk:
            # fake primary key to stop API URL routing from complaining
            page.pk = 0

        return page
