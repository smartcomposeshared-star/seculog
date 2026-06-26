from datetime import datetime, timedelta, timezone
from engine.models import LoginEvent
from engine.rules.impossible_travel import detect_impossible_travel

BASE = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_flags_singapore_to_moscow_in_five_minutes():
    events = [
        LoginEvent(username="carol", ip_address="1.1.1.1", success=True,
                   timestamp=BASE, country="Singapore", lat=1.3521, lon=103.8198),
        LoginEvent(username="carol", ip_address="2.2.2.2", success=True,
                   timestamp=BASE + timedelta(minutes=5), country="Russia",
                   lat=55.7558, lon=37.6173),
    ]
    alerts = detect_impossible_travel(events)
    assert len(alerts) == 1
    assert alerts[0].rule_type == "impossible_travel"


def test_does_not_flag_nearby_login_five_hours_later():
    events = [
        LoginEvent(username="dave", ip_address="1.1.1.1", success=True,
                   timestamp=BASE, lat=1.3521, lon=103.8198),
        LoginEvent(username="dave", ip_address="1.1.1.1", success=True,
                   timestamp=BASE + timedelta(hours=5), lat=1.36, lon=103.83),
    ]
    alerts = detect_impossible_travel(events)
    assert len(alerts) == 0


def test_ignores_events_without_coordinates():
    events = [
        LoginEvent(username="erin", ip_address="1.1.1.1", success=True, timestamp=BASE),
        LoginEvent(username="erin", ip_address="2.2.2.2", success=True,
                   timestamp=BASE + timedelta(minutes=1)),
    ]
    alerts = detect_impossible_travel(events)
    assert len(alerts) == 0
