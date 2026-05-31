import os


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.casefold() in {"1", "true", "yes", "on"}


IRAIL_BASE_URL = os.getenv("IRAIL_BASE_URL", "https://api.irail.be/v1")
IRAIL_FORMAT = "json"
IRAIL_LANGUAGE = "en"
IRAIL_TIMEOUT_SECONDS = 10.0
IRAIL_USER_AGENT = "lagovia-train-tracker/0.1"
IRAIL_FOLLOW_REDIRECTS = True
IRAIL_TRUST_ENV = _env_bool("IRAIL_TRUST_ENV", False)

DEPARTURE_WINDOW_MINUTES = 15
QUERY_MIN_LENGTH = 3
