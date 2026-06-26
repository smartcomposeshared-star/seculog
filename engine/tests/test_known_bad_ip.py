from datetime import datetime, timezone
from engine.models import LoginEvent
from engine.rules.known_bad_ip import detect_known_bad_ip

WHEN = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_flags_ip_above_threshold():
    event = LoginEvent(username="eve", ip_address="9.9.9.9", success=True, timestamp=WHEN)
    alerts = detect_known_bad_ip([event], {"9.9.9.9": 75.0})
    assert len(alerts) == 1
    assert alerts[0].rule_type == "known_bad_ip"
    assert alerts[0].severity == "medium"


def test_flags_ip_with_very_high_score_as_high_severity():
    event = LoginEvent(username="frank", ip_address="9.9.9.8", success=True, timestamp=WHEN)
    alerts = detect_known_bad_ip([event], {"9.9.9.8": 95.0})
    assert alerts[0].severity == "high"


def test_does_not_flag_ip_below_threshold():
    event = LoginEvent(username="grace", ip_address="9.9.9.7", success=True, timestamp=WHEN)
    alerts = detect_known_bad_ip([event], {"9.9.9.7": 10.0})
    assert len(alerts) == 0


def test_does_not_flag_ip_missing_from_reputation_data():
    event = LoginEvent(username="heidi", ip_address="9.9.9.6", success=True, timestamp=WHEN)
    alerts = detect_known_bad_ip([event], {})
    assert len(alerts) == 0
