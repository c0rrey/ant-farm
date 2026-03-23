'use strict';

/**
 * gate-manager.js — Gate status read/write utility for ant-farm hooks.
 *
 * Reads and writes gate-status.json inside a session directory. Each gate in
 * the GATE_CHAIN records a verdict ('PASS' or 'FAIL') plus a timestamp. The
 * file is written atomically via a tmp-file + rename pattern so readers never
 * see a partial write.
 *
 * gate-status.json format:
 *   {
 *     "gates": {
 *       "<gate-name>": {
 *         "verdict": "PASS" | "FAIL",
 *         "timestamp": "<ISO 8601>",
 *         ...extraFields
 *       }
 *     }
 *   }
 *
 * No external dependencies. Uses synchronous fs operations so this module
 * is safe to require in the hook hot-path without introducing async complexity.
 */

const fs = require('fs');
const path = require('path');

const { debugLog } = require('./debug-log');

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Name of the gate status manifest file inside a session directory. */
const GATE_STATUS_FILENAME = 'gate-status.json';

/**
 * Ordered gate dependency chain for the full ant-farm session lifecycle.
 *
 * Each gate must pass before the next gate's associated agent phase may begin.
 * The chain mirrors the step sequence defined in RULES.md:
 *
 *   startup-check
 *     └─ pre-spawn-check
 *          └─ [Implementers complete]
 *               └─ scope-verify
 *                    └─ claims-vs-code
 *                         └─ [Reviewers complete]
 *                              └─ review-integrity
 *                                   └─ [Session Scribe]
 *                                        └─ session-complete
 *
 * @type {string[]}
 */
const GATE_CHAIN = [
  'startup-check',
  'pre-spawn-check',
  'scope-verify',
  'claims-vs-code',
  'review-integrity',
  'session-complete',
];

// ---------------------------------------------------------------------------
// Types (JSDoc only — no runtime overhead)
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} GateEntry
 * @property {'PASS'|'FAIL'} verdict   The gate verdict.
 * @property {string}        timestamp ISO 8601 timestamp of when the verdict was written.
 */

/**
 * @typedef {Object} GateStatus
 * @property {Object.<string, GateEntry>} gates  Map of gate name to entry.
 */

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Returns the absolute path to gate-status.json for the given session directory.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @returns {string}
 */
function gateStatusPath(sessionDir) {
  return path.join(sessionDir, GATE_STATUS_FILENAME);
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Reads and parses gate-status.json from the given session directory.
 *
 * Returns null (silently) when:
 *   - The file does not exist (most common: gate not yet written)
 *   - The file contains invalid or partial JSON (e.g. TOCTOU mid-write)
 *   - The parsed value lacks a valid `gates` object
 *   - Any unexpected I/O or parse error occurs
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @returns {GateStatus|null}
 */
function readGateStatus(sessionDir) {
  const filePath = gateStatusPath(sessionDir);

  let raw;
  try {
    raw = fs.readFileSync(filePath, 'utf8');
  } catch (_err) {
    // File absent or not readable — silently inactive.
    debugLog('gate-manager', 'gate-status.json absent or unreadable', { sessionDir });
    return null;
  }

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (_err) {
    // Partial/corrupt JSON (e.g. mid-write TOCTOU) — fall back to null.
    debugLog('gate-manager', 'gate-status.json parse error', { sessionDir });
    return null;
  }

  // Validate shape: must be a plain object with a `gates` plain object.
  if (
    parsed === null ||
    typeof parsed !== 'object' ||
    Array.isArray(parsed) ||
    parsed.gates === null ||
    typeof parsed.gates !== 'object' ||
    Array.isArray(parsed.gates)
  ) {
    debugLog('gate-manager', 'gate-status.json has unexpected shape', { parsed });
    return null;
  }

  return { gates: parsed.gates };
}

/**
 * Atomically writes a gate verdict to gate-status.json in the given session
 * directory using a tmp-file + rename pattern.
 *
 * If gate-status.json already exists its existing gate entries are preserved;
 * only the named gate is added or overwritten. Any extra fields supplied in
 * `meta` are merged into the gate entry alongside the verdict and timestamp.
 *
 * The session directory must already exist. Any I/O error is re-thrown so
 * callers are aware of write failures — a missed verdict write is a real error,
 * unlike a missed debug-log write.
 *
 * @param {string}             sessionDir  Absolute path to the session directory.
 * @param {string}             gateName    Name of the gate (e.g. 'startup-check').
 * @param {'PASS'|'FAIL'}      verdict     The gate verdict to record.
 * @param {Object}             [meta={}]   Optional extra fields to include in the entry.
 * @returns {void}
 */
function writeGateVerdict(sessionDir, gateName, verdict, meta) {
  const filePath = gateStatusPath(sessionDir);

  // Read existing status (if any) so we preserve other gates' verdicts.
  const existing = readGateStatus(sessionDir);
  const gates = existing ? { ...existing.gates } : {};

  // Build the new entry.
  const entry = {
    verdict,
    timestamp: new Date().toISOString(),
    ...(meta !== null && typeof meta === 'object' && !Array.isArray(meta) ? meta : {}),
  };

  gates[gateName] = entry;

  const updated = { gates };
  const json = JSON.stringify(updated, null, 2) + '\n';

  // Write to a tmp file in the same directory, then rename for atomicity.
  // Using os.tmpdir() for the tmp file would cross filesystem boundaries on
  // some setups; keeping the tmp file in sessionDir avoids that.
  const tmpPath = path.join(sessionDir, `.gate-status.tmp.${process.pid}`);

  try {
    fs.writeFileSync(tmpPath, json, 'utf8');
    fs.renameSync(tmpPath, filePath);
  } catch (err) {
    // Clean up the orphaned tmp file if rename failed.
    try {
      fs.unlinkSync(tmpPath);
    } catch (_cleanupErr) {
      // Best-effort cleanup only.
    }
    debugLog('gate-manager', 'writeGateVerdict failed', { gateName, verdict, err: err.message });
    throw err;
  }

  debugLog('gate-manager', 'wrote gate verdict', { gateName, verdict });
}

/**
 * Returns true when the named gate has a recorded verdict of 'PASS'.
 *
 * Returns false when:
 *   - gate-status.json does not exist
 *   - The gate has no entry in the file
 *   - The gate's verdict is 'FAIL' or any other non-'PASS' value
 *   - Any parse/I/O error occurs (null from readGateStatus)
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @param {string} gateName    Name of the gate to check.
 * @returns {boolean}
 */
function isGatePassed(sessionDir, gateName) {
  const status = readGateStatus(sessionDir);
  if (status === null) {
    return false;
  }
  const entry = status.gates[gateName];
  return entry !== undefined && entry !== null && entry.verdict === 'PASS';
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------

module.exports = {
  GATE_CHAIN,
  GATE_STATUS_FILENAME,
  readGateStatus,
  writeGateVerdict,
  isGatePassed,
};
