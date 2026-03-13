# Task: ant-farm-l7pk
**Status**: success
**Title**: Implement crumb create, show, list commands
**Type**: task
**Priority**: P1
**Epic**: ant-farm-e7em
**Agent Type**: python-pro
**Dependencies**: {blocks: [ant-farm-cmcd, ant-farm-h7af, ant-farm-jmvi], blockedBy: [ant-farm-mg0r]}
**Blocked by**: ant-farm-mg0r (Wave 1)

## Affected Files
- crumb.py -- add create, show, list subcommands with filter flags, auto-ID assignment, duplicate detection

## Root Cause
N/A (new feature)

## Expected Behavior
Core CRUD read commands: crumb create with auto-ID and --from-json, crumb show for full detail display, crumb list with composable filter flags (--open, --closed, --priority, --type, --sort, --limit, --short, etc.).

## Acceptance Criteria
1. crumb create --title 'test task' creates entry in tasks.jsonl with auto-assigned ID matching config prefix
2. crumb create --from-json '{"title":"test","priority":"P1","type":"task"}' creates with explicit fields, auto-assigns ID if omitted
3. crumb show <id> displays all fields (title, status, priority, description, acceptance_criteria, scope, links, notes, timestamps)
4. crumb list --open --priority P1 --sort priority --limit 5 correctly applies all filters, sorts, and limits
5. crumb list --short shows compact one-line-per-crumb output (ID, title, status, priority only)
6. crumb list --after 2026-03-12 returns only crumbs created after the specified ISO 8601 date
7. Creating a crumb with a duplicate ID exits 1 with stderr error message
