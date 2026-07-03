# SecuLog — Project Context

## What this is

A portfolio project for Joy's resume — a security log analysis / mini-SIEM dashboard,
chosen specifically because Joy's degree is "Digital Systems Security" but none of her
existing 3 resume projects (FamilyTracker, VibeSoles, Jarrah Honey) demonstrate any
security skills. This fills that gap and supports her target roles (IT Analyst, System
Analyst, Infrastructure Operations). All services used are free-tier — no paid plans.

Full design: `docs/superpowers/specs/2026-06-24-seculog-design.md`
Engine implementation plan: `docs/superpowers/plans/2026-06-24-seculog-detection-engine.md`
Dashboard implementation plan: `docs/superpowers/plans/2026-07-03-seculog-dashboard.md`

## Current status (as of 2026-07-04)

**Both the detection engine AND the Next.js dashboard are COMPLETE.** HEAD: `9bec88c`.
Progress ledger: `.superpowers/sdd/progress.md` — always check that file and `git log`
before resuming, not this file's memory of state.

### Engine — fully done
All Tasks 0–11 complete, 34 tests pass, hourly GitHub Actions cron verified running
(workflow run #35 succeeded 2026-07-03). Discord alerts and Supabase rows confirmed.

### Dashboard — code complete, Vercel deploy pending
8 commits pushed (`fe7f158..9bec88c`). Files:
- `dashboard/src/app/layout.tsx` — dark nav (Overview / All Events)
- `dashboard/src/app/page.tsx` — Overview page (dynamic, fetches locations + alert IDs)
- `dashboard/src/app/events/page.tsx` — All Events page (200 rows, newest first)
- `dashboard/src/components/SummaryCards.tsx` — logins today / total alerts / by type
- `dashboard/src/components/AlertFeed.tsx` — color-coded alert feed (red=high, yellow=medium)
- `dashboard/src/components/LoginMap.tsx` — react-leaflet map (client component)
- `dashboard/src/components/LoginMapClient.tsx` — ssr:false wrapper (required by Next.js 16)
- `dashboard/src/components/EventsTable.tsx` — login events table
- `dashboard/src/lib/supabase.ts` — Supabase client singleton
- `dashboard/src/lib/types.ts` — LoginEvent, Alert, MapLocation

### Pending manual step — Joy must do this

**Deploy to Vercel:**
1. Go to vercel.com → Add New → Project → import `smartcomposeshared-star/seculog`
2. Root Directory → `dashboard`
3. Add env vars: `SUPABASE_URL` and `SUPABASE_ANON_KEY` (anon public key from Supabase
   Project Settings → API — different from the service_role key used by the engine)
4. Deploy → verify live URL shows real data

**Also:** update `dashboard/.env.local` with the real `SUPABASE_ANON_KEY` for local dev.

### What's next after Vercel is live

The project is complete. Add the live Vercel URL to the GitHub README and Joy's resume.

## Environment quirks to remember

- **Python:** Use the **`py`** launcher (`py -m pytest`, etc.) — the bare `python` command
  may not resolve on this machine due to a Windows App Execution Alias stub. Confirmed
  working: `py --version` → 3.13.x. Check `python --version` in a fresh terminal first.
- **Venv:** `.venv\Scripts\python -m pytest` or activate with `.venv\Scripts\activate`
  before using `py -m pytest`.
- **Git identity:** configured (user.name `joseph`) — no setup needed.
- **Git remote:** `origin` → `git@github.com:smartcomposeshared-star/seculog.git`. SSH —
  confirm key/agent works before first `git push`.

## How to resume

1. Read `.superpowers/sdd/progress.md` and `git log --oneline` to confirm actual state.
2. Ask Joy whether Vercel deployment is done (the one remaining step).
3. If yes → project is complete; help Joy add the URL to README and resume.
4. If not → walk Joy through the Vercel deploy steps listed above.
