# PLAN

Execution memory. **Now** is rewritten every session; **Log** is
append-only (keep the last ~15 rows, archive the rest to
`docs/log-archive.md`). The conversation is disposable; this file is not.

## Now

<One paragraph: where work stands, what is in flight, what is next.>
Updated: <date> by <session/author>

## Decision

<TODO: evaluation projects: the verdict per option, each claim citing
docs/eval/<name>.md. Onboard projects: what was recovered and the
baseline result. Otherwise delete this section.>

## Milestones

| # | Milestone | Status |
|---|---|---|
| 1 | <TODO> | not started |

## Tasks

Status: `todo` -> `in progress` -> `in review` -> `done`.
Exactly one task `in progress` at a time.
**Done when** = an observable criterion plus the command that shows it.
The reviewer judges against this column. **Read first** = the only files
a session should open before starting: code paths, `docs/architecture.md#section`,
and the ADRs that govern the area (e.g. `ADR-3`). Architecture and ADRs
only reach a session through this column and the ADR index.

| ID | Task | Track | Done when | Read first | Status |
|---|---|---|---|---|---|
| T1 | <TODO> | routine | <criterion + command> | <paths> | todo |

## Log (append-only)

| Date | Entry | Verified by |
|---|---|---|
| | | |
