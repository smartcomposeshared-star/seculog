from datetime import datetime, timedelta, timezone
from engine.models import LoginEvent
from engine.rules.brute_force import detect_brute_force


def _failed_login(username, seconds_offset):
    base = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return LoginEvent(
        username=username, ip_address="198.51.100.50", success=False,
        timestamp=base + timedelta(seconds=seconds_offset),
    )


def test_flags_five_failed_logins_within_60_seconds():
    events = [_failed_login("alice", i * 10) for i in range(5)]
    alerts = detect_brute_force(events)
    assert len(alerts) == 1
    assert alerts[0].rule_type == "brute_force"
    assert alerts[0].severity == "high"


def test_does_not_flag_four_failed_logins():
    events = [_failed_login("bob", i * 10) for i in range(4)]
    alerts = detect_brute_force(events)
    assert len(alerts) == 0


def test_does_not_flag_successful_logins():
    base = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    events = [
        LoginEvent(username="carol", ip_address="1.1.1.1", success=True,
                   timestamp=base + timedelta(seconds=i * 5))
        for i in range(6)
    ]
    alerts = detect_brute_force(events)
    assert len(alerts) == 0


def test_does_not_flag_failed_logins_spread_over_five_minutes():
    events = [_failed_login("dave", i * 90) for i in range(5)]
    alerts = detect_brute_force(events)
    assert len(alerts) == 0
