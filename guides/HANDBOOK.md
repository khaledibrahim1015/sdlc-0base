# Handbook

## 1. Mental model

- **AGENTS.md** is always in context (via CLAUDE.md). Keep it short.
- **PLAN.md** is read at session start. It says where work stands and which
  files to open next.
- **Skills** load their body only when invoked. **Subagents** run in their
  own context and return only a conclusion.
- The conversation is disposable. Anything worth keeping is written to a
  file before you `/clear`.

| Loaded | What |
|---|---|
| Always | CLAUDE.md -> AGENTS.md; skill and agent names + descriptions |
| On demand | PLAN.md (ritual step 1); the task's "Read first" files; a skill body when invoked |
| Isolated; only the conclusion returns | Subagent work (analyst, investigator, reviewer) |

## 2. Where to install

| Goal | Where | First command |
|---|---|---|
| Build something new | The project | Fill PLAN.md, then "resume" |
| Take over an existing codebase | That codebase | `/onboard` |
| Evaluate or compare repos | A separate hub (`--hub`) | `/repo-evaluation` |
| Evaluate, then build on the winner | Hub first, then the fork | `/repo-evaluation`, then `/onboard` in the fork |

Never install into repos you are only evaluating.

## 3. Install (once per project)

1. `./setup.sh /path/to/project` (or `--hub`).
2. Fill the AGENTS.md TODOs: overview paragraph and the five Commands.
3. Add your real test/lint commands to `.claude/settings.json` allow list,
   e.g. `"Bash(npm test:*)"`, so verification does not prompt every time.
4. Start `claude`; run `/agents` and `/memory` once to confirm they loaded.
5. Commit `AGENTS.md CLAUDE.md PLAN.md .claude/ docs/ .gitignore`.

## 4. Sequences

### A. Existing codebase, first session
1. `claude`, then `/onboard`.
2. Main session dispatches ONE `repo-analyst`. In its own context it maps
   the tree, builds, runs tests, reads the 2-3 core flows, and writes
   `docs/eval/self-onboard.md`.
3. Main session reads only that report and spot-checks 2-3 citations.
4. It writes `docs/architecture.md` (components with file:symbol, baseline
   table) and a few retroactive ADRs.
5. It fills AGENTS.md Commands, seeds PLAN.md (Now, Milestones, first tasks
   with Done when + Read first), appends a Log line.
6. You review the diff, commit, `/clear`.

### B. Greenfield, first session
1. Write PLAN.md milestones and T1 with a concrete Done when.
2. Say "resume"; continue with C.

### C. A routine task (every normal session)
1. `claude`, say "resume".
2. The SessionStart hook has already injected PLAN.md Now, the current task,
   its ADRs and architecture sections, and the ADR index. Claude marks the task
   in progress, opens only the code paths in Read first, records the track.
3. Implements, runs the focused command, shows command + output.
4. If the review rule applies: "review T3 with code-reviewer". The reviewer
   gets the diff + Done when, re-runs the checks, returns a verdict.
   CHANGES_REQUIRED: fix, re-verify, re-review.
5. Rewrites Now, moves the row to done, appends a Log line (the Stop hook
   insists on a PLAN.md update if code changed).
6. Commit with Conventional Commits and explicit paths (the commit gate runs
   lint first). `/clear`.

### D. A major task (design flow)
1. Run `/design <goal>` (it also triggers on its own for major work). Give
   goal, constraints, non-goals, scale, deadline. Claude asks any blocking
   questions once, in one batch.
2. If an area is unfamiliar, a `repo-analyst` reads it in isolation first.
3. Claude writes the ADR (`Status: PROPOSED`) from the template: summary,
   context, drivers, 2+ options with costs, decision, rationale,
   consequences, risks, rollout, verification. It then **stops**.
4. **You review and approve.** Optional but recommended: "review ADR-n with
   code-reviewer" (fresh-context design review). Then Claude (or you) sets
   `Status: ACCEPTED`. Until then lint blocks any task that cites it.
5. Claude updates `docs/architecture.md`: new `[planned]` areas, mermaid
   diagrams, links to the ADR.
6. Claude writes `docs/plans/<name>.md`: phases (objective, deliverables,
   entry/exit criteria, risks, rollback) and per-task Files, Steps, Tests,
   Depends on. It adds the matching PLAN.md rows (Done when, Read first =
   plan task + architecture area + ADR) and turns phases into Milestones.
7. Lint must pass before commit. You approve the plan; implementation then
   follows sequence C, one task per session, review mandatory.
8. Reviewer says ARCHITECTURE_CHANGE_REQUIRED: the diff contradicts an
   ADR. Supersede it with a new ADR (via `/design`) or change the diff.
9. When a task makes a `[planned]` part real, flip it to `[built]` in
   architecture.md in the same task.

### E. A bug
1. `/systematic-debugging` + the symptom.
2. Find a deterministic repro command. None: stop and report that.
3. Heavy reading: dispatch `investigator` (repro output, isolation trail,
   cited root cause).
4. Smallest fix to the mechanism.
5. Regression test: fails on old code, passes on the fix; show both outputs.
6. Verify, Log, then C steps 4-6.

### F. Context filling up, or stopping mid-task
1. "Update Now with exactly where we stopped and the next action."
2. `/clear`, then "resume".
3. Don't rely on `/compact` as memory; PLAN.md is the record.

### G. Evaluate one or more repos (hub)
1. `./setup.sh --hub ~/eval-hub`; clone repos into `repos/` (`git clone
   --depth 1`) or start `claude --add-dir ~/code/repoA`.
2. `/repo-evaluation`. Per repo give: path, the question, the report name.
   Use shared criteria when comparing.
3. One `repo-analyst` per repo runs in a parallel batch, each writing
   `docs/eval/<name>.md`. Large repo: several analysts, one bounded area each.
4. Main session reads only reports, checks one report per repo exists,
   writes the cited Decision section, milestones and first tasks.
5. You pick. Then an ADR for the choice, and C/D as usual. To build on the
   winner: fork it, run `setup.sh` inside the fork, `/onboard`.

### Weekly upkeep (5 min)
- Move Log rows older than the last ~15 to `docs/log-archive.md`.
- Check architecture.md against any structural change.
- Keep AGENTS.md under ~100 lines. Add a line only for a mistake made twice.

## 5. What "detailed" means (design documents)

Detail lives in on-demand docs, never in AGENTS.md. Three documents, each
with a template in `.claude/skills/design/templates/`:

| Document | Answers | Required by lint |
|---|---|---|
| ADR `docs/decisions/ADR-n-*.md` | Why did we choose this, and what did we reject? | Summary, Context, Options considered, Decision, Consequences, Risks and mitigations, Verification (retroactive: first 4 of those minus options) |
| Architecture `docs/architecture.md` | How does it work, in plain language, with diagrams? | Anchors in Read first must resolve |
| Plan `docs/plans/<name>.md` | In what order do we build it, and exactly what is each task? | Summary, Goal, Scope, 1+ phase each with Exit criteria, each task with Files and Steps, every task ID present in PLAN.md |

Division of labor, so no fact has two homes: PLAN.md holds status and the
one-line **Done when** per task; the plan doc holds Files, Steps, Tests,
dependencies and risks; the ADR holds the reasoning; architecture holds
how the system works.

Quality bar (also in the skill): every decision explains why and what it
rejected and costs; plain-language Summary first; facts cited or labeled
ASSUMPTION/INFERENCE; exit criteria are commands plus observable results;
tasks fit one session (<=5 files, one focused test command); risks carry a
mitigation and an early signal.

To get more depth, say so in the prompt, for example:
`/design add rate limiting to the public API. Scale: 50k req/min peak.
Must not add >2 ms p95. Two-week deadline. Explain every option you reject.`

A fully filled example (it passes lint) is in `guides/examples/`:
`ADR-004-rate-limit-public-api-at-gateway.md` and `rate-limiting-plan.md`.

Cost: the SessionStart hook injects only the ADR Summary, Decision and
Consequences (full file path given), plus the single plan task and
architecture area the task points to. A 4.5 KB ADR plus a 4 KB plan
injected about 2.9 KB in testing. Detail is on disk, not in every session.

## 6. Enforcement (hooks)

Written rules are requests; hooks are guarantees. `.claude/hooks/plan_guard.py`
is wired in `.claude/settings.json` and runs whether or not the model
remembers the rules. Python 3 is required (on Windows change `python3` to
`python` in settings.json and the allow rule).

| Rule | Mechanism | What happens |
|---|---|---|
| Session sees the governing ADRs and architecture sections | `SessionStart` hook (startup, resume, clear, compact) | PLAN.md Now, the current task, the full text of ACCEPTED ADRs and the architecture sections in its Read first, and the ADR index are injected as context. Superseded ADRs are flagged, not injected. |
| PLAN.md / ADRs stay well-formed | `PreToolUse(Bash)` hook on `git commit` | Commit blocked, reasons shown to Claude, until lint passes |
| PLAN.md is updated when code changes | `Stop` hook | Claude cannot end a session that changed code without touching PLAN.md |
| Detailed, approved design before code | Lint on `git commit` | Thin ADRs/plans and tasks citing unapproved ADRs cannot be committed |
| Hooks are not casually removed | `deny` rules on Edit of `.claude/hooks/**` and `settings.json` | You edit them by hand |

Lint rules (`python3 .claude/hooks/plan_guard.py lint`, also fine for CI):
ADR and plan-doc required sections (section 5); a task cannot cite a
`PROPOSED` ADR (the approval gate); at most one task in progress; non-done tasks have a valid track, Done when
and Read first; a major task names its governing ADR; every `ADR-n` and
`file.md#section` in Read first resolves; referenced ADRs are ACCEPTED; every
ADR has a Status line; Log has at most 30 rows.

Limits, stated plainly:
- It guarantees the docs are **loaded**, not that Claude **applies** them.
  The reviewer subagent is still the check on that, and review itself is not
  forced by a hook.
- The Stop gate is a heuristic: it compares a snapshot taken at session
  start with the tree at stop. It cannot judge the quality of the Log line.
- Task cells must not contain `|`. Placeholder rows (`<TODO>` in the Task
  column) are ignored, so a fresh template commits cleanly.
- Hooks are not a sandbox. `sed -i` through Bash can still edit a protected file.
- Upgrading an older install: setup.sh will not change an existing
  settings.json; it prints a NOTE telling you to merge the `hooks` block.

## 7. Safety

- Deny rules are a speed bump, not a sandbox: `Read(.env*)` does not stop
  `cat .env` through Bash.
- Analysts execute third-party code. For untrusted repos use a container/VM,
  or tell the analyst "static analysis only" and expect INFERENCE labels.
- Repo text can contain prompt injection. The analyst treats it as data;
  you should skim reports for odd instructions.
- Hub mode: add `Bash(git clone:*)` to the allow list if you want Claude to
  clone for you.

## 8. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Agent not listed in `/agents` | Frontmatter typo (misspelled fields fail silently); check file is in `.claude/agents/` |
| Rules in AGENTS.md ignored | `/memory`: is CLAUDE.md loaded and does it contain `@AGENTS.md`? |
| Permission prompt on every test run | Add the command to `.claude/settings.json` allow list |
| Skill never triggers | `onboard` and `repo-evaluation` are manual by design: type `/onboard` |
| Sessions re-read the whole repo | Tasks missing a Read first column entry |
| No `[plan_guard]` block at session start | Run `/hooks` to see if SessionStart is registered; check `python3 --version` (Windows: use `python`); settings.json must be valid JSON |
| Commit blocked | Read the listed reasons, fix PLAN.md/ADRs, or run `python3 .claude/hooks/plan_guard.py lint` yourself |
| Stop keeps being blocked | Update PLAN.md (Now + Log line). It fires only when code changed and PLAN.md did not |
| Claude wrote a thin ADR | Lint names the missing sections; ask it to use `/design` and the template |
| Reviewer approves everything | Task has no real Done when; rewrite it as command + observable result |
