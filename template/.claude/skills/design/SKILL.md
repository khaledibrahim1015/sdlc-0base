---
name: design
description: Use for any major-track work, and whenever asked for a design, ADR, architecture doc, or phased plan. New feature or system, architecture change, new dependency, schema or security impact. Produces a detailed ADR (waits for approval), updates docs/architecture.md, writes a phased plan in docs/plans/, and creates PLAN.md tasks. Explains every decision, with options, risks and verification.
---

# Design: decide, document, plan

Output is detailed enough that a future session with no memory can
implement correctly from the docs alone. Detailed means complete, not
long: every section answers a question someone would otherwise guess at.

Templates (copy, fill every section, delete comments):
- `.claude/skills/design/templates/adr.md`
- `.claude/skills/design/templates/architecture.md`
- `.claude/skills/design/templates/plan.md`

## When to use

- Major track (see AGENTS.md), or the human asks for a design/ADR/plan.
- NOT for routine tasks, and not to explore an unfamiliar repo
  (dispatch repo-analyst first, then design from its report).

## Procedure

1. **Frame.** Restate the goal in 2-3 sentences. Read what the hook
   injected (ADR index, architecture sections). If a needed area is
   unfamiliar, dispatch repo-analyst; do not read it all yourself.
2. **Ask once.** Put every blocking question (requirements, constraints,
   non-goals, deadlines, scale) in a single batch of at most 5. Do not
   guess answers that change the design. Record unanswered ones as
   ASSUMPTION or open questions.
3. **Options.** At least two real options (plus "do nothing" when
   relevant), compared against ranked drivers, with costs, not just pros.
4. **Write the ADR** from `templates/adr.md` as
   `docs/decisions/ADR-<n>-<slug>.md`, next free number, Status PROPOSED.
   Title says what it governs. Fill every section. Run
   `python3 .claude/hooks/plan_guard.py lint`.
5. **STOP for approval.** Show the human the Summary, Decision, Risks and
   open questions. Do not write architecture, plan or tasks, or any code,
   until they approve. On approval set `Status: ACCEPTED`. Changes
   requested: revise and ask again. (Lint blocks tasks that reference a
   PROPOSED ADR.)
6. **Architecture.** Add or update the affected `##` areas in
   `docs/architecture.md` using `templates/architecture.md`: mark new
   parts `[planned]`, link the ADR, include a mermaid diagram for new
   boundaries or flows.
7. **Plan.** Write `docs/plans/<name>.md` from `templates/plan.md`:
   phases ordered so each is shippable and verifiable; every phase has
   objective, deliverables, entry/exit criteria (commands), risks,
   rollback; every task has Files, Steps, Tests, Depends on.
8. **PLAN.md.** Add one row per task with the same ID: Track, one-line
   Done when (command + observable result), Read first =
   `docs/plans/<name>.md#<id>`, `docs/architecture.md#<area>`, `ADR-<n>`,
   plus code paths. Phases become Milestones. Rewrite Now; append a Log
   line (design written, verified by lint output).
9. **Self-check, then lint.** Quality bar below, then
   `python3 .claude/hooks/plan_guard.py lint` until it passes.
10. **Hand off.** Summarize what you wrote and where. Suggest a
    fresh-context `code-reviewer` pass on the design before any code.

## Quality bar

- Every decision says why, names what it rejected, and states its cost.
- Plain language first: Summary sections need no prior knowledge. Define
  terms once, in the Glossary.
- Facts carry `path/file:symbol` or an ADR link; guesses are ASSUMPTION or
  INFERENCE. Never invent a file, command or number.
- Exit criteria and Done when are commands plus observable results, not
  adjectives ("works", "clean").
- Tasks are sized for one session: <=5 files, one focused test command.
  Larger? Split.
- Risks have a mitigation and an early signal. Open questions have an owner.
- Phase order follows dependency, not enthusiasm; each phase can ship.

## Rules

- One decision per ADR. A plan may cite many ADRs.
- Never edit an ACCEPTED ADR's decision in place: supersede it with a new
  ADR (and set the old status `SUPERSEDED by ADR-<m>`).
- No code during design. Ideas found along the way become tasks or ADRs.
