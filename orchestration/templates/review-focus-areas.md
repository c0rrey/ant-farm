# Review Focus Areas

Per-type focus blocks for nitpicker review prompts. Each block is delimited
by `<!-- FOCUS: {type} -->` / `<!-- /FOCUS: {type} -->` for awk extraction
in `build-review-prompts.sh`.

<!-- FOCUS: clarity -->
**Your focus**: Readable, consistent, well-documented code. You review for human comprehension.

Focus areas:
1. **Code readability** — Are variable names clear? Is logic easy to follow?
2. **Documentation** — Are docstrings complete? Are comments helpful (not misleading or stale)?
3. **Consistency** — Do changes follow project patterns and style within the same file/module?
4. **Naming** — Are functions, variables, and fields well-named?
5. **Structure** — Is code organized logically? Does a reader need to scan back-and-forth?

**Severity calibration**:
- P1: A name or comment is actively misleading and would cause a developer to introduce a bug
- P2: A name or structure requires significant effort to understand and would slow future fixes
- P3: A name could be clearer, a comment is missing, style is inconsistent but not confusing (default)

**Not your responsibility** — hand off to the relevant reviewer:
- Edge Cases: missing input validation, error handling gaps, boundary conditions
- Correctness: logic bugs, acceptance criteria, algorithm correctness
- Drift: stale cross-file references, incomplete propagation of changes, broken assumptions
<!-- /FOCUS: clarity -->

<!-- FOCUS: edge-cases -->
**Your focus**: Defensive code that handles the unexpected. You review for robustness at the boundaries.

Focus areas:
1. **Input validation** — What happens with malformed input? Missing fields? Invalid values?
2. **Error handling** — Are exceptions caught? Are error messages helpful (not swallowed silently)?
3. **Boundary conditions** — Empty strings? None/null? Zero-length lists? Max values? Off-by-one?
4. **File operations** — What if files don't exist? Can't be read? Can't be written?
5. **Concurrency** — Race conditions? Lock contention? Shared-state mutations?
6. **Platform differences** — Path separators? Line endings? Locale-dependent parsing?

**Severity calibration**:
- P1: Unhandled edge case causes data loss, crashes a process, or corrupts persistent state
- P2: Unhandled edge case causes incorrect behavior the user will notice but can recover from
- P3: Defensive check missing but condition is highly unlikely or failure mode is obvious (default)

**Not your responsibility** — hand off to the relevant reviewer:
- Clarity: naming, comments, style, structural organization
- Correctness: happy-path logic correctness, acceptance criteria (given valid inputs)
- Drift: stale cross-file references, incomplete propagation of changes, broken assumptions
<!-- /FOCUS: edge-cases -->

<!-- FOCUS: correctness -->
**Your focus**: The code does what it claims. You review for logical soundness and acceptance criteria compliance.

Focus areas:
1. **Acceptance criteria** — Run `crumb show <task-id>` for each task. Did each fix solve what was requested?
2. **Logic correctness** — Inverted conditions? Off-by-one? Wrong operator precedence? Always-true/false?
3. **Data integrity** — Are all data transformations correct? No data loss between source and destination?
4. **Regression risks** — Could changes to shared state or common functions break other callers?
5. **Cross-file consistency** — If file A exports a contract file B depends on, do they still agree?
6. **Algorithm correctness** — Sorting, filtering, aggregation, calculations — are they right?

**Severity calibration**:
- P1: Wrong output for common production inputs, OR an acceptance criterion is explicitly unmet
- P2: Wrong output for occasional inputs, OR high-confidence regression in a shared function
- P3: Theoretical logic error needing unusual conditions, or cosmetic cross-file inconsistency (default)

**Not your responsibility** — hand off to the relevant reviewer:
- Clarity: naming, comments, style (even if logic is correct but hard to read)
- Edge Cases: what happens with invalid inputs (your scope is valid-input behavior)
- Drift: stale cross-file references, incomplete propagation of changes, broken assumptions
<!-- /FOCUS: correctness -->

<!-- FOCUS: drift -->
**Your focus**: The system agrees with itself after this change. You review for stale assumptions across file boundaries.

Focus areas:
1. **Value propagation** — Did a changed value, name, count, or path get updated everywhere it appears?
2. **Caller/consumer updates** — When a function signature or type shape changed, do all call sites match?
3. **Config/constant drift** — Were renamed or removed config keys, env vars, or constants cleaned up everywhere?
4. **Reference validity** — Do hardcoded line numbers, section names, URLs, or file paths still resolve?
5. **Default value copies** — When a default changed at the source of truth, do hardcoded copies elsewhere still match?
6. **Stale documentation** — Do comments, docstrings, and error messages still describe what the code actually does?

**Severity calibration**:
- P1: Stale assumption causes runtime failure or silently wrong results in a common path
- P2: Stale assumption creates inconsistency a developer will encounter but can work around
- P3: Stale reference that is cosmetic or low-impact (default)

**Not your responsibility** — hand off to the relevant reviewer:
- Clarity: naming quality, comment style, readability (even within a single file)
- Edge Cases: missing validation, error handling, boundary conditions
- Correctness: whether logic is right given current inputs (bugs, not drift)
<!-- /FOCUS: drift -->
