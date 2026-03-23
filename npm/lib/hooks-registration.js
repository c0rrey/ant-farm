'use strict';

/**
 * hooks-registration.js — Claude Code settings.json hook registration for ant-farm.
 *
 * Reads ~/.claude/settings.json, merges ant-farm hook entries (statusLine and
 * PreToolUse), and writes the result back atomically. Existing non-ant-farm
 * entries are preserved unchanged.
 *
 * Hooks registered:
 *   statusLine:
 *     { "type": "command", "command": "node ~/.claude/hooks/ant-farm-statusline.js" }
 *
 *   PreToolUse (matcher "Write|Edit"):
 *     { "type": "command", "command": "node ~/.claude/hooks/ant-farm-scope-advisor.js" }
 *
 *   PreToolUse (matcher "Task|TeamCreate|SendMessage"):
 *     { "type": "command", "command": "node ~/.claude/hooks/ant-farm-gate-enforcer.js" }
 *
 * Idempotency:
 *   Each function checks whether the entry is already present (by command string)
 *   before inserting. Re-running install does not add duplicate entries.
 *
 * Atomicity:
 *   Writes to a temp file in the same directory, then renames atomically. A
 *   process crash after writeFile but before rename leaves a .tmp orphan that
 *   can be cleaned up manually — the original settings.json is never partially
 *   overwritten.
 *
 * Settings.json absence:
 *   If ~/.claude/settings.json does not exist, a minimal valid JSON object is
 *   created with only the ant-farm hook entries. All other keys are absent so
 *   Claude Code uses its defaults.
 */

const fs = require('fs/promises');
const path = require('path');
const os = require('os');

/** Absolute path to ~/.claude/settings.json */
const SETTINGS_PATH = path.join(os.homedir(), '.claude', 'settings.json');

/**
 * Command strings used to identify ant-farm hook entries.
 * These are matched against the `command` field when deduplicating.
 * Using the `~` home-dir shorthand that Claude Code expects.
 */
const STATUSLINE_COMMAND = 'node ~/.claude/hooks/ant-farm-statusline.js';
const SCOPE_ADVISOR_COMMAND = 'node ~/.claude/hooks/ant-farm-scope-advisor.js';
const GATE_ENFORCER_COMMAND = 'node ~/.claude/hooks/ant-farm-gate-enforcer.js';

/**
 * Matcher string for the PreToolUse scope advisor hook.
 * Must match Write and Edit tools (the tools that modify files).
 */
const SCOPE_ADVISOR_MATCHER = 'Write|Edit';

/**
 * Matcher string for the PreToolUse gate enforcer hook.
 * Must match Task, TeamCreate, and SendMessage tools (the tools that spawn agents).
 */
const GATE_ENFORCER_MATCHER = 'Task|TeamCreate|SendMessage';

/**
 * Reads and parses ~/.claude/settings.json.
 * Returns an empty object `{}` if the file does not exist.
 * Throws if the file exists but contains invalid JSON.
 *
 * @param {string} [settingsPath]  Override path (used in tests).
 * @returns {Promise<object>}
 */
async function readSettings(settingsPath = SETTINGS_PATH) {
  let raw;
  try {
    raw = await fs.readFile(settingsPath, 'utf8');
  } catch (err) {
    if (err.code === 'ENOENT') {
      return {};
    }
    throw new Error(`Cannot read ${settingsPath}: ${err.message}`);
  }

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    throw new Error(`${settingsPath} contains invalid JSON: ${err.message}`);
  }

  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error(`${settingsPath} must be a JSON object at the top level`);
  }

  return parsed;
}

/**
 * Writes an object to a settings file atomically by writing to a temp file
 * first, then renaming. Ensures the destination directory exists.
 *
 * @param {object} settings      Parsed settings object to serialise.
 * @param {string} [settingsPath]  Override path (used in tests).
 * @returns {Promise<void>}
 */
async function writeSettings(settings, settingsPath = SETTINGS_PATH) {
  const dir = path.dirname(settingsPath);
  await fs.mkdir(dir, { recursive: true });

  const tmpPath = settingsPath + '.ant-farm.tmp';
  const serialised = JSON.stringify(settings, null, 2) + '\n';

  await fs.writeFile(tmpPath, serialised, 'utf8');
  await fs.rename(tmpPath, settingsPath);
}

/**
 * Registers the ant-farm statusLine hook in the given settings object.
 *
 * The statusLine field is a single object (not an array). If the field already
 * exists with a different command, the existing command is preserved and
 * ant-farm's command is not injected — the user's custom statusLine takes
 * precedence and a warning is returned.
 *
 * If the field already contains the ant-farm command (idempotent re-install),
 * the settings object is returned unchanged.
 *
 * @param {object} settings  Mutable parsed settings object.
 * @returns {{ changed: boolean, warning: string|null }}
 */
function registerStatusLineHook(settings) {
  const entry = { type: 'command', command: STATUSLINE_COMMAND };

  // Already registered — idempotent.
  if (
    settings.statusLine &&
    typeof settings.statusLine === 'object' &&
    settings.statusLine.command === STATUSLINE_COMMAND
  ) {
    return { changed: false, warning: null };
  }

  // Another statusLine is already configured — warn but don't overwrite.
  if (settings.statusLine && typeof settings.statusLine === 'object') {
    return {
      changed: false,
      warning:
        `A statusLine hook is already configured (command: "${settings.statusLine.command}"). ` +
        `ant-farm statusline hook was NOT registered. To enable it, manually add:\n` +
        `  "statusLine": { "type": "command", "command": "${STATUSLINE_COMMAND}" }\n` +
        `to ~/.claude/settings.json.`,
    };
  }

  settings.statusLine = entry;
  return { changed: true, warning: null };
}

/**
 * Registers the ant-farm PreToolUse scope advisor hook in the given settings object.
 *
 * The PreToolUse field is an array of `{ matcher, hooks: [...] }` group objects.
 * ant-farm's entry is appended as a new group if it is not already present.
 * Detection is by exact command string — if an existing group's hooks array
 * already contains the ant-farm command, no duplicate is added.
 *
 * @param {object} settings  Mutable parsed settings object.
 * @returns {{ changed: boolean }}
 */
function registerScopeAdvisorHook(settings) {
  // Ensure hooks and PreToolUse array exist.
  if (!settings.hooks || typeof settings.hooks !== 'object') {
    settings.hooks = {};
  }
  if (!Array.isArray(settings.hooks.PreToolUse)) {
    settings.hooks.PreToolUse = [];
  }

  const preToolUse = settings.hooks.PreToolUse;

  // Check whether the ant-farm command is already present in any existing group.
  const alreadyPresent = preToolUse.some(
    (group) =>
      Array.isArray(group.hooks) &&
      group.hooks.some(
        (h) => typeof h === 'object' && h.command === SCOPE_ADVISOR_COMMAND
      )
  );

  if (alreadyPresent) {
    return { changed: false };
  }

  // Append ant-farm's PreToolUse entry as a new group.
  preToolUse.push({
    matcher: SCOPE_ADVISOR_MATCHER,
    hooks: [{ type: 'command', command: SCOPE_ADVISOR_COMMAND }],
  });

  return { changed: true };
}

/**
 * Registers the ant-farm PreToolUse gate enforcer hook in the given settings object.
 *
 * The PreToolUse field is an array of `{ matcher, hooks: [...] }` group objects.
 * ant-farm's entry is appended as a new group if it is not already present.
 * Detection is by exact command string — if an existing group's hooks array
 * already contains the ant-farm command, no duplicate is added.
 *
 * @param {object} settings  Mutable parsed settings object.
 * @returns {{ changed: boolean }}
 */
function registerGateEnforcerHook(settings) {
  // Ensure hooks and PreToolUse array exist.
  if (!settings.hooks || typeof settings.hooks !== 'object') {
    settings.hooks = {};
  }
  if (!Array.isArray(settings.hooks.PreToolUse)) {
    settings.hooks.PreToolUse = [];
  }

  const preToolUse = settings.hooks.PreToolUse;

  // Check whether the ant-farm gate enforcer command is already present in any group.
  const alreadyPresent = preToolUse.some(
    (group) =>
      Array.isArray(group.hooks) &&
      group.hooks.some(
        (h) => typeof h === 'object' && h.command === GATE_ENFORCER_COMMAND
      )
  );

  if (alreadyPresent) {
    return { changed: false };
  }

  // Append ant-farm's gate enforcer PreToolUse entry as a new group.
  preToolUse.push({
    matcher: GATE_ENFORCER_MATCHER,
    hooks: [{ type: 'command', command: GATE_ENFORCER_COMMAND }],
  });

  return { changed: true };
}

/**
 * Removes the ant-farm statusLine hook from the given settings object.
 * Only removes if the current command matches the ant-farm command exactly.
 * A user's custom statusLine is never touched.
 *
 * @param {object} settings  Mutable parsed settings object.
 * @returns {{ changed: boolean }}
 */
function unregisterStatusLineHook(settings) {
  if (
    settings.statusLine &&
    typeof settings.statusLine === 'object' &&
    settings.statusLine.command === STATUSLINE_COMMAND
  ) {
    delete settings.statusLine;
    return { changed: true };
  }
  return { changed: false };
}

/**
 * Removes all ant-farm scope advisor PreToolUse hook entries from the given settings object.
 *
 * Iterates all groups in hooks.PreToolUse, strips the ant-farm command from
 * each group's hooks array, and prunes empty groups (groups with zero hooks
 * remaining after removal). Preserves all non-ant-farm entries.
 *
 * @param {object} settings  Mutable parsed settings object.
 * @returns {{ changed: boolean }}
 */
function unregisterScopeAdvisorHook(settings) {
  if (
    !settings.hooks ||
    !Array.isArray(settings.hooks.PreToolUse) ||
    settings.hooks.PreToolUse.length === 0
  ) {
    return { changed: false };
  }

  let changed = false;

  settings.hooks.PreToolUse = settings.hooks.PreToolUse
    .map((group) => {
      if (!Array.isArray(group.hooks)) {
        return group;
      }
      const filtered = group.hooks.filter(
        (h) => !(typeof h === 'object' && h.command === SCOPE_ADVISOR_COMMAND)
      );
      if (filtered.length !== group.hooks.length) {
        changed = true;
        return { ...group, hooks: filtered };
      }
      return group;
    })
    // Prune groups whose hooks array is now empty.
    .filter((group) => !Array.isArray(group.hooks) || group.hooks.length > 0);

  return { changed };
}

/**
 * Removes all ant-farm gate enforcer PreToolUse hook entries from the given settings object.
 *
 * Iterates all groups in hooks.PreToolUse, strips the ant-farm gate enforcer command
 * from each group's hooks array, and prunes empty groups. Preserves all non-ant-farm entries.
 *
 * @param {object} settings  Mutable parsed settings object.
 * @returns {{ changed: boolean }}
 */
function unregisterGateEnforcerHook(settings) {
  if (
    !settings.hooks ||
    !Array.isArray(settings.hooks.PreToolUse) ||
    settings.hooks.PreToolUse.length === 0
  ) {
    return { changed: false };
  }

  let changed = false;

  settings.hooks.PreToolUse = settings.hooks.PreToolUse
    .map((group) => {
      if (!Array.isArray(group.hooks)) {
        return group;
      }
      const filtered = group.hooks.filter(
        (h) => !(typeof h === 'object' && h.command === GATE_ENFORCER_COMMAND)
      );
      if (filtered.length !== group.hooks.length) {
        changed = true;
        return { ...group, hooks: filtered };
      }
      return group;
    })
    // Prune groups whose hooks array is now empty.
    .filter((group) => !Array.isArray(group.hooks) || group.hooks.length > 0);

  return { changed };
}

/**
 * Registers all ant-farm hooks (statusLine + PreToolUse scope advisor + gate enforcer)
 * in Claude Code's settings.json.
 *
 * Reads the current settings, applies all registrations, and writes back
 * only if at least one change was made. Idempotent on re-install.
 *
 * @param {object} [options]
 * @param {boolean} [options.dryRun=false]   If true, no files are written.
 * @param {object|null} [options.collector]  DryRunCollector instance.
 * @param {string} [options.settingsPath]    Override settings path (used in tests).
 * @returns {Promise<{ warnings: string[] }>}
 */
async function registerHooks({ dryRun = false, collector = null, settingsPath = SETTINGS_PATH } = {}) {
  const settings = await readSettings(settingsPath);
  const warnings = [];

  const { changed: slChanged, warning: slWarning } = registerStatusLineHook(settings);
  if (slWarning) {
    warnings.push(slWarning);
  }

  const { changed: saChanged } = registerScopeAdvisorHook(settings);
  const { changed: geChanged } = registerGateEnforcerHook(settings);

  const anyChanged = slChanged || saChanged || geChanged;

  if (dryRun) {
    if (collector) {
      collector.add('update', null, settingsPath);
    }
    return { warnings };
  }

  if (anyChanged) {
    await writeSettings(settings, settingsPath);
  }

  return { warnings };
}

/**
 * Removes all ant-farm hooks from Claude Code's settings.json.
 *
 * Reads the current settings, removes entries whose command strings match the
 * ant-farm commands, and writes back only if at least one entry was removed.
 *
 * @param {object} [options]
 * @param {boolean} [options.dryRun=false]   If true, no files are written.
 * @param {object|null} [options.collector]  DryRunCollector instance.
 * @param {string} [options.settingsPath]    Override settings path (used in tests).
 * @returns {Promise<{ warnings: string[] }>}
 */
async function unregisterHooks({ dryRun = false, collector = null, settingsPath = SETTINGS_PATH } = {}) {
  // readSettings returns {} when the file is absent — safe to call unconditionally.
  const settings = await readSettings(settingsPath);

  const { changed: slChanged } = unregisterStatusLineHook(settings);
  const { changed: saChanged } = unregisterScopeAdvisorHook(settings);
  const { changed: geChanged } = unregisterGateEnforcerHook(settings);

  const anyChanged = slChanged || saChanged || geChanged;

  if (dryRun) {
    if (collector && anyChanged) {
      collector.add('update', null, settingsPath);
    }
    return { warnings: [] };
  }

  if (anyChanged) {
    await writeSettings(settings, settingsPath);
  }

  return { warnings: [] };
}

module.exports = {
  readSettings,
  writeSettings,
  registerStatusLineHook,
  registerScopeAdvisorHook,
  registerGateEnforcerHook,
  unregisterStatusLineHook,
  unregisterScopeAdvisorHook,
  unregisterGateEnforcerHook,
  registerHooks,
  unregisterHooks,
  STATUSLINE_COMMAND,
  SCOPE_ADVISOR_COMMAND,
  GATE_ENFORCER_COMMAND,
  SCOPE_ADVISOR_MATCHER,
  GATE_ENFORCER_MATCHER,
  SETTINGS_PATH,
};
