# SecuLog Detection Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Python detection engine half of SecuLog: a script that generates simulated login events, runs three rule-based detection checks, stores results in Supabase, and posts alerts to Discord — runnable locally and on a GitHub Actions schedule.

**Architecture:** A pure-logic core (data models + 3 detection rules) is developed with TDD and has zero network dependencies, so it's fully unit-testable. Network-touching concerns (GeoIP lookup, IP reputation, Supabase writes, Discord webhook) are isolated into their own modules and wired together only in `main.py`. This keeps the rules — the most important and reusable part of the project — simple, deterministic, and fast to test.

**Tech Stack:** Python 3.11+, pytest, `requests`, `supabase-py`. Free services: Supabase (Postgres), AbuseIPDB API (free tier), ip-api.com (free GeoIP), Discord webhook, GitHub Actions (free cron).

## Global Constraints

- All services used must be free-tier — no paid plans, no credit card requiring services beyond free tiers that are credit-card-free where possible.
- Detection rule functions must take plain data in and return alerts out — no network calls inside `engine/rules/*.py`.
- Brute-force threshold: 5+ failed logins within 60 seconds (per spec).
- Impossible travel threshold: implied speed > 900 km/h (per spec).
- Known-bad-IP threshold: AbuseIPDB abuse confidence score > 50% (per spec).
- All code lives under `engine/` at the project root.

---

## Task 0: Manual Prerequisites (you, not the engineer)

These are signups only you can do (account creation, email verification). Do these before Task 1.

- [ ] **Step 1: Create a Supabase project**
  Go to https://supabase.com, sign up free, create a new project. From Project Settings → API, copy the **Project URL** and the **service_role key** (not the anon key — we need write access from a server-side script). Save them somewhere temporarily; Task 1 will need them.

- [ ] **Step 2: Get a free AbuseIPDB API key**
  Go to https://www.abuseipdb.com/register, sign up free, then go to Account → API Key and copy your key.

- [ ] **Step 3: Create a Discord webhook**
  In Discord, create a free server (or use an existing one), go to a channel → Edit Channel → Integrations → Webhooks → New Webhook. Copy the webhook URL.

- [ ] **Step 4: Create the GitHub repo**
  Create a new empty repository on GitHub (e.g. `seculog`). Locally, run:
  ```bash
  cd C:\Users\joynew\AIProjects\Fourth-project
  git init
  git remote add origin <your-repo-url>
  ```

- [ ] **Step 5: Store secrets**
  Locally, create a `.env` file at the project root (already covered by `.gitignore` in Task 1 — never commit this file):
  ```
  SUPABASE_URL=<your project url>
  SUPABASE_KEY=<your service_role key>
  ABUSEIPDB_API_KEY=<your key>
  DISCORD_WEBHOOK_URL=<your webhook url>
  ```
  Later (Task 10), the same four values get added as GitHub Actions repository secrets (Settings → Secrets and variables → Actions) so the scheduled run can use them.

---

## Task 1: Project Scaffolding and Database Schema

**Files:**
- Create: `.gitignore`
- Create: `engine/requirements.txt`
- Create: `engine/__init__.py`
- Create: `engine/rules/__init__.py`
- Create: `engine/tests/__init__.py`
- Create: `supabase/schema.sql`

**Interfaces:**
- Produces: the `login_events` and `alerts` tables that every later task reads/writes.

- [ ] **Step 1: Create `.gitignore`**

```
.env
__pycache__/
*.pyc
.pytest_cache/
node_modules/
.next/
```

- [ ] **Step 2: Create `engine/requirements.txt`**

```
requests==2.32.3
supabase==2.9.1
python-dotenv==1.0.1
pytest==8.3.3
```

- [ ] **Step 3: Create empty package init files**

Create `engine/__init__.py`, `engine/rules/__init__.py`, `engine/tests/__init__.py` — all empty files.

- [ ] **Step 4: Write the schema**

Create `supabase/schema.sql`:

```sql
create table login_events (
  id uuid primary key default gen_random_uuid(),
  username text not null,
  ip_address text not null,
  success boolean not null,
  country text,
  lat double precision,
  lon double precision,
  "timestamp" timestamptz not null
);

create table alerts (
  id uuid primary key default gen_random_uuid(),
  login_event_id uuid not null references login_events(id),
  rule_type text not null,
  severity text not null,
  details text not null,
  "timestamp" timestamptz not null
);

create index idx_alerts_username_rule on alerts (rule_type, timestamp);
create index idx_login_events_username on login_events (username, timestamp);
```

- [ ] **Step 5: Apply the schema (manual)**

In the Supabase dashboard, open SQL Editor, paste the contents of `supabase/schema.sql`, and run it. Confirm both tables appear under Table Editor.

- [ ] **Step 6: Install dependencies and verify pytest runs**

```bash
cd C:\Users\joynew\AIProjects\Fourth-project
python -m venv .venv
.venv\Scripts\activate
pip install -r engine/requirements.txt
python -m pytest engine/tests -v
```
Expected: "no tests ran" (no test files yet) — confirms pytest and deps are installed correctly, not an error.

- [ ] **Step 7: Commit**

```bash
git add .gitignore engine/requirements.txt engine/__init__.py engine/rules/__init__.py engine/tests/__init__.py supabase/schema.sql
git commit -m "chore: scaffold engine project and database schema"
```

---

## Task 2: Data Models

**Files:**
- Create: `engine/models.py`
- Test: `engine/tests/test_models.py`

**Interfaces:**
- Produces: `LoginEvent(username, ip_address, success, timestamp, country=None, lat=None, lon=None)` and `Alert(login_event, rule_type, severity, details, timestamp)` — both plain dataclasses, used by every later task.

- [ ] **Step 1: Write the failing test**

Create `engine/tests/test_models.py`:

```python
from datetime import datetime, timezone
from engine.models import LoginEvent, Alert


def test_login_event_holds_required_and_optional_fields():
    event = LoginEvent(
        username="alice",
        ip_address="1.2.3.4",
        success=True,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert event.username == "alice"
    assert event.country is None
    assert event.lat is None


def test_alert_references_its_triggering_event():
    event = LoginEvent(
        username="bob", ip_address="5.6.7.8", success=False,
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    alert = Alert(
        login_event=event, rule_type="brute_force", severity="high",
        details="5 failed logins", timestamp=event.timestamp,
    )
    assert alert.login_event.username == "bob"
    assert alert.rule_type == "brute_force"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest engine/tests/test_models.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.models'`

- [ ] **Step 3: Write minimal implementation**

Create `engine/models.py`:

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LoginEvent:
    username: str
    ip_address: str
    success: bool
    timestamp: datetime
    country: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


@dataclass
class Alert:
    login_event: LoginEvent
    rule_type: str
    severity: str
    details: str
    timestamp: datetime
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest engine/tests/test_models.py -v
```
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/models.py engine/tests/test_models.py
git commit -m "feat: add LoginEvent and Alert data models"
```

---

## Task 3: Brute-Force Detection Rule

**Files:**
- Create: `engine/rules/brute_force.py`
- Test: `engine/tests/test_brute_force.py`

**Interfaces:**
- Consumes: `LoginEvent` from `engine.models` (Task 2).
- Produces: `detect_brute_force(events: list[LoginEvent], threshold: int = 5, window_seconds: int = 60) -> list[Alert]`, used by `main.py` (Task 9) and the generator's own integration test (Task 6).

- [ ] **Step 1: Write the failing tests**

Create `engine/tests/test_brute_force.py`:

```python
from datetime import datetime, timedelta, timezone
from engine.models import LoginEvent
from engine.rules.brute_force import detect_brute_force


def _failed_login(username, seconds_offset):
    base = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return LoginEvent(
        username=username, ip_address="198.51.100.50", success=False,
        timestamp=base + timedelta(seconds=seconds_offset),
    )


def test_flags_five_failed_logins_within_60_seconds():
    events = [_failed_login("alice", i * 10) for i in range(5)]
    alerts = detect_brute_force(events)
    assert len(alerts) == 1
    assert alerts[0].rule_type == "brute_force"
    assert alerts[0].severity == "high"


def test_does_not_flag_four_failed_logins():
    events = [_failed_login("bob", i * 10) for i in range(4)]
    alerts = detect_brute_force(events)
    assert len(alerts) == 0


def test_does_not_flag_successful_logins():
    base = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    events = [
        LoginEvent(username="carol", ip_address="1.1.1.1", success=True,
                   timestamp=base + timedelta(seconds=i * 5))
        for i in range(6)
    ]
    alerts = detect_brute_force(events)
    assert len(alerts) == 0


def test_does_not_flag_failed_logins_spread_over_five_minutes():
    events = [_failed_login("dave", i * 90) for i in range(5)]
    alerts = detect_brute_force(events)
    assert len(alerts) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest engine/tests/test_brute_force.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.rules.brute_force'`

- [ ] **Step 3: Write minimal implementation**

Create `engine/rules/brute_force.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest engine/tests/test_brute_force.py -v
```
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/rules/brute_force.py engine/tests/test_brute_force.py
git commit -m "feat: add brute-force detection rule"
```

---

## Task 4: Impossible Travel Detection Rule

**Files:**
- Create: `engine/geo.py`
- Create: `engine/rules/impossible_travel.py`
- Test: `engine/tests/test_geo.py`
- Test: `engine/tests/test_impossible_travel.py`

**Interfaces:**
- Produces: `haversine_km(lat1, lon1, lat2, lon2) -> float` (in `engine.geo`, also used by Task 7's enrichment caching logic if needed) and `detect_impossible_travel(events: list[LoginEvent], max_speed_kmh: float = 900.0) -> list[Alert]`.
- Consumes: `LoginEvent`, `Alert` from `engine.models`.

- [ ] **Step 1: Write the failing test for the distance helper**

Create `engine/tests/test_geo.py`:

```python
from engine.geo import haversine_km


def test_distance_between_singapore_and_moscow_is_about_8400km():
    distance = haversine_km(1.3521, 103.8198, 55.7558, 37.6173)
    assert 8300 < distance < 8500


def test_distance_between_same_point_is_zero():
    distance = haversine_km(1.35, 103.82, 1.35, 103.82)
    assert distance == 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest engine/tests/test_geo.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.geo'`

- [ ] **Step 3: Write minimal implementation**

Create `engine/geo.py`:

```python
import math


def haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radius_km * math.asin(math.sqrt(a))
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest engine/tests/test_geo.py -v
```
Expected: PASS (2 passed)

- [ ] **Step 5: Commit the geo helper**

```bash
git add engine/geo.py engine/tests/test_geo.py
git commit -m "feat: add haversine distance helper"
```

- [ ] **Step 6: Write the failing tests for the rule**

Create `engine/tests/test_impossible_travel.py`:

```python
from datetime import datetime, timedelta, timezone
from engine.models import LoginEvent
from engine.rules.impossible_travel import detect_impossible_travel

BASE = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_flags_singapore_to_moscow_in_five_minutes():
    events = [
        LoginEvent(username="carol", ip_address="1.1.1.1", success=True,
                   timestamp=BASE, country="Singapore", lat=1.3521, lon=103.8198),
        LoginEvent(username="carol", ip_address="2.2.2.2", success=True,
                   timestamp=BASE + timedelta(minutes=5), country="Russia",
                   lat=55.7558, lon=37.6173),
    ]
    alerts = detect_impossible_travel(events)
    assert len(alerts) == 1
    assert alerts[0].rule_type == "impossible_travel"


def test_does_not_flag_nearby_login_five_hours_later():
    events = [
        LoginEvent(username="dave", ip_address="1.1.1.1", success=True,
                   timestamp=BASE, lat=1.3521, lon=103.8198),
        LoginEvent(username="dave", ip_address="1.1.1.1", success=True,
                   timestamp=BASE + timedelta(hours=5), lat=1.36, lon=103.83),
    ]
    alerts = detect_impossible_travel(events)
    assert len(alerts) == 0


def test_ignores_events_without_coordinates():
    events = [
        LoginEvent(username="erin", ip_address="1.1.1.1", success=True, timestamp=BASE),
        LoginEvent(username="erin", ip_address="2.2.2.2", success=True,
                   timestamp=BASE + timedelta(minutes=1)),
    ]
    alerts = detect_impossible_travel(events)
    assert len(alerts) == 0
```

- [ ] **Step 7: Run tests to verify they fail**

```bash
python -m pytest engine/tests/test_impossible_travel.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.rules.impossible_travel'`

- [ ] **Step 8: Write minimal implementation**

Create `engine/rules/impossible_travel.py`:

```python
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
```

- [ ] **Step 9: Run tests to verify they pass**

```bash
python -m pytest engine/tests/test_impossible_travel.py -v
```
Expected: PASS (3 passed)

- [ ] **Step 10: Commit**

```bash
git add engine/rules/impossible_travel.py engine/tests/test_impossible_travel.py
git commit -m "feat: add impossible travel detection rule"
```

---

## Task 5: Known-Bad-IP Detection Rule

**Files:**
- Create: `engine/rules/known_bad_ip.py`
- Test: `engine/tests/test_known_bad_ip.py`

**Interfaces:**
- Consumes: `LoginEvent`, `Alert` from `engine.models`.
- Produces: `detect_known_bad_ip(events: list[LoginEvent], ip_reputation: dict[str, float], threshold: float = 50.0) -> list[Alert]`. `ip_reputation` is a plain `{ip_address: abuse_confidence_score}` dict — Task 7's enrichment module is responsible for building it; this rule never calls the network itself.

- [ ] **Step 1: Write the failing tests**

Create `engine/tests/test_known_bad_ip.py`:

```python
from datetime import datetime, timezone
from engine.models import LoginEvent
from engine.rules.known_bad_ip import detect_known_bad_ip

WHEN = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_flags_ip_above_threshold():
    event = LoginEvent(username="eve", ip_address="9.9.9.9", success=True, timestamp=WHEN)
    alerts = detect_known_bad_ip([event], {"9.9.9.9": 75.0})
    assert len(alerts) == 1
    assert alerts[0].rule_type == "known_bad_ip"
    assert alerts[0].severity == "medium"


def test_flags_ip_with_very_high_score_as_high_severity():
    event = LoginEvent(username="frank", ip_address="9.9.9.8", success=True, timestamp=WHEN)
    alerts = detect_known_bad_ip([event], {"9.9.9.8": 95.0})
    assert alerts[0].severity == "high"


def test_does_not_flag_ip_below_threshold():
    event = LoginEvent(username="grace", ip_address="9.9.9.7", success=True, timestamp=WHEN)
    alerts = detect_known_bad_ip([event], {"9.9.9.7": 10.0})
    assert len(alerts) == 0


def test_does_not_flag_ip_missing_from_reputation_data():
    event = LoginEvent(username="heidi", ip_address="9.9.9.6", success=True, timestamp=WHEN)
    alerts = detect_known_bad_ip([event], {})
    assert len(alerts) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest engine/tests/test_known_bad_ip.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.rules.known_bad_ip'`

- [ ] **Step 3: Write minimal implementation**

Create `engine/rules/known_bad_ip.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest engine/tests/test_known_bad_ip.py -v
```
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/rules/known_bad_ip.py engine/tests/test_known_bad_ip.py
git commit -m "feat: add known-bad-IP detection rule"
```

---

## Task 6: Simulated Event Generator

**Files:**
- Create: `engine/generator.py`
- Test: `engine/tests/test_generator.py`

**Interfaces:**
- Consumes: `LoginEvent` from `engine.models`; `detect_brute_force`, `detect_impossible_travel` from Tasks 3-4 (only inside this task's own integration test, to prove the planted scenarios are actually detectable).
- Produces: `generate_events(num_normal_users: int = 8, bad_ip: str = "185.220.101.1", seed: int | None = None) -> list[LoginEvent]`, used by `main.py` (Task 10).

- [ ] **Step 1: Write the failing tests**

Create `engine/tests/test_generator.py`:

```python
from engine.generator import generate_events
from engine.rules.brute_force import detect_brute_force
from engine.rules.impossible_travel import detect_impossible_travel


def test_generates_expected_total_event_count():
    events = generate_events(num_normal_users=3, seed=42)
    # 3 normal + 6 brute-force attempts + 2 impossible-travel logins + 1 bad-ip login
    assert len(events) == 3 + 6 + 2 + 1


def test_planted_brute_force_scenario_is_detectable():
    events = generate_events(num_normal_users=3, seed=42)
    alerts = detect_brute_force(events)
    assert len(alerts) == 1
    assert alerts[0].login_event.username == "attacker_bf"


def test_planted_impossible_travel_scenario_is_detectable():
    events = generate_events(num_normal_users=3, seed=42)
    alerts = detect_impossible_travel(events)
    assert len(alerts) == 1
    assert alerts[0].login_event.username == "traveler_it"


def test_planted_bad_ip_login_uses_the_given_bad_ip():
    events = generate_events(num_normal_users=3, bad_ip="1.2.3.4", seed=42)
    bad_ip_events = [e for e in events if e.ip_address == "1.2.3.4"]
    assert len(bad_ip_events) == 1
    assert bad_ip_events[0].username == "visitor_bip"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest engine/tests/test_generator.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.generator'`

- [ ] **Step 3: Write minimal implementation**

Create `engine/generator.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest engine/tests/test_generator.py -v
```
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/generator.py engine/tests/test_generator.py
git commit -m "feat: add simulated login event generator with planted detection scenarios"
```

---

## Task 7: Enrichment (GeoIP + IP Reputation)

**Files:**
- Create: `engine/enrichment.py`
- Test: `engine/tests/test_enrichment.py`

**Interfaces:**
- Produces:
  - `geolocate_ip(ip_address: str, cache: dict) -> tuple[str | None, float | None, float | None]`
  - `check_ip_reputation(ip_address: str, api_key: str, cache: dict) -> float`
  - `fetch_blacklisted_ip(api_key: str, fallback_ip: str = "185.220.101.1") -> str`
  - Used by `main.py` (Task 10). `cache` is a plain dict the caller owns and reuses across calls in the same run, per the spec's caching requirement.

- [ ] **Step 1: Write the failing tests**

Create `engine/tests/test_enrichment.py`:

```python
from unittest.mock import patch, MagicMock
from engine.enrichment import geolocate_ip, check_ip_reputation, fetch_blacklisted_ip


@patch("engine.enrichment.requests.get")
def test_geolocate_ip_returns_country_and_coordinates(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {
        "status": "success", "country": "Singapore", "lat": 1.35, "lon": 103.82,
    })
    country, lat, lon = geolocate_ip("1.2.3.4", cache={})
    assert country == "Singapore"
    assert lat == 1.35
    assert lon == 103.82


@patch("engine.enrichment.requests.get")
def test_geolocate_ip_uses_cache_on_second_call(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {
        "status": "success", "country": "Singapore", "lat": 1.35, "lon": 103.82,
    })
    cache = {}
    geolocate_ip("1.2.3.4", cache)
    geolocate_ip("1.2.3.4", cache)
    assert mock_get.call_count == 1


@patch("engine.enrichment.requests.get")
def test_geolocate_ip_handles_failed_lookup(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {"status": "fail"})
    country, lat, lon = geolocate_ip("0.0.0.0", cache={})
    assert country is None and lat is None and lon is None


@patch("engine.enrichment.requests.get")
def test_check_ip_reputation_returns_score(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {
        "data": {"abuseConfidenceScore": 87},
    })
    score = check_ip_reputation("9.9.9.9", api_key="fake", cache={})
    assert score == 87.0


@patch("engine.enrichment.requests.get")
def test_check_ip_reputation_defaults_to_zero_on_error(mock_get):
    mock_get.side_effect = Exception("network down")
    score = check_ip_reputation("9.9.9.9", api_key="fake", cache={})
    assert score == 0.0


@patch("engine.enrichment.requests.get")
def test_fetch_blacklisted_ip_returns_an_ip_from_the_list(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {
        "data": [{"ipAddress": "203.0.113.200"}],
    })
    ip = fetch_blacklisted_ip(api_key="fake")
    assert ip == "203.0.113.200"


@patch("engine.enrichment.requests.get")
def test_fetch_blacklisted_ip_falls_back_on_error(mock_get):
    mock_get.side_effect = Exception("network down")
    ip = fetch_blacklisted_ip(api_key="fake", fallback_ip="1.1.1.1")
    assert ip == "1.1.1.1"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest engine/tests/test_enrichment.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.enrichment'`

- [ ] **Step 3: Write minimal implementation**

Create `engine/enrichment.py`:

```python
import requests

GEO_API_URL = "http://ip-api.com/json/{ip}"
ABUSEIPDB_CHECK_URL = "https://api.abuseipdb.com/api/v2/check"
ABUSEIPDB_BLACKLIST_URL = "https://api.abuseipdb.com/api/v2/blacklist"


def geolocate_ip(ip_address, cache):
    if ip_address in cache:
        return cache[ip_address]
    try:
        data = requests.get(GEO_API_URL.format(ip=ip_address), timeout=5).json()
        if data.get("status") == "success":
            result = (data.get("country"), data.get("lat"), data.get("lon"))
        else:
            result = (None, None, None)
    except requests.RequestException:
        result = (None, None, None)
    cache[ip_address] = result
    return result


def check_ip_reputation(ip_address, api_key, cache):
    if ip_address in cache:
        return cache[ip_address]
    try:
        data = requests.get(
            ABUSEIPDB_CHECK_URL,
            params={"ipAddress": ip_address, "maxAgeInDays": 90},
            headers={"Key": api_key, "Accept": "application/json"},
            timeout=5,
        ).json()
        score = float(data["data"]["abuseConfidenceScore"])
    except (requests.RequestException, KeyError, ValueError, TypeError):
        score = 0.0
    cache[ip_address] = score
    return score


def fetch_blacklisted_ip(api_key, fallback_ip="185.220.101.1"):
    try:
        data = requests.get(
            ABUSEIPDB_BLACKLIST_URL,
            params={"confidenceMinimum": 90, "limit": 1},
            headers={"Key": api_key, "Accept": "application/json"},
            timeout=5,
        ).json()
        return data["data"][0]["ipAddress"]
    except (requests.RequestException, KeyError, IndexError, TypeError):
        return fallback_ip
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest engine/tests/test_enrichment.py -v
```
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/enrichment.py engine/tests/test_enrichment.py
git commit -m "feat: add GeoIP and AbuseIPDB enrichment with caching"
```

---

## Task 8: Database Module (Supabase)

**Files:**
- Create: `engine/db.py`
- Test: `engine/tests/test_db.py`

**Interfaces:**
- Consumes: `LoginEvent`, `Alert` from `engine.models`.
- Produces:
  - `get_client() -> Client` (reads `SUPABASE_URL`, `SUPABASE_KEY` from environment)
  - `insert_login_events(client, events: list[LoginEvent]) -> dict[int, str]` (keyed by `id(event)`, valued by the new DB row's UUID)
  - `insert_alerts(client, alerts: list[Alert], event_id_map: dict[int, str]) -> None`
  - `has_recent_alert(client, username: str, rule_type: str, within_minutes: int = 15) -> bool`
  - Used by `main.py` (Task 10).

This task mocks the Supabase client entirely in tests (no real network/DB calls in the test suite) by passing in a fake client object that mimics the chainable `.table().insert().execute()` interface.

- [ ] **Step 1: Write the failing tests**

Create `engine/tests/test_db.py`:

```python
from datetime import datetime, timezone
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
    client.store["alerts"].append({
        "id": "a1", "login_event_id": "e1", "rule_type": "brute_force",
        "username": "alice", "timestamp": "2026-01-01T12:00:00+00:00",
    })
    assert has_recent_alert(client, "alice", "brute_force") is True


def test_has_recent_alert_false_when_no_match():
    client = FakeClient()
    assert has_recent_alert(client, "alice", "brute_force") is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest engine/tests/test_db.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.db'`

- [ ] **Step 3: Write minimal implementation**

Create `engine/db.py`:

```python
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


def has_recent_alert(client, username, rule_type, within_minutes=15):
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
```

Note: `username` is stored directly on the `alerts` row (denormalized) so `has_recent_alert` can filter without a join — simpler than the foreign-table embed syntax, at the cost of one duplicated column. Add this column to `supabase/schema.sql` from Task 1:

```sql
alter table alerts add column username text not null default '';
```

- [ ] **Step 4: Apply the schema change (manual)**

In the Supabase SQL Editor, run the `alter table` statement above.

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest engine/tests/test_db.py -v
```
Expected: PASS (5 passed)

- [ ] **Step 6: Commit**

```bash
git add engine/db.py engine/tests/test_db.py supabase/schema.sql
git commit -m "feat: add Supabase database module for events and alerts"
```

---

## Task 9: Discord Alerting

**Files:**
- Create: `engine/alerting.py`
- Test: `engine/tests/test_alerting.py`

**Interfaces:**
- Consumes: `Alert` from `engine.models`.
- Produces: `send_discord_alert(webhook_url: str, alert: Alert) -> None`, used by `main.py` (Task 10).

- [ ] **Step 1: Write the failing tests**

Create `engine/tests/test_alerting.py`:

```python
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
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
    mock_post.side_effect = Exception("network down")
    event = LoginEvent(username="bob", ip_address="1.2.3.4", success=False,
                        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc))
    alert = Alert(login_event=event, rule_type="brute_force", severity="high",
                  details="test", timestamp=event.timestamp)

    send_discord_alert("https://discord.example/webhook", alert)  # must not raise
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest engine/tests/test_alerting.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.alerting'`

- [ ] **Step 3: Write minimal implementation**

Create `engine/alerting.py`:

```python
import requests


def send_discord_alert(webhook_url, alert):
    message = (
        f"**[{alert.severity.upper()}] {alert.rule_type}** — "
        f"user `{alert.login_event.username}` ({alert.login_event.ip_address})\n"
        f"{alert.details}"
    )
    try:
        requests.post(webhook_url, json={"content": message}, timeout=5)
    except requests.RequestException:
        pass
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest engine/tests/test_alerting.py -v
```
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add engine/alerting.py engine/tests/test_alerting.py
git commit -m "feat: add Discord webhook alerting"
```

---

## Task 10: Main Orchestrator

**Files:**
- Create: `engine/main.py`

**Interfaces:**
- Consumes everything from Tasks 2-9: `generate_events`, `detect_brute_force`, `detect_impossible_travel`, `detect_known_bad_ip`, `geolocate_ip`, `check_ip_reputation`, `fetch_blacklisted_ip`, `get_client`, `insert_login_events`, `insert_alerts`, `has_recent_alert`, `send_discord_alert`.
- Produces: a `main()` function and `if __name__ == "__main__":` entry point — this is the script GitHub Actions (Task 11) runs on a schedule. No unit test; verified by the manual end-to-end check in Step 2 below, since it's pure wiring with no new logic of its own.

- [ ] **Step 1: Write `engine/main.py`**

```python
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
```

- [ ] **Step 2: Run it manually end-to-end**

With `.env` populated (Task 0, Step 5) and your venv active:

```bash
python -m engine.main
```
Expected: prints a summary line like `Generated 17 events, 3 total alerts, 3 new alerts sent.` Check the Supabase Table Editor for new rows in `login_events` and `alerts`, and check your Discord channel for 3 new alert messages.

- [ ] **Step 3: Run the full test suite once more**

```bash
python -m pytest engine/tests -v
```
Expected: all tests pass (only `main.py` itself is untested, by design — see Interfaces note above).

- [ ] **Step 4: Commit**

```bash
git add engine/main.py
git commit -m "feat: wire up main orchestrator for detection engine"
```

---

## Task 11: Scheduled Runs via GitHub Actions

**Files:**
- Create: `.github/workflows/run-engine.yml`

**Interfaces:**
- Consumes: `engine/main.py` (Task 10) and the four GitHub Actions secrets set up in Step 1 below.

- [ ] **Step 1: Add repository secrets (manual)**

On GitHub, go to your repo → Settings → Secrets and variables → Actions → New repository secret. Add all four, using the same values from your local `.env`:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `ABUSEIPDB_API_KEY`
- `DISCORD_WEBHOOK_URL`

- [ ] **Step 2: Write the workflow**

Create `.github/workflows/run-engine.yml`:

```yaml
name: Run SecuLog Detection Engine

on:
  schedule:
    - cron: "*/15 * * * *"
  workflow_dispatch: {}

jobs:
  run-engine:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r engine/requirements.txt
      - run: python -m engine.main
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          ABUSEIPDB_API_KEY: ${{ secrets.ABUSEIPDB_API_KEY }}
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
```

- [ ] **Step 3: Push and trigger manually**

```bash
git add .github/workflows/run-engine.yml
git commit -m "ci: schedule detection engine runs via GitHub Actions"
git push -u origin main
```
Then on GitHub, go to Actions → Run SecuLog Detection Engine → Run workflow (uses `workflow_dispatch`, so you don't have to wait 15 minutes for the cron).

- [ ] **Step 4: Verify**

Check the Actions run log for the same summary line printed in Task 10, Step 2. Check Supabase and Discord for new rows/messages from this run.

---

## Plan Self-Review Notes

- **Spec coverage:** all 3 detection rules (Task 3-5), simulated data generation with planted scenarios (Task 6), GeoIP + AbuseIPDB enrichment with caching (Task 7), Supabase storage (Task 1, 8), Discord alerting (Task 9), duplicate-alert suppression (Task 8's `has_recent_alert`, wired in Task 10), GitHub Actions scheduling (Task 11) are all covered. The dashboard (spec's "Dashboard UI" section) is intentionally out of scope — covered by a separate plan.
- **Type consistency:** `LoginEvent`/`Alert` field names introduced in Task 2 are used identically through Tasks 3-10 (`username`, `ip_address`, `success`, `timestamp`, `country`, `lat`, `lon`, `rule_type`, `severity`, `details`, `login_event`). `ip_reputation` dict shape (`{ip: score}`) is consistent between Task 5's rule and Task 10's orchestrator.
- **No placeholders:** every step has complete, runnable code; no "add error handling" type steps remain unfilled.
