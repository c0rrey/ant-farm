'use strict';

/**
 * retry-tracker.js — Retry event tracking for ant-farm agent sessions.
 *
 * Tracks retry events in .crumbs/sessions/<session-dir>/retries.json with
 * per-failure-type limits and a global session cap. Uses atomic tmp+rename
 * writes so concurrent hook processes never see a partial file.
 *
 * Failure-type limits:
 *   - checkpoint  : 2 retries allowed
 *   - agent_error : 1 retry allowed
 *   - stuck       : 0 retries allowed (fail immediately)
 *
 * Global cap: 5 total retries across all failure types per session.
 *
 * @module retry-tracker
 */

const fs = require('fs');
const path = require('path');

const { debugLog } = require('./debug-log');

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Filename for the retry log within the session directory. */
const RETRIES_FILE = 'retries.json';

/** Maximum retries allowed per failure type. */
const RETRY_LIMITS = Object.freeze({
  checkpoint: 2,
  agent_error: 1,
  stuck: 0,
});

/** Maximum total retries allowed across all failure types per session. */
const GLOBAL_RETRY_CAP = 5;

/** Hook name used in debug log entries. */
const HOOK_NAME = 'retry-tracker';

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Returns the absolute path to retries.json inside the given session directory.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @returns {string}
 */
function _retriesPath(sessionDir) {
  return path.join(sessionDir, RETRIES_FILE);
}

/**
 * Reads and parses retries.json from the session directory.
 * Returns an empty array when the file does not exist or cannot be parsed.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @returns {Array<RetryEntry>}
 */
function _readRetries(sessionDir) {
  const filePath = _retriesPath(sessionDir);
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      debugLog(HOOK_NAME, 'retries.json contained non-array; resetting to []', { filePath });
      return [];
    }
    return parsed;
  } catch (err) {
    if (err.code !== 'ENOENT') {
      debugLog(HOOK_NAME, 'failed to read retries.json; resetting to []', { error: err.message });
    }
    return [];
  }
}

/**
 * Atomically writes the retries array to retries.json via tmp-then-rename.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @param {Array<RetryEntry>} retries  Array of retry entries to persist.
 * @returns {void}
 */
function _writeRetries(sessionDir, retries) {
  const filePath = _retriesPath(sessionDir);
  const tmpPath = filePath + '.tmp';
  const content = JSON.stringify(retries, null, 2) + '\n';
  fs.writeFileSync(tmpPath, content, 'utf8');
  fs.renameSync(tmpPath, filePath);
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} RetryEntry
 * @property {string} timestamp      ISO 8601 timestamp of the retry event.
 * @property {string} failure_type   One of: 'checkpoint', 'agent_error', 'stuck'.
 * @property {string} task_id        Crumb ID of the failing task (e.g. 'AF-42').
 * @property {number} retry_number   1-based index of this retry for the given type+task.
 * @property {number} max_allowed    Maximum retries allowed for this failure type.
 */

/**
 * Records a retry event to retries.json in the session directory.
 *
 * The retry_number is computed as: count of existing entries with the same
 * failure_type AND task_id, plus one.
 *
 * @param {string} sessionDir    Absolute path to the session directory.
 * @param {string} failureType   Failure category ('checkpoint', 'agent_error', 'stuck').
 * @param {string} taskId        Crumb ID of the task being retried.
 * @returns {RetryEntry}  The entry that was written.
 */
function recordRetry(sessionDir, failureType, taskId) {
  const retries = _readRetries(sessionDir);

  const priorCount = retries.filter(
    (e) => e.failure_type === failureType && e.task_id === taskId
  ).length;

  const maxAllowed = Object.prototype.hasOwnProperty.call(RETRY_LIMITS, failureType)
    ? RETRY_LIMITS[failureType]
    : 0;

  /** @type {RetryEntry} */
  const entry = {
    timestamp: new Date().toISOString(),
    failure_type: failureType,
    task_id: taskId,
    retry_number: priorCount + 1,
    max_allowed: maxAllowed,
  };

  retries.push(entry);
  _writeRetries(sessionDir, retries);

  debugLog(HOOK_NAME, 'recorded retry', {
    task_id: taskId,
    failure_type: failureType,
    retry_number: entry.retry_number,
    total: retries.length,
  });

  return entry;
}

/**
 * Returns true when the task is permitted to retry for the given failure type.
 *
 * Returns false when:
 *   - The per-type retry count for this task_id already equals or exceeds the limit, OR
 *   - The total session retry count equals or exceeds GLOBAL_RETRY_CAP (5).
 *
 * @param {string} sessionDir    Absolute path to the session directory.
 * @param {string} failureType   Failure category ('checkpoint', 'agent_error', 'stuck').
 * @param {string} taskId        Crumb ID of the task to check.
 * @returns {boolean}
 */
function canRetry(sessionDir, failureType, taskId) {
  const retries = _readRetries(sessionDir);

  if (retries.length >= GLOBAL_RETRY_CAP) {
    debugLog(HOOK_NAME, 'canRetry: global cap reached', { total: retries.length });
    return false;
  }

  const maxAllowed = Object.prototype.hasOwnProperty.call(RETRY_LIMITS, failureType)
    ? RETRY_LIMITS[failureType]
    : 0;

  const typeCount = retries.filter(
    (e) => e.failure_type === failureType && e.task_id === taskId
  ).length;

  const allowed = typeCount < maxAllowed;

  debugLog(HOOK_NAME, 'canRetry', {
    task_id: taskId,
    failure_type: failureType,
    typeCount,
    maxAllowed,
    totalRetries: retries.length,
    allowed,
  });

  return allowed;
}

/**
 * Returns the total number of retry events recorded in the session.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @returns {number}
 */
function getTotalRetries(sessionDir) {
  const retries = _readRetries(sessionDir);
  return retries.length;
}

/**
 * Clears all retry events by writing an empty array to retries.json.
 * Logs the reset via debugLog.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @returns {void}
 */
function resetRetries(sessionDir) {
  _writeRetries(sessionDir, []);
  debugLog(HOOK_NAME, 'retries reset', { sessionDir });
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

module.exports = {
  recordRetry,
  canRetry,
  getTotalRetries,
  resetRetries,
  RETRY_LIMITS,
  GLOBAL_RETRY_CAP,
  RETRIES_FILE,
};
