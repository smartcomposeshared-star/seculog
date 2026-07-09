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

## Current status (as of 2026-07-10)

**PROJECT COMPLETE.** Engine, dashboard, Vercel deploy, and README are all done and
live at https://seculog.vercel.app. HEAD: `62d2a3a`.
Progress ledger: `.superpowers/sdd/progress.md` — always check that file and `git log`
before resuming, not this file's memory of state.

### Post-deploy fixes (2026-07-09/10)
- Vercel deployed successfully (Root Directory `dashboard`, env vars `SUPABASE_URL` /
  `SUPABASE_ANON_KEY` set to the anon public key).
- Fixed: RLS was enabled on `alerts`/`login_events` with zero policies, so the anon key
  got empty results everywhere even though the engine's data was there. Added public
  SELECT policies for `anon` on both tables via Supabase SQL Editor (not yet reflected
  in `supabase/schema.sql` — do that if touching the schema file again).
- Fixed: "Logins Today" card text had no explicit color, invisible against dark card
  background (`0402c6f`).
- Changed: timestamps now render in Singapore time, `dd/mm/yyyy` format, via
  `dashboard/src/lib/format.ts`; "Logins Today" boundary also aligned to SGT calendar
  day instead of server UTC (`368c3b9`).
- Added root `README.md` with live demo link, architecture, and local setup (`62d2a3a`).
- `dashboard/.env.local` now has real Supabase anon key for local dev (gitignored).

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

### What's next

Nothing required. Optional: add the live URL to Joy's resume (already in the README).

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

Project is complete. If Joy returns with a new request, read
`.superpowers/sdd/progress.md` and `git log --oneline` to confirm current state before
making changes — this file's memory can go stale.
