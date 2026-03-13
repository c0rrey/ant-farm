# Task Summary: ant-farm-n3qr

**Task**: Write /ant-farm:status skill definition
**Commit**: f54578b
**File created**: skills/status.md

---

## 1. Approaches Considered

**Approach A: Pure shell pipeline (no intermediate variables)**
Run `crumb trail list` and `crumb list` inline with `awk/grep`, surfacing counts directly. Minimal steps, but brittle against output format changes and hard to debug when a command silently fails. No named state means error recovery is opaque.

**Approach B: Explicit step-by-step with stored intermediate outputs**
Each data source is a named step that stores output in a named variable before formatting. Verbose, maximally debuggable, mirrors the style of `work.md`. Downside: slightly more steps than strictly necessary for a read-only dashboard command.

**Approach C: LLM-synthesized dashboard (no shell commands)**
Let the model summarize status from context window alone. Zero shell latency, but entirely unreliable as a standalone command invoked from a cold context. Not viable.

**Approach D: Pre-flight check + tabular dashboard with graceful degradation**
Structured pre-flight check (`.crumbs/` initialized?), then each data source gathered with explicit fallback sentinels (`HAS_TRAILS`, `HAS_CRUMBS`, `HAS_SESSION`), rendered as a fixed-width dashboard. All six partial-data combinations covered explicitly. Complete/incomplete trails marked with `✓`.

---

## 2. Selected Approach

**Approach D** — Pre-flight + tabular dashboard with graceful degradation.

**Rationale:**
- All six acceptance criteria map cleanly to named steps (Step 0 = AC5/pre-flight, Step 1 = AC2 trails, Step 2 = AC3 status counts, Step 3 = AC4 session, Step 4 = AC6 formatting + AC5 edge cases).
- Named boolean sentinels (`HAS_TRAILS`, `HAS_CRUMBS`, `HAS_SESSION`) make partial-data edge case logic explicit and verifiable.
- Fixed-section dashboard format with separator lines and section headings matches the "concise and scannable" AC6 requirement directly.
- Structural style is consistent with the three existing skills (`init.md`, `plan.md`, `work.md`): pre-flight check, numbered steps, error reference table.

---

## 3. Implementation Description

`skills/status.md` is a 183-line skill definition with YAML frontmatter, trigger conditions, four numbered steps, and an error reference table.

- **Frontmatter**: `name: ant-farm-status`, `description` covering `/ant-farm:status` and natural-language trigger phrases, `version: 1.0.0`.
- **Step 0**: Pre-flight check — verifies `.crumbs/tasks.jsonl` and `.crumbs/config.json` exist; hard-stops with `/ant-farm:init` pointer if not.
- **Step 1**: Calls `crumb trail list` then per-trail `crumb list --trail <id> --short | wc -l` for total and closed counts; sets `HAS_TRAILS`.
- **Step 2**: Calls `crumb list --open/--blocked/--in-progress/--closed --short | wc -l` for four count variables; sets `HAS_CRUMBS`.
- **Step 3**: Finds latest `exec-summary-*.md` via `ls -t ... | head -1`; reads first 20 lines; extracts date from filename; sets `HAS_SESSION`.
- **Step 4**: Renders fixed-width dashboard with TRAILS / CRUMBS / LAST SESSION sections; handles the all-empty edge case (shows "No tasks found" + `/ant-farm:plan` hint) and all three partial-data combinations; marks fully-complete trails with `✓`.

---

## 4. Correctness Review

**File: skills/status.md** (183 lines, no prior version)

- Frontmatter parses correctly: `name`, `description`, `version` fields present; `description` covers the slash command trigger and natural-language variants.
- Step 0 uses the same initialization check pattern (`tasks.jsonl` + `config.json`) as `init.md`, `plan.md`, and `work.md` — consistent.
- Step 1 `crumb trail list` and `crumb list --trail <id> --closed --short` flags are consistent with CLI usage patterns seen in `work.md`.
- Step 2 uses `--open`, `--blocked`, `--in-progress`, `--closed` flags consistent with `work.md` (which uses `crumb list --open --short` and `crumb list --in-progress --short`).
- Step 3 uses `ls -t .crumbs/history/exec-summary-*.md` matching the path and filename pattern stated in the task AC4 and description.
- Step 4 dashboard format: separator line, section headings, one line per trail with `CLOSED/TOTAL closed` notation, `✓` for complete trails. Follows the "concise and scannable" requirement.
- Edge case handling: complete no-data path surfaces to user with `/ant-farm:plan` hint; three partial-data combinations named explicitly; `crumb` CLI not found added to error reference table.

No issues found in review.

---

## 5. Build/Test Validation

This task produces a Markdown skill definition file. There are no compiled artifacts, no tests to run, and no linting configuration applicable to `skills/*.md` files. The file was verified by:
- Re-reading the full file after write (Read tool)
- Manual checklist review against all six acceptance criteria (see section 6)
- Structural comparison against `init.md`, `plan.md`, and `work.md` to confirm format consistency

---

## 6. Acceptance Criteria Checklist

- [x] **AC1** — `skills/status.md` exists with correct skill frontmatter (`name: ant-farm-status`, `description`, `version: 1.0.0`) and trigger pattern (`/ant-farm:status` invocation + natural-language variants in Trigger Conditions section). **PASS**
- [x] **AC2** — Displays trail completion counts using crumb trail list output: Step 1 calls `crumb trail list`, then per-trail `crumb list --trail <id>` for total/closed counts, rendered as `X/Y closed` per trail. **PASS**
- [x] **AC3** — Displays crumb status summary: Step 2 runs all four `crumb list --<status>` commands; Step 4 renders `open`, `in_progress`, `blocked`, `closed` counts in CRUMBS section. **PASS**
- [x] **AC4** — Shows last session summary from most recent `.crumbs/history/exec-summary-*.md`: Step 3 finds the latest file via `ls -t ... | head -1`, reads first 20 lines, renders path and excerpt in LAST SESSION section. **PASS**
- [x] **AC5** — Handles edge case no tasks/no sessions: Step 0 handles uninitialized project; Step 4 "No-data edge case" block handles all three sentinels false; partial-data combinations (trails only, crumbs only, no sessions) handled explicitly. **PASS**
- [x] **AC6** — Output is concise and scannable (dashboard format): fixed-width sections with separator lines, section headings (TRAILS, CRUMBS, LAST SESSION), aligned columns, explicit formatting instructions, no raw command output passthrough. **PASS**
