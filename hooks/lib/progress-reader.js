'use strict';

/**
 * progress-reader.js — Progress log reader and parser for ant-farm hooks.
 *
 * Reads the last non-empty line of a progress.log file and extracts session
 * state: current step label, total steps, and current wave number.
 *
 * Progress log format (pipe-delimited):
 *   TIMESTAMP|EVENT_TYPE|field=value|field=value|...
 *
 * Key EVENT_TYPEs and their step mapping:
 *   SESSION_INIT      → step 1 (session initialized)
 *   SCOUT_COMPLETE    → step 2 (recon complete)
 *   WAVE_SPAWNED      → step 3 (wave spawned)
 *   WAVE_WWD_PASS     → step 3 (wave verification in progress)
 *   WAVE_VERIFIED     → step 3 (wave verified, ready for next wave)
 *   REVIEW_COMPLETE   → step 4 (review phase)
 *   REVIEW_TRIAGED    → step 4 (review triaged)
 *   DOCS_COMMITTED    → step 5 (docs committed)
 *   XREF_VERIFIED     → step 5 (cross-reference verified)
 *   SCRIBE_COMPLETE   → step 5 (scribe done)
 *   ESV_PASS          → step 6 (exec summary verified)
 *   SESSION_COMPLETE  → step 6 (session complete)
 *
 * Returns null on any parse failure (missing file, empty, malformed line,
 * truncated/partial last line). The caller must treat null as a silent no-op.
 *
 * No external dependencies. Uses synchronous fs.readFileSync so the hook
 * never introduces async complexity in the hot path.
 */

const fs = require('fs');

/**
 * Step number mapping: event type → step number (1-based, out of TOTAL_STEPS).
 * @type {Record<string, number>}
 */
const EVENT_STEP_MAP = {
  SESSION_INIT: 1,
  SCOUT_COMPLETE: 2,
  WAVE_SPAWNED: 3,
  WAVE_WWD_PASS: 3,
  WAVE_VERIFIED: 3,
  REVIEW_COMPLETE: 4,
  REVIEW_TRIAGED: 4,
  DOCS_COMMITTED: 5,
  XREF_VERIFIED: 5,
  SCRIBE_COMPLETE: 5,
  ESV_PASS: 6,
  SESSION_COMPLETE: 6,
};

/** Total number of workflow steps displayed in the statusline. */
const TOTAL_STEPS = 6;

/**
 * Represents parsed session state extracted from progress.log.
 *
 * @typedef {Object} SessionState
 * @property {number} step   Current step number (1–TOTAL_STEPS).
 * @property {number} total  Total steps (always TOTAL_STEPS).
 * @property {number} wave   Current wave number (0 if no wave started yet).
 */

/**
 * Reads the last non-empty line from the file at `filePath` and returns it.
 * Returns null if the file cannot be read, is empty, or has no non-empty lines.
 *
 * Handles files that do not end with a newline (truncated/partial writes):
 * the last raw chunk after the final newline is treated as the last line if
 * it is non-empty and passes the validity check in the caller.
 *
 * @param {string} filePath  Absolute path to the progress log file.
 * @returns {string|null}
 */
function readLastLine(filePath) {
  let raw;
  try {
    raw = fs.readFileSync(filePath, 'utf8');
  } catch (_err) {
    return null;
  }

  if (!raw || raw.trim() === '') {
    return null;
  }

  // Split on newlines. Trailing newline produces a trailing empty string — filter it out.
  const lines = raw.split('\n').filter((l) => l.trim() !== '');
  if (lines.length === 0) {
    return null;
  }

  return lines[lines.length - 1];
}

/**
 * Parses a single pipe-delimited progress log line and extracts session state.
 *
 * A valid line must have at least 2 pipe-delimited fields:
 *   [0] TIMESTAMP  — must be non-empty
 *   [1] EVENT_TYPE — must be a recognised event type in EVENT_STEP_MAP
 *   [2..] optional key=value pairs
 *
 * Returns null if the line is malformed or the event type is unrecognised,
 * treating both as partial/truncated writes that should produce no output.
 *
 * @param {string} line  A single raw line from progress.log.
 * @returns {SessionState|null}
 */
function parseLine(line) {
  if (!line || typeof line !== 'string') {
    return null;
  }

  const fields = line.split('|');
  if (fields.length < 2) {
    return null;
  }

  const timestamp = fields[0].trim();
  const eventType = fields[1].trim();

  // Both timestamp and event type must be non-empty for the line to be valid.
  if (!timestamp || !eventType) {
    return null;
  }

  const step = EVENT_STEP_MAP[eventType];
  if (step === undefined) {
    // Unrecognised event type — treat as malformed.
    return null;
  }

  // Extract wave=N from key=value fields (fields[2] onward).
  let wave = 0;
  for (let i = 2; i < fields.length; i++) {
    const kv = fields[i].trim();
    if (kv.startsWith('wave=')) {
      const waveStr = kv.slice('wave='.length);
      const waveNum = parseInt(waveStr, 10);
      if (!isNaN(waveNum) && waveNum > 0) {
        wave = waveNum;
      }
      break;
    }
  }

  return { step, total: TOTAL_STEPS, wave };
}

/**
 * Reads and parses the progress log at `filePath`.
 * Returns a SessionState if the last non-empty line is valid, or null on any failure.
 *
 * @param {string} filePath  Absolute path to the progress log file.
 * @returns {SessionState|null}
 */
function readProgressLog(filePath) {
  const lastLine = readLastLine(filePath);
  if (lastLine === null) {
    return null;
  }
  return parseLine(lastLine);
}

module.exports = { readProgressLog, parseLine, readLastLine, EVENT_STEP_MAP, TOTAL_STEPS };
