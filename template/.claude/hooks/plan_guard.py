#!/usr/bin/env python3
"""plan_guard: deterministic enforcement of the template's session rules.

Subcommands (wired in .claude/settings.json):
  session-start  SessionStart hook. Injects PLAN.md Now + current task, the
                 ADRs and architecture sections named in its "Read first",
                 and the ADR index. Loading is guaranteed, not requested.
  commit-gate    PreToolUse(Bash) hook. Blocks `git commit` while PLAN.md,
                 ADRs or plan docs fail lint (incl. required sections).
  stop-gate      Stop hook. Blocks ending a session that changed code but
                 never touched PLAN.md.
Manual:
  lint           Validate PLAN.md and ADRs (also usable in CI / pre-commit).
  adr-index      Print one line per ADR (the reviewer subagent runs this).
Exit codes follow Claude Code hooks: 0 ok, 2 block (stderr goes to Claude).
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
MAX_DOC = 12000          # chars injected per document
MAX_LOG_ROWS = 30        # lint error above this: archive old rows
VALID_STATUS = {"todo", "in progress", "in review", "done"}
NON_CODE_FILES = {"PLAN.md", "AGENTS.md", "CLAUDE.md", ".gitignore"}
NON_CODE_DIRS = ("docs/", ".claude/")


def p(*parts):
    return os.path.join(ROOT, *parts)


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def stdin_json():
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def clip(text):
    if len(text) <= MAX_DOC:
        return text
    return text[:MAX_DOC] + "\n[... truncated by plan_guard; open the file for the rest]"


# ---------- markdown helpers ----------
def slug(title):
    return re.sub(r"[^a-z0-9 -]", "", title.lower()).strip().replace(" ", "-")


def get_section(text, pred):
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if m and pred(m.group(2)):
            level, out = len(m.group(1)), [line]
            for nxt in lines[i + 1:]:
                m2 = re.match(r"^(#{1,6})\s", nxt)
                if m2 and len(m2.group(1)) <= level:
                    break
                out.append(nxt)
            return "\n".join(out).strip()
    return None


def table_rows(section_text):
    """Parse the first markdown table: list of dicts keyed by lowercase header."""
    header, rows = None, []
    for line in (section_text or "").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        if len(cells) == len(header):
            rows.append(dict(zip(header, cells)))
    return rows


def headings(text):
    return [m.group(2).strip().lower()
            for m in re.finditer(r"^(#{1,6})\s+(.*?)\s*$", text or "", re.M)]


ADR_FULL = {"summary": r"^summary", "context": r"^context", "options": r"^options",
            "decision": r"^decision$", "consequences": r"^consequences",
            "risks": r"^risks", "verification": r"^verification"}
ADR_RETRO = ("summary", "context", "decision", "consequences")


def missing_sections(text, keys, table):
    hs = headings(text)
    return [k for k in keys if not any(re.match(table[k], h) for h in hs)]


def adr_condensed(path):
    t = read(path) or ""
    title, status = adr_meta(path)
    keep = []
    for pat in (r"^summary", r"^decision$", r"^consequences"):
        s = get_section(t, lambda x, pat=pat: re.match(pat, x.strip().lower()))
        if s:
            keep.append(s)
    if not keep:
        return clip(t)
    return (f"# {title}\n- Status: {status}\n\n" + "\n\n".join(keep)
            + f"\n\n(condensed; full ADR with options, risks, rollout: {os.path.relpath(path, ROOT)})")


# ---------- PLAN.md ----------
def load_tasks(plan):
    sec = get_section(plan, lambda t: t.strip().lower() == "tasks")
    rows = table_rows(sec)
    for r in rows:
        r["status"] = r.get("status", "").replace("`", "").strip().lower()
        r["track"] = r.get("track", "").replace("`", "").strip().lower()
    return rows


def is_placeholder(row):
    return "TODO" in row.get("task", "") or row.get("task", "").startswith("<")


def current_task(tasks):
    live = [t for t in tasks if not is_placeholder(t) and t["status"] != "done"]
    for t in live:
        if t["status"] == "in progress":
            return t
    return live[0] if live else None


def read_first_tokens(row):
    cell = row.get("read first", "").replace("`", "")
    return [t.strip() for t in re.split(r"[,;]", cell) if t.strip()]


def classify(tok):
    m = re.fullmatch(r"ADR-?0*(\d+)", tok, re.I)
    if m:
        return "adr", int(m.group(1))
    if "#" in tok and tok.split("#")[0].endswith(".md"):
        return "section", tok
    return "path", tok


# ---------- ADRs ----------
def adr_files():
    out = {}
    for f in glob.glob(p("docs", "decisions", "ADR-*.md")):
        m = re.match(r"ADR-0*(\d+)", os.path.basename(f), re.I)
        if m:
            out[int(m.group(1))] = f
    return out


def adr_meta(path):
    t = read(path) or ""
    title = re.search(r"^#\s*(.+)$", t, re.M)
    status = re.search(r"^-?\s*Status:\s*(.+)$", t, re.M)
    return (
        title.group(1).strip() if title else os.path.basename(path),
        status.group(1).strip() if status else None,
    )


def adr_active(status):
    return bool(status) and status.upper().startswith("ACCEPTED")


def adr_index_lines():
    lines = []
    for n, f in sorted(adr_files().items()):
        title, status = adr_meta(f)
        lines.append(f"- {title}  [{status or 'NO STATUS'}]  ({os.path.relpath(f, ROOT)})")
    return lines


# ---------- git / state ----------
def git(*args):
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=20)
        return r.returncode, r.stdout
    except Exception:
        return 1, ""


def is_code(path):
    return not (path in NON_CODE_FILES or path.startswith(NON_CODE_DIRS))


def code_sig():
    rc, out = git("status", "--porcelain", "-uall")
    if rc != 0:
        return None
    paths = []
    for line in out.splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ")[-1]
        paths.append(path.strip('"'))
    code = sorted(x for x in paths if is_code(x))
    h = hashlib.sha256("\n".join(code).encode())
    for x in code:
        try:
            with open(p(x), "rb") as f:
                h.update(f.read())
        except OSError:
            h.update(b"<gone>")
    return h.hexdigest()


def plan_sig():
    return hashlib.sha256((read(p("PLAN.md")) or "").encode()).hexdigest()


STATE = p(".claude", "plan_guard_state.json")


def load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    keep = dict(list(state.items())[-20:])
    try:
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(keep, f)
    except OSError:
        pass


# ---------- commands ----------
def cmd_session_start():
    data = stdin_json()
    plan = read(p("PLAN.md"))
    if plan is None:
        return 0  # not a template project
    sid, source = data.get("session_id", ""), data.get("source", "")
    if sid and source != "compact":
        st = load_state()
        st[sid] = {"code": code_sig(), "plan": plan_sig()}
        save_state(st)

    out = ["[plan_guard] Session context loaded by a hook. Do not re-read what is below;",
           "open only the code paths listed under Read first.", ""]
    now = get_section(plan, lambda t: t.strip().lower() == "now")
    if now:
        out += [now, ""]
    tasks = load_tasks(plan)
    task = current_task(tasks)
    adr_map = adr_files()
    if task:
        out += [f"## Current task {task.get('id', '?')}: {task.get('task', '')}",
                f"- Track: {task.get('track', '?')}   Status: {task.get('status', '?')}",
                f"- Done when: {task.get('done when', '')}",
                f"- Read first: {task.get('read first', '')}", ""]
        docs, paths = [], []
        for tok in read_first_tokens(task):
            kind, val = classify(tok)
            if kind == "adr":
                f = adr_map.get(val)
                if not f:
                    docs.append(f"## {tok}: NOT FOUND in docs/decisions/ (fix PLAN.md)")
                    continue
                title, status = adr_meta(f)
                if adr_active(status):
                    docs.append(f"## {os.path.relpath(f, ROOT)}\n{adr_condensed(f)}")
                elif (status or "").upper().startswith("PROPOSED"):
                    docs.append(f"## {tok}: PROPOSED, awaiting human approval. Do NOT implement against it.")
                else:
                    docs.append(f"## {tok}: status is {status}; do NOT rely on it (see its successor)")
            elif kind == "section":
                path, anchor = val.split("#", 1)
                text = read(p(path))
                sec = get_section(text, lambda t: slug(t) == anchor.lower()) if text else None
                docs.append(f"## {val}\n{clip(sec)}" if sec
                            else f"## {val}: section NOT FOUND (fix PLAN.md or the heading)")
            else:
                paths.append(val)
        for d in docs:
            out += [d, ""]
        if paths:
            out += ["## Code/other paths to open yourself: " + ", ".join(paths), ""]
    else:
        out += ["## No open task in PLAN.md. Add one (with Done when + Read first) before coding.", ""]
    idx = adr_index_lines()
    out += ["## ADR index (open any ADR whose title touches your area)"] + (idx or ["- (none yet)"])
    ctx = "\n".join(out)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                             "additionalContext": ctx}}))
    return 0


def lint():
    errs = []
    plan = read(p("PLAN.md"))
    if plan is None:
        return errs
    tasks = [t for t in load_tasks(plan) if not is_placeholder(t)]
    adr_map = adr_files()
    if sum(1 for t in tasks if t["status"] == "in progress") > 1:
        errs.append("more than one task is `in progress`")
    for t in tasks:
        tid = t.get("id", "?")
        if t["status"] not in VALID_STATUS:
            errs.append(f"{tid}: invalid status '{t['status']}'")
        if t["status"] == "done":
            continue
        if t["track"] not in {"routine", "major"}:
            errs.append(f"{tid}: track must be routine or major")
        for col in ("done when", "read first"):
            v = t.get(col, "")
            if not v or "<" in v:
                errs.append(f"{tid}: '{col}' is empty or still a placeholder")
        adr_toks = [classify(x) for x in read_first_tokens(t) if classify(x)[0] == "adr"]
        if t["track"] == "major" and not adr_toks:
            errs.append(f"{tid}: major task must list its governing ADR in Read first")
        for _, n in adr_toks:
            f = adr_map.get(n)
            if not f:
                errs.append(f"{tid}: ADR-{n} does not exist in docs/decisions/")
            elif not adr_active(adr_meta(f)[1]):
                errs.append(f"{tid}: ADR-{n} is {adr_meta(f)[1]}, not ACCEPTED "
                            "(get approval and set Status: ACCEPTED first)")
        for kind, val in (classify(x) for x in read_first_tokens(t)):
            if kind == "section":
                path, anchor = val.split("#", 1)
                text = read(p(path))
                if text is None or not get_section(text, lambda s: slug(s) == anchor.lower()):
                    errs.append(f"{tid}: Read first '{val}' does not resolve")
    for n, f in adr_map.items():
        status = adr_meta(f)[1]
        if status is None:
            errs.append(f"ADR-{n}: missing '- Status:' line")
            continue
        if status.upper().startswith(("ACCEPTED", "PROPOSED")):
            text = read(f) or ""
            retro = re.search(r"^-?\s*Retroactive:\s*yes", text, re.I | re.M)
            keys = ADR_RETRO if retro else tuple(ADR_FULL)
            miss = missing_sections(text, keys, ADR_FULL)
            if miss:
                errs.append(f"ADR-{n}: missing section(s): {', '.join(miss)}")
    plan_ids = {t.get("id") for t in load_tasks(plan) if not is_placeholder(t)}
    for f in sorted(glob.glob(p("docs", "plans", "*.md"))):
        errs += lint_plan_doc(f, plan_ids)
    log = get_section(plan, lambda t: t.lower().startswith("log"))
    n_rows = sum(1 for r in table_rows(log) if any(r.values()))
    if n_rows > MAX_LOG_ROWS:
        errs.append(f"Log has {n_rows} rows (> {MAX_LOG_ROWS}); move old rows to docs/log-archive.md")
    return errs


def lint_plan_doc(path, plan_ids):
    rel, text, errs = os.path.relpath(path, ROOT), read(path) or "", []
    hs = headings(text)
    for key, pat in (("summary", r"^summary"), ("goal", r"^goal"), ("scope", r"^scope")):
        if not any(re.match(pat, h) for h in hs):
            errs.append(f"{rel}: missing section '{key}'")
    phases = [h for h in hs if re.match(r"^phase\s+\d+", h)]
    if not phases:
        errs.append(f"{rel}: no '## Phase N' sections")
    for ph in phases:
        body = get_section(text, lambda t, ph=ph: t.strip().lower() == ph) or ""
        if "exit criteria" not in body.lower():
            errs.append(f"{rel}: '{ph}' has no Exit criteria")
    for m in re.finditer(r"^###\s+([A-Za-z]+-?\d+)\s*$", text, re.M):
        tid = m.group(1)
        body = get_section(text, lambda t, tid=tid: t.strip().lower() == tid.lower()) or ""
        for label in ("files", "steps"):
            if not re.search(rf"^\W*{label}\b", body, re.I | re.M):
                errs.append(f"{rel}: task {tid} has no '{label.capitalize()}'")
        if tid not in plan_ids:
            errs.append(f"{rel}: task {tid} is not a row in PLAN.md")
    return errs


def cmd_lint():
    errs = lint()
    if errs:
        print("plan_guard lint FAILED:\n" + "\n".join(f"  - {e}" for e in errs))
        return 1
    print("plan_guard lint OK")
    return 0


def cmd_commit_gate():
    data = stdin_json()
    cmd = (data.get("tool_input") or {}).get("command", "")
    if not re.search(r"(^|[;&|]\s*)git\s+(-[cC]\s+\S+\s+)*commit\b", cmd):
        return 0
    errs = lint()
    if errs:
        sys.stderr.write("plan_guard: commit blocked. Fix PLAN.md / ADRs first:\n"
                         + "\n".join(f"  - {e}" for e in errs) + "\n")
        return 2
    return 0


def cmd_stop_gate():
    data = stdin_json()
    if data.get("stop_hook_active"):
        return 0
    if read(p("PLAN.md")) is None:
        return 0
    st = load_state().get(data.get("session_id", ""))
    if not st:
        return 0
    if code_sig() != st.get("code") and plan_sig() == st.get("plan"):
        sys.stderr.write("plan_guard: code changed this session but PLAN.md was not updated. "
                         "Rewrite Now, update the task row, and append one Log line "
                         "(date, what, command -> result), then finish.\n")
        return 2
    return 0


def cmd_adr_index():
    print("\n".join(adr_index_lines()) or "(no ADRs yet)")
    return 0


COMMANDS = {"session-start": cmd_session_start, "commit-gate": cmd_commit_gate,
            "stop-gate": cmd_stop_gate, "lint": cmd_lint, "adr-index": cmd_adr_index}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        sys.stderr.write(__doc__)
        sys.exit(1)
    sys.exit(COMMANDS[sys.argv[1]]())
