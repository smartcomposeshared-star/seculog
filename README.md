# SecuLog — Security Log Analysis & Mini-SIEM Dashboard

**Live demo:** [seculog.vercel.app](https://seculog.vercel.app)

A mini SIEM (Security Information and Event Management) system that simulates login
activity, runs rule-based threat detection against it, and surfaces the results on a
real-time dashboard with Discord alerting — the kind of pipeline a SOC analyst works
with day to day, built end-to-end on free-tier infrastructure.

## What it does

A Python engine generates simulated login events (normal traffic plus a few deliberately
suspicious patterns), evaluates each batch against three detection rules, and persists
results to Postgres. A Next.js dashboard reads that data and renders login locations,
alert history, and summary stats. High-severity alerts also post to Discord in real time.

**Detection rules:**
- **Brute-force login attempts** — 5+ failed logins for the same username within 60 seconds
- **Impossible travel** — two logins for the same user, geographically too far apart to
  be reached in the time between them (>900 km/h implied speed)
- **Known-bad IP** — source IP has an AbuseIPDB confidence score above 50%

## Architecture

```
Python engine (GitHub Actions cron, hourly)
  → generates simulated login events
  → runs 3 detection rules
  → geolocates IPs, checks AbuseIPDB
        │
        ▼
Supabase (Postgres)  ──────────────►  Discord webhook (real-time alerts)
        │
        ▼
Next.js dashboard (Vercel)
  - Overview: summary cards, login location map, alert feed
  - All Events: full login event history
```

## Tech stack

- **Detection engine:** Python, pytest, GitHub Actions (scheduled cron)
- **Database:** Supabase (Postgres), Row Level Security with public read policies
- **Dashboard:** Next.js, TypeScript, Tailwind CSS, react-leaflet
- **Alerting:** Discord webhooks
- **Hosting:** Vercel (dashboard), GitHub Actions (engine) — all free tier

## Project structure

```
engine/       Python detection engine (rules, geo/abuse enrichment, alerting, orchestrator)
dashboard/    Next.js dashboard (App Router)
supabase/     Database schema
docs/         Design spec and implementation plans
```

## Running locally

**Engine:**
```bash
py -m venv .venv && .venv\Scripts\activate
pip install -r engine/requirements.txt
py -m pytest
py -m engine.main
```

**Dashboard:**
```bash
cd dashboard
npm install
npm run dev
```

Both require a `.env` (engine) / `.env.local` (dashboard) with Supabase credentials —
see `dashboard/.env.local` for the expected variable names.
