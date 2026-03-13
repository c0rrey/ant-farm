# Global User Instructions

## Prompt Engineering Mode

When a message starts with **"Create a prompt:"**, follow this workflow exactly:

**Persona**: You are an expert AI engineer with deep experience translating requirements into high-quality prompts that provide maximum context, clear constraints, and reliable outputs.

**Step 1 - Clarifying Questions**: Before writing any prompt, analyze the request and identify 16 high-impact clarifying questions that fill in details the user left out. These should cover:
- Target model/platform and intended use context
- Input format and data the prompt will receive
- Desired output format, length, and structure
- Tone, voice, and audience
- Edge cases and error handling expectations
- Success criteria and quality bar
- Constraints, guardrails, or things to avoid
- Examples of good/bad output (if relevant)
- How the prompt will be used (one-shot, system prompt, agent instruction, etc.)
- Domain-specific context that would improve results

Present these as multiple-choice questions using the platform's question tool (4 questions per call, so 4 rounds of questions). Wait for all answers before proceeding.

> **Platform compatibility**: Use the tool name that matches your environment — `AskUserQuestion` in Claude Code, `AskQuestion` in Cursor, or plain conversational turns if no dedicated question tool is available.

**Step 2 - Write the Prompt**: After collecting all answers, write a production-quality prompt that:
- Incorporates every answer into the prompt design
- Uses clear structure (role, context, instructions, constraints, output format)
- Includes examples where they would improve reliability
- Is ready to copy-paste and use immediately

**Step 3 - Output**: Present the final prompt in a single fenced code block. After the code block, add a brief "Design Notes" section explaining key decisions you made and any tradeoffs.

## Parallel Work Mode ("Let's get to work")

**Trigger**: When the user says "let's get to work" (case-insensitive, anywhere in message).

**CRITICAL — read before doing ANYTHING:**
- **NEVER** run `crumb show`, `crumb ready`, `crumb list`, `crumb blocked`, or any `crumb` query command — the Scout does this
- NEVER read task/issue details from the user's message and act on them directly.
- NEVER set `run_in_background` on Task agents. Multiple Task calls in one message already run concurrently. Background mode causes raw JSONL transcript leakage into your context.
- Read `~/.claude/orchestration/RULES.md` FIRST and ALONE — no parallel tool calls. Then follow it.

**Process**: Read `~/.claude/orchestration/RULES.md` and follow the workflow steps. RULES.md contains the step sequence, hard gates, concurrency rules, and a template lookup table pointing to the specific template files needed at each phase.

**Process Documentation:** See `~/.claude/orchestration/` for detailed workflows:
- `RULES.md` — Workflow steps, hard gates, concurrency rules (always loaded)
- `templates/` — Agent prompts, checkpoints, reviews (read on demand)
- `reference/` — Dependency analysis, known failures (read when needed)

**Key rule**: After SSV PASS, the Queen auto-proceeds to Step 2. No user approval required for execution strategy.

## Landing the Plane (Session Completion)

(Corresponds to RULES.md Step 6.)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Review-findings gate** — If reviews ran and found P1 issues, present findings to user before proceeding. User decides: fix now, or document deferred P1s in CHANGELOG and push. Do NOT push with undisclosed P1 blockers. If no reviews ran or no P1s exist, proceed.
4. **Update issue status** - Close finished work, update in-progress items
5. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
6. **Clean up** - Clear stashes, prune remote branches
   (Session artifacts in .crumbs/agent-summaries/_session-*/ are retained for posterity. Prune old sessions manually when needed.)
7. **Verify** - All changes committed AND pushed
8. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
