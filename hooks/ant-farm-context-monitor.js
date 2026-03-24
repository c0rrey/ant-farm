#!/usr/bin/env node
'use strict';

/**
 * ant-farm-context-monitor.js — Claude Code PostToolUse hook for context monitoring.
 *
 * Claude Code invokes this script for every PostToolUse event. It reads context
 * usage metrics from the bridge file written by the statusline hook and injects
 * advisory warnings when context is running low.
 *
 * Behavior:
 *   - Reads {SESSION_DIR}/ctx-metrics.json for percentage_remaining and tool_use_count.
 *   - At 35% remaining:  injects WARNING advisory (wrap up current work).
 *   - At 25% remaining:  injects CRITICAL advisory (inform user to run /ant-farm-pause).
 *   - Debounce: after a warning fires, the next 4 tool uses produce no warning.
 *   - Severity escalation (WARNING → CRITICAL) bypasses debounce.
 *   - Thresholds are configurable via .crumbs/config.json:
 *       context_warning_threshold  (default 35)
 *       context_critical_threshold (default 25)
 *   - Never returns continue: false — advisory only.
 *   - Silent no-op when no ant-farm session is active (no .crumbs/sessions/ directory).
 *
 * Response format:
 *   Silent (no output)                                          — below threshold, debounced, or no session
 *   {"continue": true, "additionalContext": "WARNING: ..."}     — at warning threshold
 *   {"continue": true, "additionalContext": "CRITICAL: ..."}    — at critical threshold
 *
 * Debounce state file: {SESSION_DIR}/ctx-debounce.json
 *   { "last_warning_tool_count": N, "last_severity": "warning"|"critical" }
 *
 * Debug logging:
 *   Set ANT_FARM_DEBUG=1 to write trace events to ~/.claude/.ant-farm-hook-debug.log.
 *
 * Usage (Claude Code settings.json):
 *   "PostToolUse": [{
 *     "type": "command",
 *     "command": "node /path/to/ant-farm-context-monitor.js"
 *   }]
 *
 * Exports:
 *   handler(input)          — async function accepting parsed JSON input, returning response string.
 *   findLatestSessionDir    — exported for testing.
 *   readCtxMetrics          — exported for testing.
 *   readDebounceState       — exported for testing.
 *   writeDebounceState      — exported for testing.
 *   DEBOUNCE_TOOL_COUNT     — number of tool uses in debounce window.
 */

const fs = require('fs');
const path = require('path');
const { debugLog } = require('./lib/debug-log');

const HOOK_NAME = 'ant-farm-context-monitor';

/** Number of tool uses to suppress repeated warnings after one fires. */
const DEBOUNCE_TOOL_COUNT = 5;

/** Filename for debounce state persistence. */
const DEBOUNCE_FILENAME = 'ctx-debounce.json';

/** Filename for context metrics bridge file (written by statusline hook). */
const CTX_METRICS_FILENAME = 'ctx-metrics.json';

/** Filename for project config. */
const CONFIG_FILENAME = 'config.json';

/** Default thresholds (percentage_remaining values). */
const DEFAULT_WARNING_THRESHOLD = 35;
const DEFAULT_CRITICAL_THRESHOLD = 25;

/**
 * Finds the most recently modified session directory within the project's
 * .crumbs/sessions/ directory tree. Returns the absolute path if found,
 * or null if the directory does not exist or contains no session directories.
 *
 * @param {string} projectDir  Absolute path to the project root directory.
 * @returns {string|null}
 */
function findLatestSessionDir(projectDir) {
  const sessionsDir = path.join(projectDir, '.crumbs', 'sessions');

  let sessionEntries;
  try {
    sessionEntries = fs.readdirSync(sessionsDir, { withFileTypes: true });
  } catch (_err) {
    return null;
  }

  let latestMtime = -1;
  let latestDir = null;

  for (const entry of sessionEntries) {
    if (!entry.isDirectory()) {
      continue;
    }
    const candidateDir = path.join(sessionsDir, entry.name);
    try {
      const stat = fs.statSync(candidateDir);
      if (stat.mtimeMs > latestMtime) {
        latestMtime = stat.mtimeMs;
        latestDir = candidateDir;
      }
    } catch (_err) {
      // Not accessible — skip.
    }
  }

  return latestDir;
}

/**
 * Reads context metrics from {sessionDir}/ctx-metrics.json.
 * Returns null if the file is absent, malformed, or has an unexpected shape.
 *
 * @param {string} sessionDir
 * @returns {{ percentage_remaining: number, tool_use_count: number, timestamp: string }|null}
 */
function readCtxMetrics(sessionDir) {
  const metricsPath = path.join(sessionDir, CTX_METRICS_FILENAME);
  try {
    const raw = fs.readFileSync(metricsPath, 'utf8');
    const parsed = JSON.parse(raw);
    if (
      parsed === null ||
      typeof parsed !== 'object' ||
      typeof parsed.percentage_remaining !== 'number'
    ) {
      return null;
    }
    return {
      percentage_remaining: parsed.percentage_remaining,
      tool_use_count: typeof parsed.tool_use_count === 'number' ? parsed.tool_use_count : 0,
      timestamp: typeof parsed.timestamp === 'string' ? parsed.timestamp : '',
    };
  } catch (_err) {
    return null;
  }
}

/**
 * Reads the debounce state from {sessionDir}/ctx-debounce.json.
 * Returns a default (no prior warning) state if the file is absent or malformed.
 *
 * @param {string} sessionDir
 * @returns {{ last_warning_tool_count: number, last_severity: string }}
 */
function readDebounceState(sessionDir) {
  const debPath = path.join(sessionDir, DEBOUNCE_FILENAME);
  try {
    const raw = fs.readFileSync(debPath, 'utf8');
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === 'object' && typeof parsed.last_warning_tool_count === 'number') {
      return {
        last_warning_tool_count: parsed.last_warning_tool_count,
        last_severity:
          typeof parsed.last_severity === 'string' ? parsed.last_severity : 'none',
      };
    }
  } catch (_err) {
    // File absent or malformed — use defaults.
  }
  return { last_warning_tool_count: -Infinity, last_severity: 'none' };
}

/**
 * Writes debounce state atomically to {sessionDir}/ctx-debounce.json.
 * Failures are debug-logged and swallowed — debounce state is best-effort.
 *
 * @param {string} sessionDir
 * @param {{ last_warning_tool_count: number, last_severity: string }} state
 * @returns {void}
 */
function writeDebounceState(sessionDir, state) {
  const dest = path.join(sessionDir, DEBOUNCE_FILENAME);
  const tmp = dest + '.tmp';
  try {
    fs.writeFileSync(tmp, JSON.stringify(state), 'utf8');
    fs.renameSync(tmp, dest);
    debugLog(HOOK_NAME, 'wrote debounce state', state);
  } catch (err) {
    debugLog(HOOK_NAME, 'debounce state write failed', err && err.message);
  }
}

/**
 * Reads context_warning_threshold and context_critical_threshold from
 * {projectDir}/.crumbs/config.json. Falls back to defaults when absent.
 *
 * @param {string} projectDir
 * @returns {{ warningThreshold: number, criticalThreshold: number }}
 */
function readThresholds(projectDir) {
  const configPath = path.join(projectDir, '.crumbs', CONFIG_FILENAME);
  try {
    const raw = fs.readFileSync(configPath, 'utf8');
    const parsed = JSON.parse(raw);
    const warningThreshold =
      typeof parsed.context_warning_threshold === 'number'
        ? parsed.context_warning_threshold
        : DEFAULT_WARNING_THRESHOLD;
    const criticalThreshold =
      typeof parsed.context_critical_threshold === 'number'
        ? parsed.context_critical_threshold
        : DEFAULT_CRITICAL_THRESHOLD;
    return { warningThreshold, criticalThreshold };
  } catch (_err) {
    return {
      warningThreshold: DEFAULT_WARNING_THRESHOLD,
      criticalThreshold: DEFAULT_CRITICAL_THRESHOLD,
    };
  }
}

/**
 * Severity ordinal for debounce bypass logic.
 * Higher value = more severe.
 *
 * @param {string} severity  'none' | 'warning' | 'critical'
 * @returns {number}
 */
function severityOrdinal(severity) {
  if (severity === 'critical') return 2;
  if (severity === 'warning') return 1;
  return 0;
}

/**
 * Core handler: reads context metrics and injects advisory context when thresholds
 * are breached. Never returns continue: false.
 *
 * Returns an empty string for any silent no-op condition.
 *
 * @param {object} input  Parsed JSON from Claude Code's PostToolUse stdin.
 * @returns {Promise<string>}
 */
async function handler(input) {
  try {
    const projectDir =
      (input &&
        input.workspace &&
        typeof input.workspace.project_dir === 'string' &&
        input.workspace.project_dir) ||
      process.cwd();

    debugLog(HOOK_NAME, 'projectDir', projectDir);

    // Locate active session directory. Silent no-op when absent.
    const sessionDir = findLatestSessionDir(projectDir);
    if (!sessionDir) {
      debugLog(HOOK_NAME, 'no session directory found — silent no-op');
      return '';
    }

    debugLog(HOOK_NAME, 'sessionDir', sessionDir);

    // Read context metrics from bridge file.
    const metrics = readCtxMetrics(sessionDir);
    if (!metrics) {
      debugLog(HOOK_NAME, 'ctx-metrics.json absent or malformed — silent no-op');
      return '';
    }

    debugLog(HOOK_NAME, 'metrics', metrics);

    const { warningThreshold, criticalThreshold } = readThresholds(projectDir);
    debugLog(HOOK_NAME, 'thresholds', { warningThreshold, criticalThreshold });

    const remaining = metrics.percentage_remaining;
    const toolCount = metrics.tool_use_count;

    // Determine current severity level.
    let currentSeverity = 'none';
    if (remaining <= criticalThreshold) {
      currentSeverity = 'critical';
    } else if (remaining <= warningThreshold) {
      currentSeverity = 'warning';
    }

    if (currentSeverity === 'none') {
      debugLog(HOOK_NAME, 'context within safe range — silent no-op', { remaining });
      return '';
    }

    debugLog(HOOK_NAME, 'severity triggered', { currentSeverity, remaining });

    // Check debounce state.
    const debounce = readDebounceState(sessionDir);
    debugLog(HOOK_NAME, 'debounce state', debounce);

    const toolsSinceLastWarning = toolCount - debounce.last_warning_tool_count;
    const isDebounced = toolsSinceLastWarning < DEBOUNCE_TOOL_COUNT;
    const isEscalation =
      severityOrdinal(currentSeverity) > severityOrdinal(debounce.last_severity);

    if (isDebounced && !isEscalation) {
      debugLog(HOOK_NAME, 'debounced — silent no-op', {
        toolsSinceLastWarning,
        debounceWindow: DEBOUNCE_TOOL_COUNT,
      });
      return '';
    }

    // Build advisory message.
    let additionalContext;
    if (currentSeverity === 'critical') {
      additionalContext =
        `CRITICAL: context window at ${remaining}% remaining (threshold: ${criticalThreshold}%). ` +
        `Inform the user they should run /ant-farm-pause to preserve progress and start a new session.`;
    } else {
      additionalContext =
        `WARNING: context window at ${remaining}% remaining (threshold: ${warningThreshold}%). ` +
        `Begin wrapping up current work and avoid starting new major tasks.`;
    }

    debugLog(HOOK_NAME, 'injecting advisory', { currentSeverity, remaining });

    // Persist debounce state before returning.
    writeDebounceState(sessionDir, {
      last_warning_tool_count: toolCount,
      last_severity: currentSeverity,
    });

    return JSON.stringify({ continue: true, additionalContext });
  } catch (err) {
    debugLog(HOOK_NAME, 'unexpected error', err && err.message);
    return '';
  }
}

/**
 * Main entrypoint: reads JSON from stdin, invokes handler(), writes result to stdout.
 * Exits with code 0 regardless of outcome — the hook must never crash Claude Code.
 */
async function main() {
  let inputText = '';
  try {
    inputText = fs.readFileSync('/dev/stdin', 'utf8');
  } catch (_err) {
    // stdin not available (e.g. during testing) — proceed with empty input.
  }

  let input = {};
  try {
    if (inputText && inputText.trim() !== '') {
      input = JSON.parse(inputText);
    }
  } catch (err) {
    debugLog(HOOK_NAME, 'failed to parse stdin JSON', err && err.message);
  }

  const result = await handler(input);
  if (result) {
    process.stdout.write(result + '\n');
  }
}

// Run main() only when this file is the direct entry point (not when required by tests).
if (require.main === module) {
  main().catch((_err) => {
    // Swallow all errors — never surface to Claude Code's error handling.
    process.exit(0);
  });
}

module.exports = {
  handler,
  findLatestSessionDir,
  readCtxMetrics,
  readDebounceState,
  writeDebounceState,
  readThresholds,
  DEBOUNCE_TOOL_COUNT,
  DEBOUNCE_FILENAME,
  CTX_METRICS_FILENAME,
};
