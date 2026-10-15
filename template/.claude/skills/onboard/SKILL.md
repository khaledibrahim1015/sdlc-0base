---
name: onboard
description: Adopts an existing codebase. Reverse-documents the as-is architecture into docs/architecture.md, recovers implicit decisions as retroactive ADRs, records the build/test baseline, fills AGENTS.md Commands, seeds PLAN.md. Run once, in the first session on an existing project.
disable-model-invocation: true
---

# Onboard an existing codebase

The codebase is the research subject. One pass. The docs it produces are
what every later session reads instead of rescanning the repo.

## When to use

- First session on an existing project.
- NOT for greenfield (fill PLAN.md and start) or for repos you are only
  evaluating (use repo-evaluation in a hub).

## Procedure

1. Dispatch ONE repo-analyst subagent on this codebase with the question
   "what IS this system?". Report path: docs/eval/self-onboard.md.
   From here on, read the report, not the repo.
2. Spot-check 2-3 citations from the report against the code. If any is
   wrong, treat the report as suspect and ask the subagent to redo that
   section.
3. Write docs/architecture.md following
   `.claude/skills/design/templates/architecture.md`: overview, system
   context diagram, component table, one `##` area per major component
   (purpose, how it works, interfaces, data, failure modes), data model,
   2-3 key flows with mermaid sequence diagrams, cross-cutting concerns,
   constraints and debt, glossary. Every claim cited file:symbol; mark
   everything `[built]`. Explain in plain language, not just file lists.
   Document what IS. Never propose changes during onboard.
4. Recover implicit decisions: for each "why is it this way?" the code
   answers silently (framework, structure, patterns), write a retroactive
   ADR from `.claude/skills/design/templates/adr.md` (Status ACCEPTED,
   Retroactive: yes; Summary, Context, Decision, Consequences required).
   Only decisions a future session would re-litigate; not one per file.
5. Record the baseline table in docs/architecture.md: build/test/lint
   commands, actual results, date. Fill AGENTS.md Commands from it.
6. Seed PLAN.md: Now ("onboard complete, next is T1"), Milestones from
   the system's state, first Tasks with Done when + Read first (name the architecture.md
   sections and ADRs each task depends on). Append a
   Log line: onboard done, verified by the baseline output.

## Rules

- One pass. Do not rescan later; keep architecture.md current via ADRs.
- No proposals during onboard. Ideas become Tasks, changes become ADRs,
  after onboard.

## Verification

architecture.md cites file:symbol per component; the baseline table shows
real command output; at least one retroactive ADR exists (or the codebase
is genuinely trivial); PLAN.md has a next task with Done when + Read first.
