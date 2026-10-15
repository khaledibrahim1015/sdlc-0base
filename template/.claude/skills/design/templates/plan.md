<!-- docs/plans/<name>.md: the DETAIL behind PLAN.md rows.
     PLAN.md stays the lean state (status, Done when, Read first).
     Task IDs here must exist in PLAN.md. Heading for a task is exactly
     its ID (### T3) so `docs/plans/<name>.md#t3` resolves. -->

# Plan: <name>

- Status: draft | approved | in progress | done
- Date: <date>
- Governing ADRs: <ADR-n, ...>

## Summary
<Plain language: what we are building, why, in how many phases, what
"finished" looks like. No unexplained jargon.>

## Goal and success criteria
<Observable outcomes, each with the command/metric that shows it.>

## Scope
- In: <...>
- Out (and why): <...>

## Assumptions and open questions
<ASSUMPTIONs the plan depends on; questions the human must answer, with
who/when. Block the affected phase until resolved.>

## Phase 1: <name>
- Objective: <one sentence>
- Deliverables: <what exists afterwards>
- Entry criteria: <what must be true to start>
- Exit criteria: <observable, with the command that proves each>
- Risks: <phase-specific, with mitigation>
- Rollback: <how to undo this phase safely>

### T1
- Title: <imperative, specific>
- Track: routine | major
- Why: <how it serves the phase objective>
- Files: <paths/areas touched, `file:symbol` where known>
- Steps:
  1. <concrete step>
  2. <concrete step>
- Tests: <what to add or change; the focused command>
- Depends on: <task IDs or none>
- Risks / notes: <...>

### T2
- Title:
- Track:
- Why:
- Files:
- Steps:
  1.
- Tests:
- Depends on:

## Phase 2: <name>
- Objective:
- Deliverables:
- Entry criteria:
- Exit criteria:
- Risks:
- Rollback:

## Dependencies and ordering
<A short mermaid flowchart or list of task dependencies across phases.
Order phases so each is shippable and verifiable on its own.>

## Verification plan
<Full-suite, integration, load, manual checks before the plan is "done".>
