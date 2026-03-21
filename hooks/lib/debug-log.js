'use strict';

/**
 * debug-log.js — Shared debug logging utility for ant-farm hooks.
 *
 * Writes to ~/.claude/.ant-farm-hook-debug.log only when ANT_FARM_DEBUG=1.
 * When ANT_FARM_DEBUG is not set, all calls are silent no-ops.
 *
 * No external dependencies. Uses synchronous fs.appendFileSync so log writes
 * never delay or interfere with the hook's stdout output.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

/** Absolute path to the debug log file. */
const DEBUG_LOG_PATH = path.join(os.homedir(), '.claude', '.ant-farm-hook-debug.log');

/**
 * Returns true when ANT_FARM_DEBUG=1 is set in the environment.
 *
 * @returns {boolean}
 */
function isDebugEnabled() {
  return process.env.ANT_FARM_DEBUG === '1';
}

/**
 * Writes a debug log entry when ANT_FARM_DEBUG=1 is set.
 * Silently swallows any write errors — the log must never cause the hook to fail.
 *
 * Each line is prefixed with an ISO timestamp and the hook name for traceability.
 *
 * @param {string} hookName  Short name identifying the hook (e.g. 'ant-farm-statusline').
 * @param {string} message   Human-readable message to log.
 * @param {unknown} [extra]  Optional extra value stringified as JSON on the same line.
 * @returns {void}
 */
function debugLog(hookName, message, extra) {
  if (!isDebugEnabled()) {
    return;
  }

  try {
    const ts = new Date().toISOString();
    const extraPart = extra !== undefined ? ' ' + JSON.stringify(extra) : '';
    const line = `${ts} [${hookName}] ${message}${extraPart}\n`;
    fs.appendFileSync(DEBUG_LOG_PATH, line, 'utf8');
  } catch (_err) {
    // Intentionally silent: log write failure must never surface to stdout/stderr.
  }
}

module.exports = { debugLog, isDebugEnabled, DEBUG_LOG_PATH };
