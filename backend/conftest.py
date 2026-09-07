import shutil

import pytest
from django.conf import settings


@pytest.fixture(autouse=True, scope="session")
def _clean_test_media():
    yield
    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
