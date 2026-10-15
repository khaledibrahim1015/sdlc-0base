# claude-project-template (v2)

A small, durable setup that gives every Claude Code session the right
context, and keeps long projects from rotting.

## The four ideas

1. **External memory.** `PLAN.md` holds execution state. The conversation is disposable.
2. **Isolated context.** Read-heavy work runs in subagents; only the conclusion returns.
3. **Verification.** No "done" without a real command and its real output.
4. **Recorded decisions.** ADRs stop future sessions from re-litigating old choices.

## Quick start

    ./setup.sh /path/to/project          # a project you build or maintain
    ./setup.sh --hub /path/to/eval-hub   # a workspace for evaluating other repos

Then follow the "Next steps" it prints. Full walkthrough: `guides/HANDBOOK.md`.

## What gets installed

    CLAUDE.md                  one line: @AGENTS.md  (generated, no symlink)
    AGENTS.md                  universal rules + session ritual (always loaded)
    PLAN.md                    state: Now / Milestones / Tasks / Log
    docs/architecture.md       as-is architecture + build/test baseline
    docs/decisions/            ADRs (detailed, template-driven)
    docs/plans/                phased plans: task detail behind PLAN.md rows
    docs/eval/                 analyst reports
    docs/log-archive.md        old Log rows
    .claude/settings.json      permissions
    .claude/hooks/plan_guard.py  enforcement: context injection, commit + stop gates, lint
    .claude/agents/            code-reviewer, repo-analyst, investigator
    .claude/skills/            design (+ADR/architecture/plan templates), onboard, systematic-debugging
    (--hub) .claude/skills/repo-evaluation

`setup.sh` never overwrites, is idempotent, and never runs git.

## Enforcement

Hooks (not instructions) load the current task's ADRs and architecture
sections at every session start, block commits while PLAN.md/ADRs are
malformed, and stop a session from ending with code changed but PLAN.md
untouched. One Python file, no dependencies. See HANDBOOK section 5.

## Design documents

`/design` produces a detailed ADR (waits for your approval), architecture
sections with diagrams, a phased plan with per-task steps, and PLAN.md
rows. Lint rejects thin versions. Worked example: `guides/examples/`.

## Not over-engineered: what was deliberately left out

Skills for the session ritual and "verify before done" (they live in
AGENTS.md instead), a test-writer agent, agent memory, a symlink,
CLAUDE.local.md scaffolding.

## Not verified here

The files were built and the installer and `plan_guard.py` tested in a
sandbox with simulated hook input, but nothing was run inside Claude Code
itself. After install, run `/agents` and
`/memory` once to confirm the agents and CLAUDE.md load.
# sdlc-0base
