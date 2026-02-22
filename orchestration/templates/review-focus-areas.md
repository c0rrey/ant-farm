# Review Focus Areas

Per-type focus blocks for nitpicker review prompts. Each block is delimited
by `<!-- FOCUS: {type} -->` / `<!-- /FOCUS: {type} -->` for awk extraction
in `compose-review-skeletons.sh`.

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
- Excellence: performance, security vulnerabilities, architecture concerns
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
- Excellence: performance of valid paths, security beyond input validation, architecture
<!-- /FOCUS: edge-cases -->

<!-- FOCUS: correctness -->
**Your focus**: The code does what it claims. You review for logical soundness and acceptance criteria compliance.

Focus areas:
1. **Acceptance criteria** — Run `bd show <task-id>` for each task. Did each fix solve what was requested?
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
- Excellence: performance, security hardening, architectural elegance
<!-- /FOCUS: correctness -->

<!-- FOCUS: excellence -->
**Your focus**: Good engineering practice, security, performance, and future maintainability. You review for quality above the functional baseline.

Focus areas:
1. **Best practices** — Does code follow language/framework conventions?
2. **Performance** — Unnecessary loops-in-loops? Repeated expensive ops? N+1 patterns?
3. **Security** — Path traversal? Injection risks? Insecure defaults? Credentials in code/logs?
4. **Maintainability** — High cyclomatic complexity? Deep nesting? Technical debt without justification?
5. **Architecture** — Does this fit project design principles? Does it add a third way to do something done two ways?
6. **Scalability** — Will this perform at 10x scale?

**Severity calibration**:
- P1: Security vulnerability with a realistic exploit path (user input reaching shell/SQL unsanitized)
- P2: Performance issue noticeable at realistic scale, OR significant maintenance burden for next developer
- P3: Best-practice miss that is real but low-stakes (loop→comprehension, missing test, splittable function) (default)

**Not your responsibility** — hand off to the relevant reviewer:
- Clarity: naming, comments, style (don't re-report style as "maintainability" unless architectural)
- Edge Cases: input validation, error handling (don't re-report as security unless active exploit path)
- Correctness: bugs, acceptance criteria (don't report correct-but-inefficient as "correctness")
<!-- /FOCUS: excellence -->
