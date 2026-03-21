'use strict';

/**
 * mcp-registration.js — Claude Code settings.json MCP server registration for ant-farm.
 *
 * Reads ~/.claude/settings.json, merges the ant-farm crumb MCP server entry under
 * the ``mcpServers`` key, and writes the result back atomically. Existing non-ant-farm
 * entries are preserved unchanged.
 *
 * MCP server registered:
 *   mcpServers.crumb:
 *     { "command": "python3", "args": ["~/.claude/mcp_server.py"] }
 *
 * Idempotency:
 *   Registration checks whether a ``mcpServers.crumb`` entry is already present
 *   (by command + args) before inserting. Re-running install does not add duplicate
 *   entries or overwrite a user-modified entry with a different command.
 *
 * Atomicity:
 *   Delegates to the same ``readSettings`` / ``writeSettings`` utilities used by
 *   hooks-registration.js, which write to a temp file then rename atomically.
 *   A process crash after writeFile but before rename leaves a .tmp orphan that
 *   can be cleaned up manually — the original settings.json is never partially
 *   overwritten.
 *
 * Settings.json absence:
 *   If ~/.claude/settings.json does not exist, a minimal valid JSON object is
 *   created with only the ant-farm MCP entry. All other keys are absent so
 *   Claude Code uses its defaults.
 */

const { readSettings, writeSettings, SETTINGS_PATH } = require('./hooks-registration');

/**
 * Server name key used under ``mcpServers`` in settings.json.
 * This is also the name Claude Code displays for the MCP server.
 */
const MCP_SERVER_NAME = 'crumb';

/**
 * Startup command for the crumb MCP server.
 * The server script is installed to ~/.claude/mcp_server.py by the file manifest.
 * The ``~`` path is expanded by the shell when Claude Code spawns the server process.
 */
const MCP_COMMAND = 'python3';
const MCP_ARGS = ['~/.claude/mcp_server.py'];

/**
 * Registers the ant-farm crumb MCP server entry in the given settings object.
 *
 * If ``mcpServers.crumb`` is already present with the expected command and args,
 * the settings object is returned unchanged (idempotent re-install).
 *
 * If ``mcpServers.crumb`` exists but has a different command (user-customised),
 * the existing entry is preserved and a warning is returned — ant-farm never
 * silently overwrites a user's custom MCP configuration.
 *
 * @param {object} settings  Mutable parsed settings object.
 * @returns {{ changed: boolean, warning: string|null }}
 */
function registerMcpServer(settings) {
  if (!settings.mcpServers || typeof settings.mcpServers !== 'object') {
    settings.mcpServers = {};
  }

  const existing = settings.mcpServers[MCP_SERVER_NAME];

  // Already registered with the correct command — idempotent.
  if (
    existing &&
    typeof existing === 'object' &&
    existing.command === MCP_COMMAND &&
    Array.isArray(existing.args) &&
    existing.args.length === MCP_ARGS.length &&
    existing.args.every((a, i) => a === MCP_ARGS[i])
  ) {
    return { changed: false, warning: null };
  }

  // An entry exists but differs — user may have customised it; warn but don't overwrite.
  if (existing && typeof existing === 'object') {
    return {
      changed: false,
      warning:
        `An mcpServers.${MCP_SERVER_NAME} entry already exists with a different command ` +
        `("${existing.command}"). The ant-farm crumb MCP server was NOT registered. ` +
        `To enable it, manually set:\n` +
        `  "mcpServers": { "${MCP_SERVER_NAME}": { "command": "${MCP_COMMAND}", "args": ${JSON.stringify(MCP_ARGS)} } }\n` +
        `in ~/.claude/settings.json.`,
    };
  }

  // No existing entry — register.
  settings.mcpServers[MCP_SERVER_NAME] = {
    command: MCP_COMMAND,
    args: MCP_ARGS,
  };

  return { changed: true, warning: null };
}

/**
 * Removes the ant-farm crumb MCP server entry from the given settings object.
 * Only removes if the current command and args exactly match the ant-farm values.
 * A user-customised entry is never touched.
 *
 * @param {object} settings  Mutable parsed settings object.
 * @returns {{ changed: boolean }}
 */
function unregisterMcpServer(settings) {
  if (
    !settings.mcpServers ||
    typeof settings.mcpServers !== 'object' ||
    !settings.mcpServers[MCP_SERVER_NAME]
  ) {
    return { changed: false };
  }

  const existing = settings.mcpServers[MCP_SERVER_NAME];

  if (
    typeof existing === 'object' &&
    existing.command === MCP_COMMAND &&
    Array.isArray(existing.args) &&
    existing.args.length === MCP_ARGS.length &&
    existing.args.every((a, i) => a === MCP_ARGS[i])
  ) {
    delete settings.mcpServers[MCP_SERVER_NAME];
    return { changed: true };
  }

  return { changed: false };
}

/**
 * Registers the ant-farm crumb MCP server in Claude Code's settings.json.
 *
 * Reads the current settings, applies the registration, and writes back only
 * if a change was made. Idempotent on re-install.
 *
 * @param {object} [options]
 * @param {boolean} [options.dryRun=false]   If true, no files are written.
 * @param {object|null} [options.collector]  DryRunCollector instance.
 * @param {string} [options.settingsPath]    Override settings path (used in tests).
 * @returns {Promise<{ warnings: string[] }>}
 */
async function registerMcp({ dryRun = false, collector = null, settingsPath = SETTINGS_PATH } = {}) {
  const settings = await readSettings(settingsPath);
  const warnings = [];

  const { changed, warning } = registerMcpServer(settings);
  if (warning) {
    warnings.push(warning);
  }

  if (dryRun) {
    if (collector) {
      collector.add('update', null, settingsPath);
    }
    return { warnings };
  }

  if (changed) {
    await writeSettings(settings, settingsPath);
  }

  return { warnings };
}

/**
 * Removes the ant-farm crumb MCP server entry from Claude Code's settings.json.
 *
 * Reads the current settings, removes the entry if its command matches the
 * ant-farm command, and writes back only if a change was made.
 *
 * @param {object} [options]
 * @param {boolean} [options.dryRun=false]   If true, no files are written.
 * @param {object|null} [options.collector]  DryRunCollector instance.
 * @param {string} [options.settingsPath]    Override settings path (used in tests).
 * @returns {Promise<{ warnings: string[] }>}
 */
async function unregisterMcp({ dryRun = false, collector = null, settingsPath = SETTINGS_PATH } = {}) {
  const settings = await readSettings(settingsPath);

  const { changed } = unregisterMcpServer(settings);

  if (dryRun) {
    if (collector && changed) {
      collector.add('update', null, settingsPath);
    }
    return { warnings: [] };
  }

  if (changed) {
    await writeSettings(settings, settingsPath);
  }

  return { warnings: [] };
}

module.exports = {
  registerMcpServer,
  unregisterMcpServer,
  registerMcp,
  unregisterMcp,
  MCP_SERVER_NAME,
  MCP_COMMAND,
  MCP_ARGS,
  SETTINGS_PATH,
};
