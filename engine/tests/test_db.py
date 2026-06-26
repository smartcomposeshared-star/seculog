from datetime import datetime, timedelta, timezone
from engine.models import LoginEvent, Alert
from engine.db import insert_login_events, insert_alerts, has_recent_alert


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self, name, store):
        self.name = name
        self.store = store
        self._filters = []

    def insert(self, rows):
        inserted = []
        for row in rows:
            row = dict(row)
            row["id"] = f"id-{len(self.store[self.name])}"
            self.store[self.name].append(row)
            inserted.append(row)
        self._pending = inserted
        return self

    def select(self, *_args, **_kwargs):
        self._pending = list(self.store[self.name])
        return self

    def eq(self, key, value):
        self._pending = [r for r in self._pending if r.get(key) == value]
        return self

    def gte(self, key, value):
        self._pending = [r for r in self._pending if r.get(key, "") >= value]
        return self

    def execute(self):
        return FakeResult(self._pending)


class FakeClient:
    def __init__(self):
        self.store = {"login_events": [], "alerts": []}

    def table(self, name):
        return FakeTable(name, self.store)


WHEN = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_insert_login_events_returns_id_per_event():
    client = FakeClient()
    events = [
        LoginEvent(username="alice", ip_address="1.1.1.1", success=True, timestamp=WHEN),
        LoginEvent(username="bob", ip_address="2.2.2.2", success=False, timestamp=WHEN),
    ]
    id_map = insert_login_events(client, events)
    assert len(id_map) == 2
    assert id(events[0]) in id_map
    assert id(events[1]) in id_map


def test_insert_alerts_links_to_correct_event_id():
    client = FakeClient()
    event = LoginEvent(username="alice", ip_address="1.1.1.1", success=False, timestamp=WHEN)
    id_map = insert_login_events(client, [event])
    alert = Alert(login_event=event, rule_type="brute_force", severity="high",
                  details="test", timestamp=WHEN)
    insert_alerts(client, [alert], id_map)
    assert len(client.store["alerts"]) == 1
    assert client.store["alerts"][0]["login_event_id"] == id_map[id(event)]


def test_insert_alerts_does_nothing_for_empty_list():
    client = FakeClient()
    insert_alerts(client, [], {})
    assert client.store["alerts"] == []


def test_has_recent_alert_true_when_match_exists():
    client = FakeClient()
    recent_time = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    client.store["alerts"].append({
        "id": "a1", "login_event_id": "e1", "rule_type": "brute_force",
        "username": "alice", "timestamp": recent_time,
    })
    assert has_recent_alert(client, "alice", "brute_force") is True


def test_has_recent_alert_false_when_no_match():
    client = FakeClient()
    assert has_recent_alert(client, "alice", "brute_force") is False


def test_has_recent_alert_false_when_alert_is_stale():
    client = FakeClient()
    stale_time = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    client.store["alerts"].append({
        "id": "a2", "login_event_id": "e1", "rule_type": "brute_force",
        "username": "alice", "timestamp": stale_time,
    })
    assert has_recent_alert(client, "alice", "brute_force") is False
