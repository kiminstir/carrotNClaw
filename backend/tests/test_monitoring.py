from unittest import mock

from config.monitoring import init_sentry, sentry_options


def test_no_dsn_means_no_options():
    assert sentry_options("", "develop", "sha-abc1234") is None


def test_options_keep_errors_only():
    options = sentry_options("https://key@bugs.example.com/1", "develop", "sha-abc1234")
    assert options == {
        "dsn": "https://key@bugs.example.com/1",
        "environment": "develop",
        "release": "sha-abc1234",
        "traces_sample_rate": 0,
        "send_default_pii": True,
    }


def test_empty_release_is_omitted():
    options = sentry_options("https://key@bugs.example.com/1", "develop", "")
    assert options["release"] is None


def _env(values):
    return lambda name, default="": values.get(name, default)


def test_init_is_skipped_without_dsn():
    with mock.patch("sentry_sdk.init") as init:
        assert init_sentry(_env({})) is False
    init.assert_not_called()


def test_init_uses_environment_values():
    env = _env(
        {
            "SENTRY_DSN": "https://key@bugs.example.com/1",
            "SENTRY_ENVIRONMENT": "develop",
            "APP_RELEASE": "sha-abc1234",
        }
    )
    with mock.patch("sentry_sdk.init") as init:
        assert init_sentry(env) is True
    init.assert_called_once_with(
        dsn="https://key@bugs.example.com/1",
        environment="develop",
        release="sha-abc1234",
        traces_sample_rate=0,
        send_default_pii=True,
    )
