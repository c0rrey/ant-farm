'use strict';

/**
 * wave-tracker.js — Per-wave agent result tracking for ant-farm sessions.
 *
 * Records per-agent success/failure results for each orchestration wave.
 * Results are stored in a per-wave JSON file inside the session directory:
 *   <sessionDir>/wave-<N>-results.json
 *
 * Each file contains a JSON array of result entries:
 *   [
 *     { "wave": N, "agent_id": "...", "status": "success"|"failure", "timestamp": "..." },
 *     ...
 *   ]
 *
 * Files are written atomically via tmp-file + rename (same pattern as gate-manager.js
 * and retry-tracker.js) to avoid partial reads under concurrent hook processes.
 *
 * Public API:
 *   recordAgentResult(sessionDir, waveNum, agentId, status) — record a result entry
 *   getWaveStatus(sessionDir, waveNum)  — return { total, succeeded, failed, failureRate }
 *   WAVE_RESULTS_FILENAME(waveNum)      — returns the per-wave filename (for tests)
 *
 * No external dependencies. Uses synchronous fs operations (consistent with all
 * other hook libraries in this project).
 */

const fs = require('fs');
const path = require('path');

const { debugLog } = require('./debug-log');

/** Hook name used in debug log entries. */
const HOOK_NAME = 'wave-tracker';

/** Valid status values for agent results. */
const VALID_STATUSES = new Set(['success', 'failure']);

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Returns the filename for the per-wave results file.
 *
 * @param {number} waveNum  1-based wave number.
 * @returns {string}  e.g. 'wave-1-results.json'
 */
function WAVE_RESULTS_FILENAME(waveNum) {
  return `wave-${waveNum}-results.json`;
}

/**
 * Returns the absolute path to the per-wave results file inside the session directory.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @param {number} waveNum     1-based wave number.
 * @returns {string}
 */
function _waveFilePath(sessionDir, waveNum) {
  return path.join(sessionDir, WAVE_RESULTS_FILENAME(waveNum));
}

/**
 * Reads and parses the per-wave results file.
 * Returns an empty array when the file does not exist or cannot be parsed.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @param {number} waveNum     1-based wave number.
 * @returns {Array<WaveResultEntry>}
 */
function _readWaveResults(sessionDir, waveNum) {
  const filePath = _waveFilePath(sessionDir, waveNum);
  try {
    const raw = fs.readFileSync(filePath, 'utf8');
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      debugLog(HOOK_NAME, `wave-${waveNum}-results.json contained non-array; resetting to []`, { filePath });
      return [];
    }
    return parsed;
  } catch (err) {
    if (err.code !== 'ENOENT') {
      debugLog(HOOK_NAME, `failed to read wave-${waveNum}-results.json; resetting to []`, { error: err.message });
    }
    return [];
  }
}

/**
 * Atomically writes the results array to the per-wave file via tmp-then-rename.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @param {number} waveNum     1-based wave number.
 * @param {Array<WaveResultEntry>} results  Array of result entries to persist.
 * @returns {void}
 */
function _writeWaveResults(sessionDir, waveNum, results) {
  const filePath = _waveFilePath(sessionDir, waveNum);
  const tmpPath = filePath + '.tmp';
  const content = JSON.stringify(results, null, 2) + '\n';
  try {
    fs.writeFileSync(tmpPath, content, 'utf8');
    fs.renameSync(tmpPath, filePath);
  } catch (err) {
    // Clean up orphaned tmp file if rename failed.
    try {
      fs.unlinkSync(tmpPath);
    } catch (_cleanupErr) {
      // Best-effort cleanup only.
    }
    debugLog(HOOK_NAME, `writeWaveResults failed for wave ${waveNum}`, { error: err.message });
    throw err;
  }
}

// ---------------------------------------------------------------------------
// Types (JSDoc only)
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} WaveResultEntry
 * @property {number} wave        The wave number this result belongs to.
 * @property {string} agent_id    Identifier for the agent that ran.
 * @property {'success'|'failure'} status  Result of the agent run.
 * @property {string} timestamp   ISO 8601 timestamp of when the result was recorded.
 */

/**
 * @typedef {Object} WaveStatus
 * @property {number} total        Total number of agents recorded for this wave.
 * @property {number} succeeded    Number of agents that reported 'success'.
 * @property {number} failed       Number of agents that reported 'failure'.
 * @property {number} failureRate  Fraction of agents that failed (0..1). 0 when total is 0.
 */

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Records an agent result for the given wave.
 *
 * Appends a single entry to the per-wave results file. Creates the file on first
 * write. Uses atomic tmp+rename to avoid partial reads under concurrent writes.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @param {number} waveNum     1-based wave number.
 * @param {string} agentId     Identifier for the agent (e.g. task ID or arbitrary label).
 * @param {'success'|'failure'} status  Result to record.
 * @returns {WaveResultEntry}  The entry that was written.
 * @throws {Error}  When status is not 'success' or 'failure'.
 */
function recordAgentResult(sessionDir, waveNum, agentId, status) {
  if (!VALID_STATUSES.has(status)) {
    throw new Error(`wave-tracker: invalid status "${status}" — must be "success" or "failure"`);
  }

  const results = _readWaveResults(sessionDir, waveNum);

  /** @type {WaveResultEntry} */
  const entry = {
    wave: waveNum,
    agent_id: agentId,
    status,
    timestamp: new Date().toISOString(),
  };

  results.push(entry);
  _writeWaveResults(sessionDir, waveNum, results);

  debugLog(HOOK_NAME, 'recorded agent result', {
    wave: waveNum,
    agent_id: agentId,
    status,
    total: results.length,
  });

  return entry;
}

/**
 * Returns aggregate status for all agent results recorded in the given wave.
 *
 * Returns zeroed-out counts when no results file exists (wave not yet started
 * or results not yet recorded).
 *
 * failureRate is defined as `failed / total`. Returns 0 when total is 0 to
 * avoid divide-by-zero; a wave with no results is not considered failed.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @param {number} waveNum     1-based wave number.
 * @returns {WaveStatus}
 */
function getWaveStatus(sessionDir, waveNum) {
  const results = _readWaveResults(sessionDir, waveNum);

  const total = results.length;
  const succeeded = results.filter((e) => e.status === 'success').length;
  const failed = results.filter((e) => e.status === 'failure').length;
  const failureRate = total === 0 ? 0 : failed / total;

  debugLog(HOOK_NAME, 'getWaveStatus', { wave: waveNum, total, succeeded, failed, failureRate });

  return { total, succeeded, failed, failureRate };
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

module.exports = {
  recordAgentResult,
  getWaveStatus,
  WAVE_RESULTS_FILENAME,
};
