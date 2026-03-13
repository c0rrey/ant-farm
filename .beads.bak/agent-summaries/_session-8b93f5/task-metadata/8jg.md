# Task: ant-farm-8jg
**Status**: success
**Title**: AGG-026: Standardize agent name casing and article usage
**Type**: task
**Priority**: P2
**Epic**: ant-farm-amk
**Agent Type**: refactoring-specialist
**Dependencies**: blocks: [], blockedBy: [ant-farm-jxf]

## Affected Files
- orchestration/templates/*.md — All template files with prose references to agent names (the Queen, The Queen, the Nitpickers, etc.)
- orchestration/RULES.md — Prose references to agent names
- README.md — Prose references and any architecture diagrams with agent names

## Root Cause
Agent names are capitalized and articled inconsistently: the Queen / Queen / The Queen, the Nitpickers / Nitpicker team, Big Head always title case. Filenames use kebab-case while prose mixes forms.

## Expected Behavior
Standardized convention: lowercase article in prose (the Queen, the Scout), title case for role names, kebab-case in filenames. Convention documented in glossary (which ant-farm-jxf creates).

## Acceptance Criteria
1. All prose references use consistent article/casing pattern (e.g., the Queen not The Queen)
2. All filenames use kebab-case for agent names
3. The naming convention is documented in the glossary
