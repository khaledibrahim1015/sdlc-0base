# Plan: Public API rate limiting

- Status: approved
- Date: 2026-10-01
- Governing ADRs: ADR-4

## Summary
We add per-key rate limiting to the gateway in two shippable phases:
first a safe shadow mode that only measures, then enforcement turned on
tier by tier. Finished means noisy keys are throttled with 429s, limits
are changed in config, and Redis trouble never takes the API down.

## Goal and success criteria
- A key sending 2x its limit is held within 5% of the limit across 4
  instances (`scripts/loadtest.sh --key=test --rps=2x`).
- Added p95 latency under 2 ms in the same run.
- Killing Redis during load causes zero 5xx and increments
  `ratelimit_bypass_total`.

## Scope
- In: limiter middleware, config, metrics, shadow mode, rollout.
- Out (and why): per-endpoint quotas and billing tiers, separate project;
  DDoS defense, handled at the CDN.

## Assumptions and open questions
- ASSUMPTION: Redis (existing cache cluster) can take ~5k extra ops/s.
- Question for the human: initial limits per tier? Blocks T12.

## Phase 1: Build and measure (shadow mode)
- Objective: limiter exists and reports would-block data without rejecting.
- Deliverables: middleware, Lua script, config, metrics, tests.
- Entry criteria: ADR-4 ACCEPTED.
- Exit criteria: `npm test -- ratelimit` passes; load test shows accepted
  rate within 5% in shadow accounting; dashboards show would-block counts.
- Risks: Lua script bug miscounts. Mitigation: property test on bucket math.
- Rollback: remove middleware from `chain`; no data to undo.

### T10
- Title: Implement token bucket Lua script and client wrapper
- Track: major
- Why: core correctness of the whole feature (ADR-4 Decision).
- Files: gateway/src/ratelimit/bucket.lua, gateway/src/ratelimit/client.ts, gateway/test/ratelimit.test.ts
- Steps:
  1. Write the atomic refill-and-take Lua script.
  2. Wrap it with a 20 ms timeout returning allow/deny/bypass.
  3. Add tests for refill, burst, concurrent callers, timeout.
- Tests: `npm test -- ratelimit`.
- Depends on: none
- Risks / notes: clock source must be Redis `TIME`, not instance clocks.

### T11
- Title: Add rateLimit middleware in shadow mode with metrics
- Track: major
- Why: wires the limiter into the request chain safely.
- Files: gateway/src/middleware/index.ts, gateway/src/middleware/rateLimit.ts, config/limits.yaml
- Steps:
  1. Insert `rateLimit` after `auth` in `chain`.
  2. Read limits by key tier from config; honor `enforce: false`.
  3. Emit `ratelimit_check_ms`, `ratelimit_would_block_total`, `ratelimit_bypass_total`.
- Tests: `npm test -- middleware`.
- Depends on: T10

## Phase 2: Enforce and roll out
- Objective: enforcement on for all tiers with an alert on bypass.
- Deliverables: 429 + Retry-After behavior, alerts, runbook.
- Entry criteria: one week of shadow data reviewed by the human; limits answered.
- Exit criteria: `scripts/loadtest.sh` meets success criteria; Redis-kill test passes.
- Risks: wrong limits block customers. Mitigation: enable per tier, largest first.
- Rollback: set `enforce: false`.

### T12
- Title: Enable enforcement with 429 and Retry-After
- Track: major
- Why: delivers the actual protection.
- Files: gateway/src/middleware/rateLimit.ts, config/limits.yaml
- Steps:
  1. Return 429 with `Retry-After` when the bucket is empty and `enforce: true`.
  2. Enable tier by tier per the rollout section of ADR-4.
- Tests: `npm test -- ratelimit` plus `scripts/loadtest.sh`.
- Depends on: T11

### T13
- Title: Alerts and runbook for bypass and latency
- Track: routine
- Why: fail-open must not hide an outage.
- Files: deploy/alerts.yaml, docs/runbooks/ratelimit.md
- Steps:
  1. Alert when bypass rate > 1% for 5 min.
  2. Write the runbook: how to disable, how to read the metrics.
- Tests: `scripts/check-alerts.sh`.
- Depends on: T11

## Dependencies and ordering
T10 -> T11 -> (T12, T13). Phase 1 is shippable alone (measurement only).

## Verification plan
Full suite, the load test with Redis killed mid-run, one week of shadow data.
