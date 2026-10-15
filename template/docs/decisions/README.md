# Decisions (ADRs)

Write an ADR for: architecture changes, new dependencies, anything a
future session would otherwise re-litigate ("why is it this way?").
Major-track tasks need an approved ADR before code.

## Index

Generated from the ADR files, never kept by hand:
`python3 .claude/hooks/plan_guard.py adr-index`
(also injected at session start). So: every ADR needs a `# ADR-<n>: <title>`
line and a `- Status:` line, and the title must say what it governs
("Sessions are stateless JWTs", not "Auth decision").

## Format

Do not hand-write these. Use the `design` skill, which fills
`.claude/skills/design/templates/adr.md` completely.

Lifecycle: `PROPOSED` (drafted, awaiting human approval) -> `ACCEPTED` ->
`SUPERSEDED by ADR-<m>` or `REVERSED`. Only ACCEPTED ADRs may govern tasks.
Never edit an ACCEPTED decision in place: supersede it.

Required sections (lint enforces): Summary, Context, Options considered,
Decision, Consequences, Risks and mitigations, Verification.
Retroactive ADRs (recovered by /onboard, `Retroactive: yes`) need only:
Summary, Context, Decision, Consequences.
