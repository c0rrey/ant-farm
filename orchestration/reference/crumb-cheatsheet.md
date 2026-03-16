# crumb CLI Cheat Sheet

## Commands

**create** — Create a new crumb
```
crumb create --title "Title" [--priority P0-P4] [--type task|bug|feature] [--description TEXT]
crumb create --from-json '{"title":"Fix login","priority":"P1","type":"bug"}'
```

**show** — Show full detail for a crumb or trail
```
crumb show <ID>
crumb show AF-141
```

**list** — List crumbs (use --short for compact output)
```
crumb list [--open|--closed|--in-progress] [--priority P0-P4] [--type task|bug|feature] [--short]
crumb list --open --priority P1 --short
```

**update** — Update fields or append a note
```
crumb update <ID> [--status open|in_progress|closed] [--priority P0-P4] [--note TEXT] [--title TEXT]
crumb update AF-141 --status in_progress
crumb update AF-141 --from-json '{"priority":"P0","status":"in_progress"}'
```

**close** — Close one or more crumbs
```
crumb close <ID> [<ID> ...]
crumb close AF-141
```

**link** — Add a relationship to a crumb
```
crumb link <ID> [--parent <ID>] [--blocked-by <ID>] [--remove-blocked-by <ID>] [--discovered-from <ID>]
crumb link AF-142 --blocked-by AF-141
```

**trail create** — Create a trail (epic/milestone container)
```
crumb trail create --title "Title" [--priority P0-P4] [--description TEXT] [--acceptance-criteria TEXT]
crumb trail create --title "Auth overhaul" --priority P1
```

**trail show** — Show a trail and its child crumbs
```
crumb trail show <TRAIL-ID>
crumb trail show AF-T3
```

**doctor** — Validate tasks.jsonl integrity
```
crumb doctor [--fix]
crumb doctor --fix
```

---

## Gotchas

- **--from-json takes inline JSON string, not a file path.**
  Correct: `--from-json '{"priority":"P1"}'`
  Wrong: `--from-json ./data.json`

- **Priority values are strings P0–P4, not integers.**
  Correct: `--priority P1`
  Wrong: `--priority 1`

- **--short flag only works with `crumb list`, not show or other subcommands.**

- **link positional arg order: the crumb being described comes first.**
  `crumb link AF-142 --blocked-by AF-141` means AF-142 is blocked by AF-141.

- **crumb show, crumb ready, crumb list, crumb blocked** are Scout-only reads.
  The Queen must not call these directly — let the Scout digest them.
