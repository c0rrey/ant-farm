# Task: ant-farm-fdz2
**Status**: success
**Title**: Implement crumb import and --from-beads migration
**Type**: task
**Priority**: P2
**Epic**: ant-farm-e7em
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: [ant-farm-h7af, ant-farm-jmvi]}
**Blocked by**: ant-farm-h7af (Wave 3), ant-farm-jmvi (Wave 3)

## Affected Files
- crumb.py -- add import subcommand with JSONL validation, --from-beads migration with field mapping

## Root Cause
N/A (new feature)

## Expected Behavior
Bulk import and migration: crumb import validates and imports JSONL entries with duplicate detection and counter updates. crumb import --from-beads converts Beads format with priority mapping, epic-to-trail conversion, and dependency mapping.

## Acceptance Criteria
1. crumb import file.jsonl imports valid JSONL entries and reports count of imported items
2. Malformed JSON lines are skipped with stderr warning including line number
3. Duplicate IDs against existing entries are skipped with stderr warning
4. crumb import --from-beads .beads/issues.jsonl converts beads format to crumb format
5. Beads priority mapping: 0 to P0, 1 to P1, 2 to P2, 3 to P3, 4 to P4
6. Beads type 'epic' becomes type 'trail' with T-prefixed ID
7. next_crumb_id/next_trail_id in config.json updated to exceed highest imported ID
