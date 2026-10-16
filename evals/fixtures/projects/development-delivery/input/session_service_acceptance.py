from datetime import datetime, timedelta, timezone

from session_service import validate_session


now = datetime(2030, 1, 1, tzinfo=timezone.utc)
assert validate_session(now - timedelta(seconds=1), now) == "SESSION_EXPIRED"
assert validate_session(now + timedelta(seconds=1), now) == "ACTIVE"
