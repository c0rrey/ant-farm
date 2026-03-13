# Task: ant-farm-dhh8
**Status**: success
**Title**: Implement crumb search and tree commands
**Type**: task
**Priority**: P2
**Epic**: ant-farm-e7em
**Agent Type**: python-pro
**Dependencies**: {blocks: [], blockedBy: [ant-farm-jmvi]}
**Blocked by**: ant-farm-jmvi (Wave 3)

## Affected Files
- crumb.py -- add search and tree subcommands for full-text search and hierarchical visualization

## Root Cause
N/A (new feature)

## Expected Behavior
Search and visualization: crumb search performs case-insensitive full-text search across titles and descriptions. crumb tree shows all trails and children as indented hierarchy, optionally scoped to a single trail.

## Acceptance Criteria
1. crumb search 'keyword' returns crumbs/trails matching keyword in title or description
2. Search is case-insensitive ('Rate' matches 'rate')
3. crumb tree displays hierarchical view with trails as parents and child crumbs indented
4. crumb tree <trail-id> shows only the specified trail and its children
5. Empty search results produce no output and exit 0
