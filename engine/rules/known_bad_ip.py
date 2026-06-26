from engine.models import Alert


def detect_known_bad_ip(events, ip_reputation, threshold=50.0):
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
