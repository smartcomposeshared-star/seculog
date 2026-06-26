from engine.models import Alert, LoginEvent


def detect_known_bad_ip(events: list[LoginEvent], ip_reputation: dict[str, float], threshold: float = 50.0) -> list[Alert]:
    alerts = []
    for event in events:
        score = ip_reputation.get(event.ip_address)
        if score is None or score <= threshold:
            continue
        alerts.append(Alert(
            login_event=event,
            rule_type="known_bad_ip",
            severity="high" if score >= 90 else "medium",
            details=f"IP {event.ip_address} has abuse confidence score {score:.0f}%",
            timestamp=event.timestamp,
        ))
    return alerts
