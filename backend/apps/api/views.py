from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.api.serializers import (
    serialize_footer,
    serialize_header,
    serialize_hours,
    serialize_music,
)
from apps.music.models import MusicSettings
from apps.navigation.models import FooterSettings, HeaderSettings, OpeningHoursSettings


class SiteSettingsAPIView(APIView):
    """Header menu, footer, opening hours and music playlist in one call."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        context = {"request": request}
        return Response(
            {
                "header": serialize_header(HeaderSettings.load(request_or_site=request), context),
                "footer": serialize_footer(FooterSettings.load(request_or_site=request), context),
                "hours": serialize_hours(
                    OpeningHoursSettings.load(request_or_site=request), context
                ),
                "music": serialize_music(MusicSettings.load(request_or_site=request), context),
            }
        )
