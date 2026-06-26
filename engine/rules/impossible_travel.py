from engine.geo import haversine_km
from engine.models import Alert


def detect_impossible_travel(events, max_speed_kmh=900.0):
    alerts = []
    by_user = {}
    for event in events:
        if event.lat is None or event.lon is None:
            continue
        by_user.setdefault(event.username, []).append(event)

    for username, user_events in by_user.items():
        user_events.sort(key=lambda e: e.timestamp)
        for prev, curr in zip(user_events, user_events[1:]):
            hours = (curr.timestamp - prev.timestamp).total_seconds() / 3600.0
            if hours <= 0:
                continue
            distance_km = haversine_km(prev.lat, prev.lon, curr.lat, curr.lon)
            speed_kmh = distance_km / hours
            if speed_kmh > max_speed_kmh:
                alerts.append(Alert(
                    login_event=curr,
                    rule_type="impossible_travel",
                    severity="high",
                    details=(
                        f"'{username}' traveled {distance_km:.0f}km in "
                        f"{hours:.2f}h ({speed_kmh:.0f} km/h)"
                    ),
                    timestamp=curr.timestamp,
                ))
    return alerts
