# RC2–RC5 Post-Session Fixes

**Issues closed**: ant-farm-abff, ant-farm-49z4
**Commit**: a6d2ee2

## Fix 1 — Incomplete "Correctness Redux" Rename (ant-farm-abff)

Three files missed the canonical rename from "Correctness Redux" to "Correctness" / "Correctness Review":

| File | Line | Old | New |
|------|------|-----|-----|
| `README.md` | 149 | `Correctness Redux` | `Correctness` |
| `orchestration/GLOSSARY.md` | 84 | `Correctness Redux (P1–P2)` | `Correctness (P1–P2)` |
| `orchestration/templates/SESSION_PLAN_TEMPLATE.md` | 211 | `Correctness Redux Review` | `Correctness Review` |

Acceptance criterion verified: `grep -rn "Correctness Redux" orchestration/ README.md --exclude-dir=_archive` returns zero matches.

## Fix 2 — Stale Timestamp Format in PLACEHOLDER_CONVENTIONS.md (ant-farm-49z4)

| File | Line | Old | New |
|------|------|-----|-----|
| `orchestration/PLACEHOLDER_CONVENTIONS.md` | 65 | `YYYYMMDD-HHMMSS` | `YYYYMMDD-HHmmss` |

`HHmmss` is the correct mixed-case convention (hours uppercase, minutes/seconds lowercase) consistent with the canonical definition established elsewhere in the project.

Acceptance criterion verified: `grep -n "HHMMSS" orchestration/PLACEHOLDER_CONVENTIONS.md` returns zero matches.

## Notes

- Both fixes are pure propagation misses — no logic or design changes.
- Remote push intentionally deferred per session instructions.
