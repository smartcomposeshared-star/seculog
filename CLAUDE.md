# SecuLog — Project Context

## What this is

A portfolio project for Joy's resume — a security log analysis / mini-SIEM dashboard,
chosen specifically because Joy's degree is "Digital Systems Security" but none of her
existing 3 resume projects (FamilyTracker, VibeSoles, Jarrah Honey) demonstrate any
security skills. This fills that gap and supports her target roles (IT Analyst, System
Analyst, Infrastructure Operations). All services used are free-tier — no paid plans.

Full design: `docs/superpowers/specs/2026-06-24-seculog-design.md`
Engine implementation plan: `docs/superpowers/plans/2026-06-24-seculog-detection-engine.md`
(A second plan for the Next.js dashboard will be written after the engine is built.)

## Current status (as of this session)

**The detection engine (Tasks 1–11) is COMPLETE.** All 34 tests pass. HEAD: `bbd78cb`.
Progress ledger: `.superpowers/sdd/progress.md` — always check that file and `git log`
before resuming, not this file's memory of state.

### What's done
- Task 0: Supabase project, AbuseIPDB API key, Discord webhook, GitHub repo, `.env` — done.
- Task 1: `engine/` scaffolding + `supabase/schema.sql` — done (`fc17b6f`).
- Task 2: `engine/models.py` (LoginEvent, Alert dataclasses) — done (`51825f7`).
- Task 3: `engine/rules/brute_force.py` — done (`287aa20`).
- Task 4: `engine/geo.py` + `engine/rules/impossible_travel.py` — done (`53a53fa`).
- Task 5: `engine/rules/known_bad_ip.py` — done (`0a37284`).
- Task 6: `engine/generator.py` — done (`254335e`).
- Task 7: `engine/enrichment.py` (GeoIP + AbuseIPDB) — done (`f3b3631`).
- Task 8: `engine/db.py` (Supabase module) — done (`0d96d34`).
- Task 9: `engine/alerting.py` (Discord webhook) — done (`e81700d`).
- Task 10: `engine/main.py` (orchestrator) — done (`96170f1`).
- Task 11: `.github/workflows/run-engine.yml` (hourly cron) — done (`bbd78cb`).

### Pending manual steps (Joy must do these before the engine works end-to-end)

1. **Apply the Supabase schema** — open Supabase SQL Editor, paste the full contents of
   `supabase/schema.sql` and run it. This creates `login_events` and `alerts` tables
   and adds the `username` column to `alerts`. Confirm both tables appear in Table Editor.

2. **Run the engine once locally to verify** — with `.env` populated and venv active:
   ```
   .venv\Scripts\python -m engine.main
   ```
   Expected output: `Generated 17 events, 3 total alerts, 3 new alerts sent.`
   Check Supabase Table Editor for new rows. Check Discord for 3 alert messages.

3. **Add GitHub Actions secrets** — repo → Settings → Secrets and variables → Actions.
   Add all four: `SUPABASE_URL`, `SUPABASE_KEY`, `ABUSEIPDB_API_KEY`, `DISCORD_WEBHOOK_URL`
   (same values as local `.env`).

4. **Push and trigger the workflow**:
   ```
   git push -u origin main
   ```
   Then on GitHub: Actions → "Run SecuLog Detection Engine" → Run workflow.
   Verify the Actions run log shows the summary line and Supabase/Discord receive data.

### What's next after the engine is working

Write a second plan for the Next.js dashboard (the UI half of the spec).
See `docs/superpowers/specs/2026-06-24-seculog-design.md` for the Dashboard UI section.

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
2. Ask Joy whether the 4 manual steps above are done.
3. If engine manual steps are done → write the dashboard plan, then implement it.
4. If not → help Joy through the manual steps first.
