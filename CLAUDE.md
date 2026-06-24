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

Executing the engine plan via the subagent-driven-development skill (fresh implementer
+ reviewer subagent per task). Progress ledger: `.superpowers/sdd/progress.md` —
**always check that file and `git log` before resuming, not this file's memory of state.**

- Task 0 (manual prerequisites): **done.** Supabase project, AbuseIPDB API key, Discord
  webhook, GitHub repo (`git@github.com:smartcomposeshared-star/seculog.git`) all created.
  `.env` populated at project root (gitignored, never commit it).
- Task 1 (project scaffolding + schema): **done and reviewed clean** (commit `fc17b6f`).
  `engine/` package skeleton, `engine/requirements.txt`, `supabase/schema.sql` created.
- **Pending manual step:** the Supabase schema (`supabase/schema.sql`) still needs to be
  pasted into the Supabase SQL Editor and run — Joy was given the exact SQL but hadn't
  confirmed completion when this session paused. Confirm this is done before relying on
  Task 8 (db module) working end-to-end.
- Task 2 onward (data models, 3 detection rules, generator, enrichment, db, alerting,
  orchestrator, GitHub Actions) — **not started yet.**

## Environment quirks to remember

- **Python:** installed at `C:\Users\joynew\AppData\Local\Programs\Python\Python313\`.
  The bare `python` command does NOT resolve correctly in this shell session (a Windows
  App Execution Alias stub intercepts it, and the terminal's cached PATH predates the
  install). Use the **`py`** launcher instead for everything (`py -m pytest`,
  `py -m venv .venv`, etc.) — confirmed working (`py --version` → 3.13.14). This may
  resolve itself in a fresh terminal; check `python --version` again before assuming
  the workaround is still needed.
- **Git identity:** already configured (user.name `joseph`, user.email set) — no setup
  needed.
- **Git remote:** `origin` → `git@github.com:smartcomposeshared-star/seculog.git`. Uses
  SSH — confirm SSH key/agent works before the first `git push` (Task 11 in the plan).

## How to resume

1. Read `.superpowers/sdd/progress.md` and `git log --oneline` to confirm what's
   actually committed (trust git over any written narrative).
2. Confirm the Supabase schema has been applied (ask the user, or check the Supabase
   Table Editor for `login_events` and `alerts` tables).
3. Continue subagent-driven-development from Task 2 of
   `docs/superpowers/plans/2026-06-24-seculog-detection-engine.md`.
