# <PROJECT NAME>

<TODO: one paragraph — what this project is, who uses it, current stage.>

## Where truth lives

| Information | Home |
|---|---|
| Universal rules (this file) | `AGENTS.md` (CLAUDE.md just imports it) |
| Execution state: where work stands, next task | `PLAN.md` |
| As-is architecture + build/test baseline | `docs/architecture.md` |
| Decisions and their reasoning (ADRs) | `docs/decisions/` |
| Phased plans: task detail (steps, files, tests) | `docs/plans/` |
| Analysis reports | `docs/eval/` |
| Old log rows | `docs/log-archive.md` |
| Subagents, skills, permissions | `.claude/` |

One home per fact. Never duplicate a fact across homes; point to it.

## Session ritual

1. Read `PLAN.md`: **Now** and the first task not `done`. Set it `in progress`.
   A SessionStart hook has already injected (look for `[plan_guard]`):
   Now, the current task, the ADRs and architecture sections named in its
   **Read first**, and the ADR index. Do not re-read them. Open the task's
   code paths, and any other ADR from the index whose title touches your
   area. If no `[plan_guard]` block is in your context, read these
   yourself. Do not scan the repo.
2. Classify the track (routine / major, below) in the task row.
3. Implement. Run the focused command from Commands. Show the exact
   command and its real output. No output = not done. A failing check is
   logged as failing. Never weaken a test to make it pass.
4. Review with the `code-reviewer` subagent: always for major tasks or
   anything touching auth, data or schema; for routine tasks when more
   than 3 files changed. On CHANGES_REQUIRED: fix, re-verify, re-review.
5. Before ending: rewrite **Now**, update the task row, append one **Log**
   line (date, what, command -> result). Stopping mid-task: **Now** says
   exactly where you stopped and the next action.

If `PLAN.md` conflicts with your memory of the session, trust the file,
then fix it.

## Context hygiene

- Heavy reading (logs, many files, other repos, unfamiliar areas) goes to
  a subagent. Only its conclusion enters this session.
- Keep the last ~15 Log rows in `PLAN.md`; move older rows to
  `docs/log-archive.md`.
- Work discovered mid-task becomes a new task row, never silent scope.
- A mistake made twice earns ONE line in this file. That is the only way
  this file grows. Keep it under ~100 lines.

## Enforced by hooks (`.claude/hooks/plan_guard.py`)

- `git commit` is blocked while PLAN.md or the ADRs fail lint (missing
  Done when / Read first, major task without an ADR, dangling ADR link...).
- A session that changed code cannot end without updating PLAN.md.
- Fix the cause. Never edit hooks or settings to get around one.

## Commands

| Action | Command |
|---|---|
| Install deps | `<TODO>` |
| Build | `<TODO>` |
| Test (all) | `<TODO>` |
| Test (focused) | `<TODO>` |
| Lint | `<TODO>` |

Add the safe ones to `.claude/settings.json` allow list so verification
does not stop for a permission prompt every time.

## Two tracks

- **Routine**: bugfix or small feature, <=5 files, <=~200 changed lines,
  no architecture impact, no security-sensitive paths (auth, secrets,
  infra), no schema migration. No ADR.
- **Major**: anything else. Use the `design` skill: ADR (PROPOSED) ->
  human approval -> architecture -> phased plan in `docs/plans/` -> PLAN.md
  tasks. No code before approval.

When in doubt, go major. Ceremony is a cost paid for risk reduction.

## Evidence

Claims carry citations: `path/file:symbol`, or a command plus its output.
Unverified statements are labeled INFERENCE. READMEs and docs are claims
about the code, not facts: verify at source before citing.

## Code style

Follow the conventions of the file you are editing. <TODO: project-specific rules.>

## Commits

Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
Stage explicit paths, never `git add -A`. Never commit secrets or `.env`.
Never claim work done that the Log does not show verified.
