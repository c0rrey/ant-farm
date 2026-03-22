# crumb --json Output Schema

The `crumb` CLI accepts a `--json` flag on six commands. When present the
command writes structured JSON to stdout instead of human-readable text. This
document is the canonical reference for that schema.

The MCP server (`mcp_server.py`) is a thin wrapper around the same commands and
returns identical JSON objects. Every field and example below applies to both
the CLI and MCP paths.

---

## Crumb Object

A **crumb object** is the core data structure returned by `list`, `show`,
`create`, `search`, and (on success) `update`.

### Required Fields

All ten fields below are always present. If the field was never set on a
crumb the value is `null`.

| Field                 | Type              | Description                                                   |
| --------------------- | ----------------- | ------------------------------------------------------------- |
| `id`                  | string            | Unique identifier, e.g. `"AF-42"` or trail `"AF-T3"`.        |
| `title`               | string            | Short human-readable title.                                   |
| `type`                | string            | One of `"task"`, `"bug"`, `"feature"`, `"trail"`.            |
| `status`              | string            | One of `"open"`, `"in_progress"`, `"closed"`.                |
| `priority`            | string            | One of `"P0"`, `"P1"`, `"P2"`, `"P3"`, `"P4"`.              |
| `description`         | string \| null    | Free-form description text.                                   |
| `acceptance_criteria` | string \| null    | Free-form acceptance criteria text.                           |
| `scope`               | object \| null    | Arbitrary scope metadata (e.g. `{"files": ["crumb.py"]}`).   |
| `links`               | object \| null    | Relationship map, e.g. `{"parent": "AF-T1", "blocked_by": ["AF-10"]}`. |
| `notes`               | array \| null     | List of timestamped note objects appended via `--note`.       |

### Optional Fields

Extra fields stored on the record are preserved and appended after the
required fields. Common optional fields:

| Field        | Type   | Description                                       |
| ------------ | ------ | ------------------------------------------------- |
| `created_at` | string | ISO 8601 timestamp of creation, e.g. `"2026-03-22T14:05:00Z"`. |
| `updated_at` | string | ISO 8601 timestamp of last update.               |
| `agent_type` | string | Agent type hint stored on the crumb, e.g. `"technical-writer"`. |

---

## Per-Command Output Format

| Command                    | Output shape     | Notes                                                       |
| -------------------------- | ---------------- | ----------------------------------------------------------- |
| `crumb list --json`        | array of objects | Empty array `[]` when no crumbs match the filters.         |
| `crumb show <id> --json`   | single object    | Exits non-zero if the ID is not found.                      |
| `crumb create ... --json`  | single object    | The newly created crumb.                                    |
| `crumb update ... --json`  | update envelope  | Object with a `success` key plus the full crumb fields.     |
| `crumb doctor --json`      | diagnostic object| Fields: `ok`, `error_count`, `warning_count`, `errors`, `warnings`, `fixes_applied`. |
| `crumb search <q> --json`  | array of objects | Same shape as `list`. Empty array when nothing matches.     |

---

## Examples

### `crumb list --json`

Returns an array. Each element is a crumb object.

```json
[
  {
    "id": "AF-1",
    "title": "Write installation guide",
    "type": "task",
    "status": "closed",
    "priority": "P2",
    "description": "Document the setup steps for new contributors.",
    "acceptance_criteria": "Installation guide exists in docs/.",
    "scope": {"files": ["docs/installation-guide.md"]},
    "links": {"parent": "AF-T1"},
    "notes": null,
    "created_at": "2026-03-01T10:00:00Z",
    "updated_at": "2026-03-10T09:15:00Z"
  },
  {
    "id": "AF-2",
    "title": "Add --json flag to all commands",
    "type": "feature",
    "status": "closed",
    "priority": "P1",
    "description": null,
    "acceptance_criteria": null,
    "scope": null,
    "links": null,
    "notes": null,
    "created_at": "2026-03-02T08:30:00Z",
    "updated_at": null
  }
]
```

### `crumb show <id> --json`

Returns a single crumb object (not wrapped in an array).

```json
{
  "id": "AF-42",
  "title": "Refactor auth module",
  "type": "bug",
  "status": "in_progress",
  "priority": "P1",
  "description": "The auth module raises a KeyError on missing env vars.",
  "acceptance_criteria": "No unhandled exceptions on missing env vars.",
  "scope": {"files": ["auth.py"]},
  "links": {"blocked_by": ["AF-39"]},
  "notes": [
    {"timestamp": "2026-03-20T11:00:00Z", "text": "Reproduced locally."}
  ],
  "created_at": "2026-03-15T14:00:00Z",
  "updated_at": "2026-03-20T11:00:00Z",
  "agent_type": "engineer"
}
```

### `crumb create --title "..." --json`

Returns the newly created crumb object. All required fields are present;
fields not supplied at creation time are `null`.

```json
{
  "id": "AF-101",
  "title": "Improve error messages",
  "type": "task",
  "status": "open",
  "priority": "P3",
  "description": null,
  "acceptance_criteria": null,
  "scope": null,
  "links": null,
  "notes": null,
  "created_at": "2026-03-22T18:00:00Z",
  "updated_at": null
}
```

### `crumb update <id> --status=in_progress --json`

On success, returns an **update envelope**: a `"success": true` key followed
by all crumb object fields at the top level.

```json
{
  "success": true,
  "id": "AF-101",
  "title": "Improve error messages",
  "type": "task",
  "status": "in_progress",
  "priority": "P3",
  "description": null,
  "acceptance_criteria": null,
  "scope": null,
  "links": null,
  "notes": null,
  "created_at": "2026-03-22T18:00:00Z",
  "updated_at": "2026-03-22T18:05:00Z"
}
```

When no fields are changed the command exits 0 and returns:

```json
{
  "success": false,
  "message": "no changes"
}
```

### `crumb doctor --json`

Returns a diagnostic object. Does **not** include crumb object fields.

| Field           | Type         | Description                                              |
| --------------- | ------------ | -------------------------------------------------------- |
| `ok`            | boolean      | `true` when `error_count` is 0.                          |
| `error_count`   | integer      | Number of integrity errors found.                        |
| `warning_count` | integer      | Number of warnings found.                                |
| `errors`        | array[string]| Human-readable error descriptions.                       |
| `warnings`      | array[string]| Human-readable warning descriptions.                     |
| `fixes_applied` | array[string]| Descriptions of repairs made when `--fix` is passed.     |

Healthy store:

```json
{
  "ok": true,
  "error_count": 0,
  "warning_count": 0,
  "errors": [],
  "warnings": [],
  "fixes_applied": []
}
```

Store with errors (exits with code 1):

```json
{
  "ok": false,
  "error_count": 1,
  "warning_count": 0,
  "errors": ["duplicate id 'AF-5' on lines 3 and 7"],
  "warnings": [],
  "fixes_applied": []
}
```

### `crumb search <query> --json`

Returns an array of crumb objects whose `title` or `description` contains the
query string (case-insensitive). Empty array when nothing matches.

```json
[
  {
    "id": "AF-55",
    "title": "Add search index",
    "type": "feature",
    "status": "open",
    "priority": "P2",
    "description": "Build a simple search index over tasks.jsonl.",
    "acceptance_criteria": null,
    "scope": null,
    "links": null,
    "notes": null,
    "created_at": "2026-03-18T09:00:00Z",
    "updated_at": null
  }
]
```

---

## Notes on Null vs Missing

The `_crumb_to_json_obj` serializer guarantees that all ten required fields are
always present as explicit keys. A field that was never set on the crumb record
appears as `null`, not as an absent key. Consumer code may therefore use direct
key access (e.g. `obj["description"]`) rather than `.get()` for the required
fields.

Optional fields such as `created_at`, `updated_at`, and `agent_type` are
included only when present on the stored record.
