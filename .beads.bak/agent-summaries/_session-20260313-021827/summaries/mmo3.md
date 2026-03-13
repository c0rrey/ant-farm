# Summary: ant-farm-mmo3 — Migrate agent definitions (mechanical)

**Commit**: 76d02ad
**Files changed**: agents/scout-organizer.md, agents/nitpicker.md

---

## 1. Approaches Considered

**Approach A — Blind global replace_all**
Replace every occurrence of `bd` with `crumb` using `replace_all: true`. Fast but risks collateral replacement of `bd` appearing in non-command contexts (prose, variable names, embedded strings). Not chosen because precision is preferable for agent definition files that serve as authoritative prompts.

**Approach B — Pattern-targeted per-occurrence Edit tool calls**
Replace each `bd` command reference individually using surrounding context as a unique anchor string. Fully auditable per-line, zero risk of collateral substitution, each change independently verifiable against the acceptance criteria line numbers. Selected approach.

**Approach C — Rewrite full files from scratch**
Read content, reconstruct with substitutions, write entire file with Write tool. Highest cognitive overhead, most error-prone for 176-line files, risk of whitespace or formatting drift unrelated to the task. Not chosen.

**Approach D — Shell sed substitution**
Use `sed -i 's/\bbd\b/crumb/g'` via Bash. Quick but macOS vs GNU sed word-boundary regex differences introduce platform risk, harder to audit without re-reading the result, and requires shell invocation when Edit tool is more direct. Not chosen.

---

## 2. Selected Approach with Rationale

Approach B — pattern-targeted per-occurrence Edit tool replacements.

Each Edit call uses a unique surrounding-context anchor, guaranteeing no collateral matches. The 7 individual replacements map precisely to the 7 `bd` command references identified in the task brief (4 in scout-organizer.md, 3 in nitpicker.md). Every change is independently verifiable by re-reading the file after each edit.

---

## 3. Implementation Description

Two sets of edits were applied — first to `~/.claude/agents/` (the live Claude Code agent files), then to `agents/` inside the git-tracked project repo (the source of truth for commits). The project repo copies were discovered by searching for the file names inside the ant-farm project directory; they are separate files (not symlinks) with slightly older content but the same `bd` occurrences at the same logical positions.

**scout-organizer.md replacements (4 occurrences):**
- L3 description: "bd CLI" → "crumb CLI"
- L25 filter mode description: `` `bd list` `` → `` `crumb list` ``
- L33 workflow step 2: `` `bd` CLI `` → `` `crumb` CLI ``
- L35 workflow step 4: `` `bd show` `` → `` `crumb show` ``

**nitpicker.md replacements (3 occurrences):**
- L107 Correctness what-to-look-for: `` `bd show <task-id>` `` → `` `crumb show <task-id>` ``
- L124 Correctness heuristics: `` `bd show <task-id>` `` → `` `crumb show <task-id>` ``
- L172 Cross-review messaging example: `bd show <task-id>` → `crumb show <task-id>`

---

## 4. Correctness Review (per-file)

### agents/scout-organizer.md

Re-read after all edits. All 4 substitutions confirmed present. Surrounding prose is functionally unchanged. The agent description accurately describes behavior (task discovery via crumb CLI). The workflow steps remain logically consistent. No formatting, indentation, or structural changes were introduced.

No adjacent issues fixed. Note for future: the scout.md template referenced at L29 (`~/.claude/orchestration/templates/scout.md`) likely still contains `bd` references — out of scope for this task.

### agents/nitpicker.md

Re-read after all edits. All 3 substitutions confirmed present. The CORRECTNESS REVIEWER section (L107, L124) continues to correctly instruct the reviewer to retrieve acceptance criteria using the CLI. The cross-review messaging example at L172 continues to be a valid illustrative message. No formatting or structural changes were introduced. All other 173 lines are unchanged.

---

## 5. Build/Test Validation

```
grep -c '\bbd\b' agents/scout-organizer.md agents/nitpicker.md
```

Results:
- `agents/scout-organizer.md:0`
- `agents/nitpicker.md:0`

Both files pass the acceptance criterion grep test. The same test was run on the `~/.claude/agents/` copies and also returned 0 on both.

---

## 6. Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| agents/scout-organizer.md: all bd command references replaced with crumb equivalents (L3, L25, L33, L35) | PASS — 4 occurrences replaced |
| agents/nitpicker.md: all 3 bd references replaced with crumb equivalents (L107, L124, L172) | PASS — 3 occurrences replaced |
| `grep -c '\bbd\b'` on both files returns 0 | PASS — both return 0 |
| Agent descriptions and tool references remain functionally correct after substitution | PASS — only CLI tool name changed, all instructions and logic intact |
