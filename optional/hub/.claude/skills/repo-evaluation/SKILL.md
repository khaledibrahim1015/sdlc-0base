---
name: repo-evaluation
description: Evaluates one or more repos in parallel, one repo-analyst subagent per repo, hands-on verified reports in docs/eval/, then a cited synthesis into PLAN.md. Use in an evaluation hub to answer "which repo should we build on?".
disable-model-invocation: true
---

# Repo evaluation

Answers "which repo should we build on?" with evidence, without rotting
the main session's context with raw source.

## When to use

- Comparing 2+ candidate repos, or several areas of one large repo.
- Due diligence on a dependency or fork base.
- NOT for one quick question about one file: just read it.

## Procedure

1. For each repo: name it, give it the question it must answer, and a
   report path (docs/eval/<name>.md). Use ONE shared criteria list when
   comparing like for like (fit, maturity, security, cost to adopt).
2. Dispatch one repo-analyst per repo, all in a single parallel batch.
   Pass: repo path, the question, the report path. Tell each analyst
   whether execution is allowed or static analysis only.
3. Wait for all reports. A missing report means a missing repo; say so,
   never fill it in from impressions.
4. Read ONLY the reports. Spot-check 2-3 citations by asking a subagent.
5. Synthesize into PLAN.md: a Decision section (verdict per option,
   strengths/risks, each claim citing docs/eval/<name>.md), Milestones,
   first Tasks. Update Now.

## Rules

- The main session never reads the evaluated repos' source. On doubt,
  dispatch a subagent question; do not reach into the repo.
- Reports persist in docs/eval/. Re-run only a repo that changed. Date
  every report; supersede explicitly, never silently.

## Verification

docs/eval/ holds one report per dispatched repo, each with hands-on
output; PLAN.md Decision cites each; every dispatched repo is accounted
for in the synthesis.
