#!/usr/bin/env node
'use strict';

/**
 * ant-farm-statusline.js — Claude Code statusLine hook for ant-farm.
 *
 * Claude Code invokes this script for every statusLine event. It receives a
 * JSON blob on stdin describing the current workspace and session, then writes
 * a one-line status string to stdout.
 *
 * Output format (when session state is available):
 *   ant-farm: step N/M | K crumbs open | wave W
 *
 * Silent no-op conditions (produces no stdout output):
 *   - No active ant-farm session (no .crumbs/sessions/ directory)
 *   - progress.log absent, empty, or contains only malformed lines
 *   - Partial/truncated last line in progress.log
 *   - `crumb` binary not on PATH
 *   - Any unexpected runtime error
 *
 * Debug logging:
 *   Set ANT_FARM_DEBUG=1 to write errors to ~/.claude/.ant-farm-hook-debug.log.
 *   When unset, all errors are silently swallowed.
 *
 * Usage (Claude Code settings.json):
 *   "statusLine": { "type": "command", "command": "node /path/to/ant-farm-statusline.js" }
 *
 * Exports:
 *   handler(input)        — async function that accepts the parsed JSON input object
 *                           and returns the status string (or empty string for silent).
 *                           Used by tests to exercise the logic without spawning a process.
 *   writeCtxMetrics(sessionDir, metrics) — writes ctx-metrics.json atomically to
 *                           SESSION_DIR. Used by tests to exercise metrics write in isolation.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { debugLog } = require('./lib/debug-log');
const { readProgressLog } = require('./lib/progress-reader');

const HOOK_NAME = 'ant-farm-statusline';

/**
 * Finds the most recently modified progress.log within the project's
 * .crumbs/sessions/ directory tree. Returns the absolute path if found,
 * or null if the directory does not exist or contains no progress.log files.
 *
 * Uses synchronous fs calls — appropriate for a short-lived hook process.
 *
 * @param {string} projectDir  Absolute path to the project root directory.
 * @returns {string|null}
 */
function findLatestProgressLog(projectDir) {
  const sessionsDir = path.join(projectDir, '.crumbs', 'sessions');

  let sessionEntries;
  try {
    sessionEntries = fs.readdirSync(sessionsDir, { withFileTypes: true });
  } catch (_err) {
    return null;
  }

  let latestMtime = -1;
  let latestPath = null;

  for (const entry of sessionEntries) {
    if (!entry.isDirectory()) {
      continue;
    }
    const candidatePath = path.join(sessionsDir, entry.name, 'progress.log');
    try {
      const stat = fs.statSync(candidatePath);
      if (stat.mtimeMs > latestMtime) {
        latestMtime = stat.mtimeMs;
        latestPath = candidatePath;
      }
    } catch (_err) {
      // File does not exist or is not accessible — skip.
    }
  }

  return latestPath;
}

/**
 * Counts the number of open crumbs by running `crumb list --open --short`.
 * Returns 0 if `crumb` is not available, returns an error, or produces no output.
 *
 * Intentionally uses execSync with a short timeout. The statusline hook is
 * invoked frequently; a hung crumb process must not block the UI.
 *
 * @returns {number}
 */
function countOpenCrumbs() {
  try {
    const output = execSync('crumb list --open --short', {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
      timeout: 3000,
    });
    if (!output || output.trim() === '') {
      return 0;
    }
    const lines = output.trim().split('\n').filter((l) => l.trim() !== '');
    return lines.length;
  } catch (_err) {
    return 0;
  }
}

/**
 * Context metrics written to SESSION_DIR/ctx-metrics.json on every statusLine event.
 *
 * @typedef {Object} CtxMetrics
 * @property {number} percentage_remaining  Context window percentage remaining (0–100).
 * @property {string} timestamp             ISO 8601 timestamp of this write.
 * @property {number} tool_use_count        Number of tool calls in this session (0 if unavailable).
 */

/**
 * Writes context usage metrics to `{sessionDir}/ctx-metrics.json` atomically
 * using a tmp-file + rename strategy.
 *
 * If the write fails for any reason the error is debug-logged and silently
 * swallowed — metrics writes must never affect the statusLine output.
 *
 * @param {string}     sessionDir  Absolute path to the active session directory.
 * @param {CtxMetrics} metrics     Metrics object to serialise as JSON.
 * @returns {void}
 */
function writeCtxMetrics(sessionDir, metrics) {
  const dest = path.join(sessionDir, 'ctx-metrics.json');
  const tmp = dest + '.tmp';
  try {
    const json = JSON.stringify(metrics);
    fs.writeFileSync(tmp, json, 'utf8');
    fs.renameSync(tmp, dest);
    debugLog(HOOK_NAME, 'wrote ctx-metrics.json', dest);
  } catch (err) {
    debugLog(HOOK_NAME, 'ctx-metrics write failed', err && err.message);
    // Silent no-op — metrics write failure must never surface to Claude Code.
  }
}

/**
 * Extracts a numeric context metric from the statusLine input payload.
 * Returns `fallback` when the value is absent, null, or NaN.
 *
 * @param {unknown} value     Raw value from the input payload.
 * @param {number}  fallback  Default when value is unavailable.
 * @returns {number}
 */
function extractNumericMetric(value, fallback) {
  if (value === null || value === undefined) {
    return fallback;
  }
  const n = Number(value);
  return isNaN(n) ? fallback : n;
}

/**
 * Core handler: accepts the parsed JSON event object from Claude Code's
 * statusLine event, reads session state, and returns the status string.
 *
 * Side effect: writes ctx-metrics.json to SESSION_DIR when a session is active.
 * Returns an empty string for any silent no-op condition.
 *
 * @param {object} input  Parsed JSON from Claude Code's statusLine stdin.
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

    const progressLogPath = findLatestProgressLog(projectDir);
    if (!progressLogPath) {
      debugLog(HOOK_NAME, 'no progress.log found under', path.join(projectDir, '.crumbs/sessions/'));
      return '';
    }

    debugLog(HOOK_NAME, 'reading progress.log', progressLogPath);

    const state = readProgressLog(progressLogPath);
    if (!state) {
      debugLog(HOOK_NAME, 'progress.log parse returned null (absent, empty, or malformed)');
      return '';
    }

    debugLog(HOOK_NAME, 'parsed state', state);

    // Derive SESSION_DIR from the progress.log path (progress.log lives directly
    // inside SESSION_DIR — its parent is always the session directory).
    const sessionDir = path.dirname(progressLogPath);

    // Extract context metrics from the statusLine input payload.
    // Claude Code provides context_window.remaining_percentage directly; fall back
    // to computing 100 - used_percentage when the field is absent (older versions).
    const ctxWindow = (input && input.context_window) || {};
    const usedPct = extractNumericMetric(ctxWindow.used_percentage, 0);
    const remainingPct = extractNumericMetric(
      ctxWindow.remaining_percentage,
      Math.max(0, 100 - usedPct)
    );
    const toolUseCount = extractNumericMetric(
      input && input.session && input.session.tool_use_count,
      0
    );

    writeCtxMetrics(sessionDir, {
      percentage_remaining: Math.min(100, Math.max(0, remainingPct)),
      timestamp: new Date().toISOString(),
      tool_use_count: toolUseCount,
    });

    const openCount = countOpenCrumbs();

    debugLog(HOOK_NAME, 'openCount', openCount);

    const waveStr = state.wave > 0 ? `wave ${state.wave}` : 'wave -';
    return `ant-farm: step ${state.step}/${state.total} | ${openCount} crumbs open | ${waveStr}`;
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

module.exports = { handler, writeCtxMetrics };
