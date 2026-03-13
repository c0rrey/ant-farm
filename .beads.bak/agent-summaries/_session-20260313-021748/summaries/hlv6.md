# Summary: ant-farm-hlv6
**Task**: Create decomposition orchestration template
**Agent**: prompt-engineer
**Status**: completed
**Files changed**: orchestration/templates/decomposition.md

## Approaches Considered

### 1. Accept file as-is (no changes)
**Strategy**: xtu9 already created orchestration/templates/decomposition.md with substantial content covering all 9 workflow steps. Treat the file as complete and verify each acceptance criterion passes against the existing content.
**Pros**: Zero change risk; no possibility of introducing regressions into a file already shaped by prior intent.
**Cons**: AC3 requires "full JSON payloads" — the existing JSON example used placeholder `"..."` strings, not a realistic populated payload. A reader following the template would not know what a valid, production-ready JSON looks like. This gap is a genuine deficiency, not a subjective judgment.

### 2. Add full JSON example inline in Step 7 (selected)
**Strategy**: Insert a complete, domain-realistic crumb JSON payload immediately after the field-template structure in Step 7's "Create Crumbs" section, alongside a `cat > /tmp/...` bash example that shows how to write it to disk.
**Pros**: Placed exactly where a reader naturally looks for CLI usage; uses realistic Python-domain field values (auth service, pytest assertions) that model what good acceptance criteria and file lists look like; no structural changes to the file.
**Cons**: Increases file length by ~36 lines.

### 3. Add a "Worked Example" appendix at the end
**Strategy**: Add a new section at the bottom of the file with a full end-to-end trace showing trail creation, 2-3 crumbs with full JSON, and all dep-add calls.
**Pros**: Comprehensive; shows the complete sequence in one place.
**Cons**: Separates the example from the Step 7 instructions, requiring the reader to context-switch. An appendix can be skimmed or missed. The acceptance criterion specifically says "command examples" — inline is more natural than a separate appendix.

### 4. Add a CLI Quick Reference section before the Prohibitions
**Strategy**: Add a new "Quick Reference" section after Step 9 listing every CLI command pattern with descriptions, like a cheat sheet.
**Pros**: Fast scanning for readers who already understand the workflow and just need syntax.
**Cons**: Duplicates information already in Step 7; creates maintenance burden (two places to update if syntax changes); does not address AC3's "full JSON payloads" requirement specifically.

## Selected Approach
**Choice**: Approach 2 — add full JSON example inline in Step 7.
**Rationale**: The gap was specifically in AC3 ("full JSON payloads"). Approach 2 closes that gap with zero structural disruption, placed where a reader would naturally look. Approach 3 was rejected because separation from the instructions weakens the example's discoverability. Approach 4 was rejected because it duplicates existing content without solving the AC3 gap.

## Implementation

The existing file (created by xtu9) already satisfied 5 of 6 acceptance criteria. The gap was AC3: the JSON object template used `"..."` placeholder strings instead of a realistic, fully-populated example.

Added two blocks immediately after the field-template structure in Step 7 "Create Crumbs":

1. A **full JSON example** with realistic field values: a Python auth service session store crumb with 5 concrete acceptance criteria (test command, return value assertions, error behavior), 5 specific file paths, and `python-pro` agent type.

2. A **bash example** showing the `cat > /tmp/crumb-session-store.json << 'EOF'` pattern for writing the JSON to a temp file before running `bd create --from-json`.

The example values were chosen to model best practices: pytest-style assertions (testable, not vague), specific error message text, concrete token format constraints, domain-appropriate file paths.

## Correctness Review

### orchestration/templates/decomposition.md
- **Re-read**: yes (full file, 411 lines)
- **Acceptance criteria verified**:
  - AC1: File exists with clear step-by-step workflow (Steps 1-9 each have a heading and prose) — PASS
  - AC2: Input reading order defined — Step 1 lists spec.md first (#1), then 4 research briefs (#2-5), Step 2 scans codebase after — PASS
  - AC3: Full JSON payloads included — new example at lines 228-265 has all fields populated with realistic values — PASS
  - AC4: blocked_by wiring guidance — Step 5 has 5 named dependency rules; Step 7 Wire Blocked-By section has CLI command with BLOCKER/BLOCKED argument order; Dolt mode warning included — PASS
  - AC5: scope.files and scope.agent_type guidance with examples — Step 4 Agent Type Assignment has 3-rule lookup table with .py/.ts/.go examples; Crumb Fields section documents both fields; full JSON example shows concrete values — PASS
  - AC6: decomposition-brief.md output template included — Step 8 has complete markdown template with 7 required sections — PASS
- **Issues found**: None after correction.
- **Cross-file consistency**: architect-skeleton.md references `~/.claude/orchestration/templates/decomposition.md` and uses consistent CLI syntax (`bd trail create`, `bd create --from-json`, `bd dep add`). The new example uses the same command forms. No inconsistency introduced.

## Build/Test Validation
- **Command run**: n/a — this is a markdown template file with no executable components; no build or test commands apply.
- **Result**: File is syntactically valid markdown. All code blocks have matching opening/closing fences. No broken table syntax.

## Acceptance Criteria
- [x] orchestration/templates/decomposition.md exists with clear step-by-step workflow — PASS
- [x] Input reading order defined: spec.md first, then research briefs, then codebase structure — PASS
- [x] crumb trail create and crumb create --from-json command examples with full JSON payloads included — PASS
- [x] blocked_by wiring guidance: when to add dependencies, how to detect data/API dependencies — PASS
- [x] scope.files and scope.agent_type assignment guidance with examples — PASS
- [x] decomposition-brief.md output template included — PASS

## Commit
**Hash**: ebcffeb
