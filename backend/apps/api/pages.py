from wagtail.api.v2.views import PagesAPIViewSet as WagtailPagesAPIViewSet


class PagesAPIViewSet(WagtailPagesAPIViewSet):
    """Wagtail's page endpoint plus `last_published_at`, which the sitemap uses as <lastmod>."""

    meta_fields = WagtailPagesAPIViewSet.meta_fields + ["last_published_at"]
    listing_default_fields = WagtailPagesAPIViewSet.listing_default_fields + ["last_published_at"]
