# ADR-<n>: <title that says what it governs, e.g. "Sessions are stateless JWTs">

- Status: PROPOSED
- Date: <YYYY-MM-DD>
- Track: major
- Retroactive: no
- Related: <ADR-m (supersedes / depends on), docs/plans/<name>.md>

<!-- Detailed means complete, not long: every section answers a question a
     future session would otherwise guess at. Delete this comment. -->

## Summary
<3-5 plain-language sentences. The problem, the choice, the main cost. A
new engineer must understand the decision from this section alone, with
no unexplained jargon.>

## Context
<What exists today (cite `file:symbol` or ADR-n). What forces this
decision now: requirement, incident, deadline, constraint. What is NOT in
scope. Facts carry citations; guesses are labeled ASSUMPTION.>

## Decision drivers
<The criteria that matter, ranked: e.g. latency budget, team skills, cost,
reversibility, security posture, time to ship.>

## Options considered
<At least two real options, plus "do nothing" when relevant. Same
structure for each so they can be compared fairly.>

### Option A: <name>
- How it works: <2-4 sentences>
- Pros: <...>
- Cons / cost: <effort, risk, lock-in, ongoing cost>
- Fit against the drivers: <one line per driver>

### Option B: <name>
- How it works:
- Pros:
- Cons / cost:
- Fit against the drivers:

## Decision
<One sentence: "We will ...". Then the shape: components touched,
interfaces, data, boundaries. Enough that someone could implement it.>

## Rationale
<Why this option beats the others against the drivers. Explain the
trade-off you are knowingly accepting.>

## Consequences
### Gains
<What gets better, measurably.>
### Costs
<What gets worse or harder: complexity, migration, operational burden.>

## Risks and mitigations
| Risk | Likelihood / impact | Mitigation | Early signal |
|---|---|---|---|
| | | | |

## Rollout / migration
<Order of changes, feature flags, data migration, how to roll back, what
must stay backward compatible and for how long.>

## Verification
<How we will know it works: commands, metrics, tests, a load figure. Each
item observable.>

## Architecture impact
<Sections of docs/architecture.md to add or change (anchors), marked
[planned] until built.>

## Tasks
<PLAN.md IDs created from this decision, grouped by phase in
docs/plans/<name>.md.>
