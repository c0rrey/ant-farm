# Summary: ant-farm-oc9v

**Task**: Incomplete pantry-review deprecation across docs and agent configs
**Status**: Complete
**Commit**: (see below)

## 1. Approaches Considered

**Approach A: Remove pantry-review from scout.md exclusion list entirely**
The exclusion list is a runtime instruction the Scout uses when building its agent catalog. The pantry-review agent file has been moved to `orchestration/_archive/` and no longer exists as an active agent at `~/.claude/agents/`. Listing a non-existent agent as an exclusion is a dead reference. Removing it keeps the list accurate and avoids confusing future readers.
- Pros: Clean, accurate, machine-parseable list remains intact.
- Cons: Loses explicit history that pantry-review was once an orchestration agent.

**Approach B: Add strikethrough markup in scout.md exclusion list**
Change `pantry-review` to `~~pantry-review~~ (deprecated)` in the comma-separated list, consistent with how GLOSSARY.md handles the same agent.
- Pros: Preserves historical awareness with a consistent convention.
- Cons: The exclusion list is a comma-separated directive read by the Scout at runtime. Inline strikethrough and parenthetical text within a list value could cause the Scout to parse `~~pantry-review~~` as an exclusion name, which no agent matches — harmless but potentially confusing.

**Approach C: Add a trailing note line after the exclusion list**
Keep the list clean and add a separate line: `(pantry-review deprecated — removed from list; see RULES.md Step 3b)`
- Pros: Clean list, readable note.
- Cons: More verbose. The context is self-evident: the surrounding prose already describes these as orchestration agents, and pantry-review's deprecation is documented in GLOSSARY.md and README.md.

**Approach D: Replace pantry-review with a parenthetical note on the same line**
`scout-organizer, pantry-impl, pest-control, nitpicker, big-head  _(pantry-review deprecated; archived)_`
- Pros: One-line, brief, keeps context.
- Cons: Mixes list and prose on the same line; markdown italics in a directive line is unusual.

## 2. Selected Approach

**Approach A — Remove pantry-review from scout.md exclusion list entirely.**

Rationale: The exclusion list serves a runtime purpose: filter out agent names that should not be recommended as Dirt Pushers. Since pantry-review's agent file no longer exists in the active agents directory, the Scout's dynamic discovery will not find it in the first place. The entry is dead. Removing it keeps the list accurate without any markup clutter. The deprecation is already documented in GLOSSARY.md:L28 (strikethrough) and README.md:L309 (DEPRECATED label) — there is no need to repeat it in a runtime filter list.

## 3. Implementation Description

Single edit to `orchestration/templates/scout.md`:

**Before (line 63):**
```
scout-organizer, pantry-impl, pantry-review, pest-control, nitpicker, big-head
```

**After (line 63):**
```
scout-organizer, pantry-impl, pest-control, nitpicker, big-head
```

No other files required edits. The other three files cited in the task (RULES.md, GLOSSARY.md, README.md) were already in a correct deprecation state:
- `GLOSSARY.md:L28` — uses `~~pantry-review.md~~` (deprecated; see RULES.md Step 3b)
- `GLOSSARY.md:L81` — uses `~~agents/pantry-review.md~~` (deprecated; see RULES.md Step 3b)
- `README.md:L309` — uses `~~Review prompt composer...~~ **DEPRECATED** — replaced by fill-review-slots.sh`
- `RULES.md` — no pantry-review references exist anywhere (task yb95 already cleaned this)

The RULES.md L182-183 finding referenced in the task brief had stale line numbers: those lines in the current file contain Nitpicker team spawn instructions, not any pantry-review content. Task yb95 (closed 2026-02-20) addressed the RULES.md table rows.

## 4. Correctness Review

**orchestration/templates/scout.md** — Changed
- Line 63: `pantry-review` removed from exclusion list. Surrounding prose on line 60 refers to "orchestration agents (scout, pantry, pest-control, etc.)" — the `etc.` gracefully covers the deprecated case without needing an update.
- No other lines in scout.md reference pantry-review (confirmed by grep).
- The list format is still valid comma-separated syntax; no trailing comma left behind.

**orchestration/RULES.md** — Not changed (already clean)
- Full grep for `pantry-review` returns no matches.
- Lines 182-183: Pest Control / Templates instructions — no pantry-review content.

**orchestration/GLOSSARY.md** — Not changed (already correct)
- L28: `~~pantry-review.md~~` (deprecated; see RULES.md Step 3b) — proper strikethrough deprecation marker present.
- L81: `~~agents/pantry-review.md~~` (deprecated; see RULES.md Step 3b) — proper strikethrough deprecation marker present.

**README.md** — Not changed (already correct)
- L309: `~~Review prompt composer...~~ **DEPRECATED** — replaced by fill-review-slots.sh bash script; see RULES.md Step 3b` — proper DEPRECATED label present.

**Adjacent issues documented (not fixed):**
- `docs/plans/2026-02-19-review-loop-convergence.md:L455` references `pantry-review` in a historical plan document. This is outside scope and is a planning artifact, not a live workflow document.
- `scripts/fill-review-slots.sh:L5` mentions pantry-review in a comment explaining the replacement. This is accurate prose and outside scope.

## 5. Build/Test Validation

This is a documentation-only change. No build steps or automated tests apply.

Manual validation:
- Grep confirms `pantry-review` no longer appears in `orchestration/templates/scout.md`.
- Grep confirms `pantry-review` does not appear in `orchestration/RULES.md`.
- GLOSSARY.md and README.md references confirmed to carry proper deprecation markers.
- scout.md exclusion list syntax is valid: five comma-separated agent type names, no trailing comma, no stray markup.

## 6. Acceptance Criteria Checklist

1. **No file references pantry-review without a deprecation marker** — PASS
   - scout.md: reference removed entirely (no marker needed for a removed entry)
   - RULES.md: no references
   - GLOSSARY.md L28: `~~pantry-review.md~~` (deprecated) — marker present
   - GLOSSARY.md L81: `~~agents/pantry-review.md~~` (deprecated) — marker present
   - README.md L309: `~~...~~ **DEPRECATED**` — marker present

2. **GLOSSARY.md:L28 and L81 updated to remove or mark deprecated pantry-review references** — PASS
   - Both lines already carry strikethrough + "(deprecated; see RULES.md Step 3b)" — no edit required

3. **scout.md:L61 exclusion list cleaned up (remove stale pantry-review entry or mark deprecated)** — PASS
   - `pantry-review` removed from the exclusion list on line 63 (was L63 at time of edit; task brief cited L61 as approximate range)

4. **RULES.md:L182-183 deprecated row wording unified (remove duplication)** — PASS
   - No pantry-review content exists anywhere in RULES.md; already cleaned by task yb95
