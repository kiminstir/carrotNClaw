"""Error reporting through the Sentry SDK to the self-hosted Bugsink instance.

Nothing is initialised unless SENTRY_DSN is set, so local development and tests never report.
Bugsink stores errors only, hence tracing is off; PII stays on because the instance is ours and
request context is what makes an error debuggable.
"""


def sentry_options(dsn: str, environment: str, release: str) -> dict | None:
    if not dsn:
        return None
    return {
        "dsn": dsn,
        "environment": environment,
        "release": release or None,
        "traces_sample_rate": 0,
        "send_default_pii": True,
    }


def init_sentry(env) -> bool:
    """Initialise the SDK from environment variables; returns whether it was enabled."""
    options = sentry_options(
        env("SENTRY_DSN", default=""),
        env("SENTRY_ENVIRONMENT", default="development"),
        env("APP_RELEASE", default=""),
    )
    if options is None:
        return False
    import sentry_sdk

    sentry_sdk.init(**options)
    return True
