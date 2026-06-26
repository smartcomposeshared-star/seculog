import os
from dotenv import load_dotenv

from engine.generator import generate_events
from engine.enrichment import geolocate_ip, check_ip_reputation, fetch_blacklisted_ip
from engine.rules.brute_force import detect_brute_force
from engine.rules.impossible_travel import detect_impossible_travel
from engine.rules.known_bad_ip import detect_known_bad_ip
from engine.db import get_client, insert_login_events, insert_alerts, has_recent_alert
from engine.alerting import send_discord_alert


def main():
    load_dotenv()
    abuseipdb_key = os.environ["ABUSEIPDB_API_KEY"]
    discord_webhook = os.environ["DISCORD_WEBHOOK_URL"]

    bad_ip = fetch_blacklisted_ip(abuseipdb_key)
    events = generate_events(num_normal_users=8, bad_ip=bad_ip)

    geo_cache, reputation_cache = {}, {}
    for event in events:
        if event.country is None:
            country, lat, lon = geolocate_ip(event.ip_address, geo_cache)
            event.country, event.lat, event.lon = country, lat, lon

    ip_reputation = {
        event.ip_address: check_ip_reputation(event.ip_address, abuseipdb_key, reputation_cache)
        for event in events
    }

    alerts = (
        detect_brute_force(events)
        + detect_impossible_travel(events)
        + detect_known_bad_ip(events, ip_reputation)
    )

    client = get_client()
    event_id_map = insert_login_events(client, events)

    new_alerts = []
    for alert in alerts:
        if has_recent_alert(client, alert.login_event.username, alert.rule_type):
            continue
        new_alerts.append(alert)

    insert_alerts(client, new_alerts, event_id_map)
    for alert in new_alerts:
        send_discord_alert(discord_webhook, alert)

    print(f"Generated {len(events)} events, {len(alerts)} total alerts, "
          f"{len(new_alerts)} new alerts sent.")


if __name__ == "__main__":
    main()
