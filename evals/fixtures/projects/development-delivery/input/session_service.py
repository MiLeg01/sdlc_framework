from datetime import datetime


def validate_session(expires_at: datetime, now: datetime) -> str:
    return "ACTIVE"
