from collections import defaultdict
from datetime import timedelta
from engine.models import Alert


def detect_brute_force(events, threshold=5, window_seconds=60):
    alerts = []
    failed_by_user = defaultdict(list)
    for event in events:
        if not event.success:
            failed_by_user[event.username].append(event)

    window = timedelta(seconds=window_seconds)
    for username, fails in failed_by_user.items():
        fails.sort(key=lambda e: e.timestamp)
        start = 0
        for end in range(len(fails)):
            while fails[end].timestamp - fails[start].timestamp > window:
                start += 1
            count = end - start + 1
            if count >= threshold:
                alerts.append(Alert(
                    login_event=fails[end],
                    rule_type="brute_force",
                    severity="high",
                    details=f"{count} failed logins for '{username}' within {window_seconds}s",
                    timestamp=fails[end].timestamp,
                ))
                break
    return alerts
