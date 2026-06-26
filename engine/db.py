import os
from datetime import datetime, timedelta, timezone
from supabase import create_client


def get_client():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def insert_login_events(client, events):
    rows = [{
        "username": e.username,
        "ip_address": e.ip_address,
        "success": e.success,
        "country": e.country,
        "lat": e.lat,
        "lon": e.lon,
        "timestamp": e.timestamp.isoformat(),
    } for e in events]
    result = client.table("login_events").insert(rows).execute()
    return {id(event): row["id"] for event, row in zip(events, result.data)}


def insert_alerts(client, alerts, event_id_map):
    if not alerts:
        return
    rows = [{
        "login_event_id": event_id_map[id(alert.login_event)],
        "rule_type": alert.rule_type,
        "severity": alert.severity,
        "details": alert.details,
        "timestamp": alert.timestamp.isoformat(),
        "username": alert.login_event.username,
    } for alert in alerts]
    client.table("alerts").insert(rows).execute()


def has_recent_alert(client, username, rule_type, within_minutes=60):
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=within_minutes)).isoformat()
    result = (
        client.table("alerts")
        .select("id")
        .eq("rule_type", rule_type)
        .eq("username", username)
        .gte("timestamp", cutoff)
        .execute()
    )
    return len(result.data) > 0
