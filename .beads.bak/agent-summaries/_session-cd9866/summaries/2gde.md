# ant-farm-2gde — Dead GLOSSARY.md link in checkpoints.md

**Status**: CLOSED
**Commit**: fix: replace dead GLOSSARY.md links with inline wave definition (ant-farm-2gde)

## Changes Made

### orchestration/templates/checkpoints.md (line 264)
Removed the dead link `[Glossary: wave](../GLOSSARY.md#workflow-concepts)` — `orchestration/GLOSSARY.md` does not exist in the repository, so the link would 404 for any reader.

Replaced with an inline parenthetical definition:
> (a "wave" is a group of agents spawned in parallel for the same execution round — e.g. all Nitpickers in round 1 constitute one wave)

This keeps the definition self-contained at the point of use without requiring a separate file to exist. The definition is consistent with the usage of "wave" throughout the file (e.g. "Wave 1 of Epic 74g" in the Known failure mode example on line 270).

## Search Results
Only one GLOSSARY.md reference was found in checkpoints.md (confirmed via grep). No other dead links to GLOSSARY.md exist in this file.
