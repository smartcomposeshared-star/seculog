from datetime import datetime, timezone
from engine.models import LoginEvent, Alert


def test_login_event_holds_required_and_optional_fields():
    event = LoginEvent(
        username="alice",
        ip_address="1.2.3.4",
        success=True,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert event.username == "alice"
    assert event.country is None
    assert event.lat is None


def test_alert_references_its_triggering_event():
    event = LoginEvent(
        username="bob", ip_address="5.6.7.8", success=False,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    alert = Alert(
        login_event=event, rule_type="brute_force", severity="high",
        details="5 failed logins", timestamp=event.timestamp,
    )
    assert alert.login_event.username == "bob"
    assert alert.rule_type == "brute_force"
