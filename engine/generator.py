import random
from datetime import datetime, timedelta, timezone
from engine.models import LoginEvent

NORMAL_LOCATIONS = [
    ("Singapore", 1.3521, 103.8198),
    ("Singapore", 1.2800, 103.8500),
]


def generate_events(num_normal_users=8, bad_ip="185.220.101.1", seed=None):
    rng = random.Random(seed)
    now = datetime.now(timezone.utc)
    events = []

    for i in range(num_normal_users):
        country, lat, lon = NORMAL_LOCATIONS[i % len(NORMAL_LOCATIONS)]
        events.append(LoginEvent(
            username=f"user{i + 1}",
            ip_address=f"203.0.113.{i + 1}",
            success=True,
            timestamp=now - timedelta(minutes=rng.randint(0, 60)),
            country=country, lat=lat, lon=lon,
        ))

    for i in range(6):
        events.append(LoginEvent(
            username="attacker_bf",
            ip_address="198.51.100.50",
            success=False,
            timestamp=now - timedelta(seconds=50 - i * 8),
        ))

    events.append(LoginEvent(
        username="traveler_it", ip_address="203.0.113.99", success=True,
        timestamp=now - timedelta(minutes=10),
        country="Singapore", lat=1.3521, lon=103.8198,
    ))
    events.append(LoginEvent(
        username="traveler_it", ip_address="198.51.100.77", success=True,
        timestamp=now - timedelta(minutes=5),
        country="Russia", lat=55.7558, lon=37.6173,
    ))

    events.append(LoginEvent(
        username="visitor_bip", ip_address=bad_ip, success=True,
        timestamp=now - timedelta(minutes=2),
    ))

    return events
