---
name: systematic-debugging
description: Use for any bug, failing test you do not understand, or regression. Reproduce, isolate, find the root cause, fix the mechanism, add a regression test. No symptom patches. Dispatches the investigator subagent when reading would flood the session.
---

# Systematic debugging

## When to use

- A bug, a failing test you do not understand, a regression.
- NOT for a known-mechanism fix: just fix it with the focused test.

## Procedure

1. Reproduce: a deterministic command that triggers it. No repro: stop
   and report that. Guessing at a fix without one is the anti-pattern
   this skill exists to prevent.
2. Isolate: module, input, commit (git bisect for regressions). Heavy
   reading or log-walking: dispatch the investigator subagent with the
   symptom; it returns a cited root cause.
3. Root cause: one mechanistic paragraph. Why this input through this
   code produces this output, cited file:symbol. No paragraph, no fix.
4. Fix the mechanism, not the symptom: the smallest change that makes the
   mechanism correct. Symptom patches (swallowing the error,
   special-casing the input) are rejected.
5. Regression test: write it yourself (it is small). Run it against the
   unfixed code (must fail) and the fix (must pass). Report both outputs.
6. Finish per AGENTS.md session ritual: verify, review if required, Log
   the repro + fix + test outcome.

## Rules

- One root cause per investigation chain. Two causes, two chains.
- If the fix requires weakening a test, the root cause is wrong. Back to 3.
- Mechanism correct but behavior unwanted? That is a design decision, not
  a bug: propose an ADR instead of patching.

## Verification

The repro command failed before and passes after (real outputs in the
Log); the root-cause paragraph carries a citation.
