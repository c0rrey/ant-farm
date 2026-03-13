# Fix Brief: ant-farm-wzno

## Context
Review finding RC-3 (P2): In `scripts/parse-progress-log.sh`, the key-value store section (~line 104-150) has a heading comment claiming "POSIX-compatible" design, but the script freely uses bash-only constructs like `[[ =~ ]]` (line ~169). The actual portability target is bash 3+ (avoiding `declare -A` which requires bash 4+), not POSIX sh.

## Fix
Reword the comment heading for the key-value store section. Change from claiming "POSIX-compatible" to accurately stating "Bash 3+-compatible key-value store (replaces bash 4+ `declare -A`)". This clarifies the actual portability target without changing any code.

## Scope Boundaries
- **Edit ONLY**: `scripts/parse-progress-log.sh` (the key-value store section heading comment, around lines 104-110)
- **Do NOT edit**: Any other file or any code logic

## Acceptance Criteria
1. The comment heading no longer claims "POSIX-compatible" or "POSIX" compatibility
2. The comment accurately states "Bash 3+" as the portability target
3. No code logic is changed — only the comment text
