# SecuLog — Security Log Analysis & Mini-SIEM Dashboard

**Date:** 2026-06-24
**Status:** Approved design, pending implementation plan

## Purpose

A portfolio project demonstrating security-monitoring and detection skills, aimed at
strengthening a resume for IT Analyst / System Analyst / Infrastructure Operations roles.
It directly supports the "Digital Systems Security" degree specialization, which is not
otherwise demonstrated by any existing project.

The system simulates login activity, runs three rule-based detection checks against it,
stores results in a database, displays them on a simple read-only dashboard, and pushes
real-time alerts to Discord when something suspicious is flagged.

## Architecture

```
Python Engine (generates fake logins, runs 3 detection rules)
        |
        v
Supabase (Postgres, free tier) — login_events, alerts
        |                              |
        v                              v
Discord Webhook (free)          Next.js Dashboard (Vercel, free)
(alert notifications)           (reads & displays events/alerts)
```

- **Python engine**: scheduled via free GitHub Actions cron (e.g. every 15 minutes).
  Each run generates a batch of simulated login events and immediately evaluates them
  against the three detection rules.
- **Supabase**: free-tier Postgres database, single source of truth for all events and
  alerts.
- **Next.js + TypeScript dashboard**: deployed free on Vercel. Read-only — it queries
  Supabase and renders data. It does not perform any detection logic itself.
- **Discord webhook**: free Discord server + webhook URL; the Python engine posts a
  message whenever a rule fires.

## Data Model

### `login_events`
| column | type | meaning |
|---|---|---|
| id | uuid | unique ID |
| username | text | fake identity used for the login attempt |
| ip_address | text | source IP |
| country, lat, lon | text/float | from free GeoIP lookup on the IP |
| success | boolean | whether the login succeeded |
| timestamp | timestamptz | when the event occurred |

### `alerts`
| column | type | meaning |
|---|---|---|
| id | uuid | unique ID |
| login_event_id | uuid (FK) | links back to the triggering event |
| rule_type | text | `brute_force` \| `impossible_travel` \| `known_bad_ip` |
| severity | text | low / medium / high |
| details | text | human-readable explanation (e.g. "6 failed logins in 45s") |
| timestamp | timestamptz | when the alert was created |

## Detection Rules (MVP scope: 3 rules)

1. **Brute-force login attempts** — group recent failed logins by username; if the same
   username has 5+ failed logins within 60 seconds, create a `brute_force` alert
   (severity: high).
2. **Impossible travel** — for each username, compare its two most recent login
   locations (lat/lon) and the time gap between them; if the implied travel speed
   exceeds ~900 km/h (faster than a commercial flight), create an `impossible_travel`
   alert (severity: high).
3. **Known-bad IP** — check each login's IP against AbuseIPDB (free tier, ~1,000
   checks/day); if the abuse confidence score exceeds 50%, create a `known_bad_ip` alert
   (severity: medium-high).

Additional rules (off-hours access, privilege escalation) are explicitly out of scope
for the MVP and noted as future additions.

### Simulated data generation

The Python engine invents a small set of fake identities and generates both normal and
deliberately suspicious login events:
- A handful of "normal" fake users with consistent login patterns (same general
  location, occasional logins).
- Planted scenarios on each run to guarantee each rule has something to detect:
  - One fake user receives 6+ rapid failed logins (triggers brute-force).
  - One fake user logs in from two distant locations minutes apart (triggers impossible
    travel).
  - One fake login uses a known public test "bad" IP from AbuseIPDB's sample list
    (triggers known-bad-IP).

The exact number and style of fake users (names, realism, login frequency) is a tunable
detail to be decided during implementation, not fixed by this spec.

## Dashboard UI

Two pages only, with a simple top nav — intentionally minimal, no settings or
configuration screens, everything read-only:

**Page 1 — Overview (default/home page)**
- Summary cards: total logins today, active alerts, alerts-by-type breakdown.
- Alert feed: list/table, most recent first, color-coded by severity (red = high,
  yellow = medium), each row showing time, rule type, username/IP, and a short
  explanation.
- A small map showing recent login locations, suspicious ones highlighted in red.

**Page 2 — All Events (raw log)**
- A plain table of every login event (success/fail, IP, location, time), for viewing
  the full picture behind any alert.

## Error Handling & Reliability

- **API rate limits/downtime** (AbuseIPDB, GeoIP lookup): results are cached per IP
  after first lookup. If a call fails or times out, the engine logs it and skips
  enrichment for that event rather than failing the whole run.
- **Duplicate alerts**: before creating a new alert, the engine checks whether an alert
  for that username/rule was already created recently, to avoid re-flagging an ongoing
  incident on every run.
- **Database write issues**: a failed Supabase insert is retried once, then logged and
  skipped rather than halting the batch.
- **Scheduling drift**: GitHub Actions free-tier cron may run a few minutes late; this
  is acceptable for a demo project and requires no special handling.

## Testing Approach

- The three detection rules are pure functions (event list in, alerts out) and are
  covered by unit tests using hand-crafted fixtures (e.g., "given these 6 failed
  logins, does it flag brute force?"). External API calls (GeoIP, IP reputation) are
  stubbed in these tests.
- The dashboard is read-only display and is verified manually in the browser rather
  than via automated tests, matching its low complexity.

## Tech Stack & Free Services

| Purpose | Service | Free tier basis |
|---|---|---|
| Detection engine | Python | n/a |
| Scheduling | GitHub Actions cron | free for public/private repos within usage limits |
| Database | Supabase (Postgres) | free tier |
| Dashboard | Next.js + TypeScript, hosted on Vercel | free tier |
| Alerting | Discord webhook | free |
| IP reputation | AbuseIPDB API | free tier (~1,000 checks/day) |
| Geolocation | Free IP geolocation API (e.g. ip-api.com) | free for non-commercial use |

## Out of Scope (future additions)

- Off-hours / unusual access time detection rule.
- Privilege escalation pattern detection rule.
- Real public security log dataset ingestion (currently simulated data only).
- Email alerting (Discord webhook only for MVP).
