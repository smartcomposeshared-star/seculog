import requests

from engine.models import Alert


def send_discord_alert(webhook_url: str, alert: Alert) -> None:
    message = (
        f"**[{alert.severity.upper()}] {alert.rule_type}** — "
        f"user `{alert.login_event.username}` ({alert.login_event.ip_address})\n"
        f"{alert.details}"
    )
    try:
        requests.post(webhook_url, json={"content": message}, timeout=5)
    except requests.RequestException:
        pass
