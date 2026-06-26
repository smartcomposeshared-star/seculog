from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
import requests
from engine.models import LoginEvent, Alert
from engine.alerting import send_discord_alert


@patch("engine.alerting.requests.post")
def test_sends_post_request_with_alert_details_in_message(mock_post):
    mock_post.return_value = MagicMock(status_code=204)
    event = LoginEvent(username="alice", ip_address="1.2.3.4", success=False,
                        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc))
    alert = Alert(login_event=event, rule_type="brute_force", severity="high",
                  details="6 failed logins in 45s", timestamp=event.timestamp)

    send_discord_alert("https://discord.example/webhook", alert)

    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert "alice" in kwargs["json"]["content"]
    assert "brute_force" in kwargs["json"]["content"]


@patch("engine.alerting.requests.post")
def test_does_not_raise_when_webhook_call_fails(mock_post):
    mock_post.side_effect = requests.RequestException("network down")
    event = LoginEvent(username="bob", ip_address="1.2.3.4", success=False,
                        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc))
    alert = Alert(login_event=event, rule_type="brute_force", severity="high",
                  details="test", timestamp=event.timestamp)

    send_discord_alert("https://discord.example/webhook", alert)  # must not raise
