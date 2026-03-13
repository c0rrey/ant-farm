# Task: ant-farm-x0m
**Status**: success
**Title**: Wave concept used in RULES.md but never defined
**Type**: task
**Priority**: P3
**Epic**: ant-farm-amk
**Agent Type**: technical-writer
**Dependencies**: blocks: [ant-farm-1jo, ant-farm-5q3], blockedBy: [ant-farm-jxf]

## Affected Files
- orchestration/RULES.md — References "Next agent in wave" in Hard Gates table, needs wave definition
- orchestration/templates/checkpoints.md — References "BEFORE spawning next agent in same wave"
- orchestration/GLOSSARY.md (new, created by ant-farm-jxf) — Add wave definition here

## Root Cause
RULES.md Hard Gates table references "Next agent in wave" and checkpoints.md says "BEFORE spawning next agent in same wave". The concept of a wave (batch of parallel agents) is never defined anywhere.

## Expected Behavior
Glossary entry added: "Wave: a batch of agents spawned in parallel. Wave N completes before Wave N+1 begins." Cross-references added from RULES.md and checkpoints.md to the glossary definition.

## Acceptance Criteria
1. Glossary contains a canonical definition for "wave"
2. RULES.md and checkpoints.md reference the glossary definition rather than using the term undefined
3. Definition specifies the sequential relationship between waves (Wave N completes before Wave N+1 begins)

## Note on Downstream Blockers
- ant-farm-5q3 (P1) has a SECOND blocker (ant-farm-98c, external P3 bug) — completing x0m alone will not unblock ant-farm-5q3
