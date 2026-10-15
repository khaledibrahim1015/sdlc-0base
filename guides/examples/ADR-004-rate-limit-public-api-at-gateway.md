# ADR-4: Public API rate limiting is enforced at the gateway with a shared token bucket

- Status: ACCEPTED
- Date: 2026-10-01
- Track: major
- Retroactive: no
- Related: ADR-1 (stateless JWTs), docs/plans/rate-limiting.md

## Summary
Customers can currently send unlimited requests, and one noisy client
slowed everyone down on 2026-09-18. We will limit each API key to a fixed
request budget, enforced at the gateway (the single entry point) using a
counter stored in Redis, so every server instance sees the same count. The
main cost is a new Redis dependency on the request path, which we cover
with a fail-open fallback.

## Context
- All public traffic enters through `gateway/src/server.ts:handleRequest`;
  there is no throttling today (`gateway/src/middleware/index.ts:chain`
  has auth and logging only).
- Incident 2026-09-18: one key sent ~40k req/min; p95 latency tripled for
  all tenants (ASSUMPTION: taken from the incident ticket, not re-measured).
- Gateway runs as 4+ stateless instances (`deploy/gateway.yaml:replicas`),
  so per-instance counters would undercount by the replica count.
- Out of scope: per-endpoint quotas, billing tiers, abuse/DDoS defense.

## Decision drivers
1. Correct limits across all instances. 2. Added latency under 2 ms p95.
3. Gateway must stay up if the limiter breaks. 4. Small change, shippable
in two weeks. 5. Easy to tune per key without a deploy.

## Options considered
### Option A: In-memory counter per gateway instance
- How it works: each instance counts requests per key locally.
- Pros: no new dependency, near-zero latency.
- Cons / cost: effective limit = limit x replicas, and changes whenever we
  scale; unfair under uneven load balancing.
- Fit against the drivers: fails 1; passes 2, 3, 4; 5 needs a deploy.

### Option B: Shared token bucket in Redis, enforced at the gateway
- How it works: a Lua script atomically refills and decrements a bucket
  keyed by API key; the gateway rejects with 429 when empty.
- Pros: one correct limit for all instances; limits live in config.
- Cons / cost: Redis is on the request path (+0.5-1 ms expected), new
  operational dependency.
- Fit against the drivers: passes 1, 4, 5; 2 to be verified; 3 needs a fallback.

### Option C: Third-party API management product
- How it works: move rate limiting to a hosted gateway product.
- Pros: rich features, no code.
- Cons / cost: new vendor, migration of auth and routing, months not weeks.
- Fit against the drivers: fails 4.

## Decision
We will enforce per-API-key rate limits in the gateway using a Redis-backed
token bucket (Option B). A middleware `rateLimit` is added after `auth` in
`middleware/index.ts:chain`. Limits come from `config/limits.yaml`, keyed by
key tier. Over-limit requests get HTTP 429 with `Retry-After`. If Redis is
unreachable or slower than 20 ms, the middleware fails open and increments
a `ratelimit_bypass_total` metric.

## Rationale
Only option B gives a single correct limit across instances within the
timeline. We knowingly accept a new request-path dependency; the fail-open
rule trades temporary loss of protection for availability, which matches
driver 3.

## Consequences
### Gains
Noisy clients are contained; limits are tunable without deploys.
### Costs
Redis becomes critical infrastructure; +~1 ms per request; a limiter
outage silently removes protection (mitigated by the bypass metric/alert).

## Risks and mitigations
| Risk | Likelihood / impact | Mitigation | Early signal |
|---|---|---|---|
| Redis latency spikes slow all requests | Medium / High | 20 ms timeout then fail open | p95 of `ratelimit_check_ms` |
| Wrong limits block real customers | Medium / High | Shadow mode (log only) for one week before enforcing | `ratelimit_would_block_total` |
| Fail-open hides a long outage | Low / Medium | Alert when bypass rate > 1% for 5 min | `ratelimit_bypass_total` |

## Rollout / migration
Ship in shadow mode (counts and logs, never rejects), review would-block
data, then enable enforcement per tier, largest limits first. Rollback:
set `enforce: false` in config; no data migration.

## Verification
- Unit: bucket math in `gateway/test/ratelimit.test.ts` passes
  (`npm test -- ratelimit`).
- Load: 4 instances, one key at 2x limit, observed accepted rate within 5%
  of the limit (`scripts/loadtest.sh`).
- Latency: added p95 < 2 ms in the same load run.

## Architecture impact
Add `## Rate limiting` to docs/architecture.md (`[planned]`); update
`## Gateway` request-chain flow.

## Tasks
T10 to T13, see docs/plans/rate-limiting.md.
