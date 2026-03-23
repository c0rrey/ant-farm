'use strict';

/**
 * progress-reader.test.js — Tests for progress-reader.js
 *
 * Tests cover:
 *   getExpectedNextStep — returns null when progress.log absent
 *   getExpectedNextStep — returns null when progress.log is empty
 *   getExpectedNextStep — returns null when no next_step= field in any line
 *   getExpectedNextStep — returns last next_step= value from a single line
 *   getExpectedNextStep — returns last next_step= value when multiple lines have next_step=
 *   getExpectedNextStep — ignores lines where next_step= value is empty string
 *   getExpectedNextStep — handles extra whitespace around field values
 *   getExpectedNextStep — returns null when progress.log has only unrecognised event types and no next_step=
 *   getExpectedNextStep — handles lines with next_step= at different field positions
 *   readAllLines — returns empty array for absent file
 *   readAllLines — returns empty array for empty file
 *   readAllLines — filters out empty lines
 *   readAllLines — handles file not ending with newline
 *   readProgressLog — returns null for absent file (regression guard)
 *   readProgressLog — returns SessionState for valid last line (regression guard)
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  getExpectedNextStep,
  readAllLines,
  readProgressLog,
  EVENT_STEP_MAP,
  TOTAL_STEPS,
} = require('../progress-reader');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Creates a temporary session directory containing a progress.log with the given content.
 * Returns the session directory path.
 *
 * @param {string|null} content  File content, or null to skip creating the file.
 * @returns {string}  Absolute path to the temp session directory.
 */
function makeSession(content) {
  const sessionDir = fs.mkdtempSync(path.join(os.tmpdir(), 'progress-reader-test-'));
  if (content !== null) {
    fs.writeFileSync(path.join(sessionDir, 'progress.log'), content, 'utf8');
  }
  return sessionDir;
}

/**
 * Removes a temp directory created by makeSession.
 *
 * @param {string} sessionDir
 */
function cleanup(sessionDir) {
  fs.rmSync(sessionDir, { recursive: true, force: true });
}

// ===========================================================================
// getExpectedNextStep
// ===========================================================================

test('getExpectedNextStep: returns null when progress.log is absent', () => {
  const sessionDir = makeSession(null);
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, null, 'Should return null when progress.log does not exist');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: returns null when progress.log is empty', () => {
  const sessionDir = makeSession('');
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, null, 'Should return null for empty progress.log');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: returns null when no line contains next_step=', () => {
  const content = [
    '2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0',
    '2026-01-01T00:01:00.000Z|SCOUT_COMPLETE|wave=0',
  ].join('\n') + '\n';
  const sessionDir = makeSession(content);
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, null, 'Should return null when no next_step= field exists');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: returns value from a single line with next_step=', () => {
  const content = [
    '2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0|next_step=pre-spawn-check',
  ].join('\n') + '\n';
  const sessionDir = makeSession(content);
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, 'pre-spawn-check', 'Should return the next_step= value');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: returns last next_step= when multiple lines have one', () => {
  const content = [
    '2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0|next_step=pre-spawn-check',
    '2026-01-01T00:01:00.000Z|SCOUT_COMPLETE|wave=0|next_step=scope-verify',
    '2026-01-01T00:02:00.000Z|WAVE_SPAWNED|wave=1',
  ].join('\n') + '\n';
  const sessionDir = makeSession(content);
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, 'scope-verify', 'Should return the LAST next_step= value across all lines');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: ignores next_step= when its value is empty', () => {
  const content = [
    '2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0|next_step=startup-check',
    '2026-01-01T00:01:00.000Z|SCOUT_COMPLETE|wave=0|next_step=',
  ].join('\n') + '\n';
  const sessionDir = makeSession(content);
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, 'startup-check', 'Empty next_step= should be ignored; earlier value returned');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: handles next_step= at different field positions', () => {
  const content = [
    '2026-01-01T00:00:00.000Z|WAVE_SPAWNED|wave=2|task_count=5|next_step=scope-verify',
  ].join('\n') + '\n';
  const sessionDir = makeSession(content);
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, 'scope-verify', 'Should find next_step= regardless of its field position');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: handles whitespace around KV fields', () => {
  const content = [
    '2026-01-01T00:00:00.000Z|SESSION_INIT| next_step=review-integrity ',
  ].join('\n') + '\n';
  const sessionDir = makeSession(content);
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, 'review-integrity', 'Should trim field key and extract value after next_step=');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: returns null for file with only blank lines', () => {
  const sessionDir = makeSession('\n\n\n');
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, null, 'Should return null for file with only blank lines');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: returns null for file without next_step= in mixed content', () => {
  const content = [
    '2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0',
    '2026-01-01T00:01:00.000Z|WAVE_SPAWNED|wave=1|task_count=3',
    '2026-01-01T00:02:00.000Z|WAVE_VERIFIED|wave=1',
  ].join('\n') + '\n';
  const sessionDir = makeSession(content);
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, null, 'Should return null when no line has next_step=');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: handles file not ending with newline', () => {
  // Write without trailing newline to simulate partial write.
  const sessionDir = makeSession(null);
  try {
    const logPath = path.join(sessionDir, 'progress.log');
    fs.writeFileSync(logPath, '2026-01-01T00:00:00.000Z|SESSION_INIT|next_step=startup-check', 'utf8');
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, 'startup-check', 'Should handle file not ending with newline');
  } finally {
    cleanup(sessionDir);
  }
});

test('getExpectedNextStep: last occurrence wins when same-step values differ', () => {
  const content = [
    '2026-01-01T00:00:00.000Z|SESSION_INIT|next_step=pre-spawn-check',
    '2026-01-01T00:01:00.000Z|SCOUT_COMPLETE|next_step=scope-verify',
    '2026-01-01T00:02:00.000Z|REVIEW_COMPLETE|next_step=session-complete',
  ].join('\n') + '\n';
  const sessionDir = makeSession(content);
  try {
    const result = getExpectedNextStep(sessionDir);
    assert.equal(result, 'session-complete', 'Last line wins when multiple next_step= values exist');
  } finally {
    cleanup(sessionDir);
  }
});

// ===========================================================================
// readAllLines
// ===========================================================================

test('readAllLines: returns empty array for absent file', () => {
  const sessionDir = makeSession(null);
  try {
    const filePath = path.join(sessionDir, 'progress.log');
    const result = readAllLines(filePath);
    assert.deepEqual(result, [], 'Should return empty array for missing file');
  } finally {
    cleanup(sessionDir);
  }
});

test('readAllLines: returns empty array for empty file', () => {
  const sessionDir = makeSession('');
  try {
    const filePath = path.join(sessionDir, 'progress.log');
    const result = readAllLines(filePath);
    assert.deepEqual(result, [], 'Should return empty array for empty file');
  } finally {
    cleanup(sessionDir);
  }
});

test('readAllLines: filters out empty and blank lines', () => {
  const sessionDir = makeSession('line one\n\nline two\n   \nline three\n');
  try {
    const filePath = path.join(sessionDir, 'progress.log');
    const result = readAllLines(filePath);
    assert.equal(result.length, 3, 'Should have 3 non-empty lines');
    assert.equal(result[0], 'line one');
    assert.equal(result[1], 'line two');
    assert.equal(result[2], 'line three');
  } finally {
    cleanup(sessionDir);
  }
});

test('readAllLines: handles file without trailing newline', () => {
  const sessionDir = makeSession(null);
  try {
    const filePath = path.join(sessionDir, 'progress.log');
    fs.writeFileSync(filePath, 'line one\nline two', 'utf8');
    const result = readAllLines(filePath);
    assert.equal(result.length, 2, 'Should return both lines even without trailing newline');
  } finally {
    cleanup(sessionDir);
  }
});

// ===========================================================================
// readProgressLog — regression guards
// ===========================================================================

test('readProgressLog: returns null for absent progress.log', () => {
  const sessionDir = makeSession(null);
  try {
    const filePath = path.join(sessionDir, 'progress.log');
    const result = readProgressLog(filePath);
    assert.equal(result, null, 'Regression: readProgressLog must return null for missing file');
  } finally {
    cleanup(sessionDir);
  }
});

test('readProgressLog: returns SessionState for valid last line', () => {
  const content = '2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0\n';
  const sessionDir = makeSession(content);
  try {
    const filePath = path.join(sessionDir, 'progress.log');
    const result = readProgressLog(filePath);
    assert.ok(result !== null, 'Regression: readProgressLog must return non-null for valid line');
    assert.equal(result.step, EVENT_STEP_MAP.SESSION_INIT);
    assert.equal(result.total, TOTAL_STEPS);
    assert.equal(result.wave, 0);
  } finally {
    cleanup(sessionDir);
  }
});

test('readProgressLog: extracts wave number from valid line', () => {
  const content = '2026-01-01T00:00:00.000Z|WAVE_SPAWNED|wave=3\n';
  const sessionDir = makeSession(content);
  try {
    const filePath = path.join(sessionDir, 'progress.log');
    const result = readProgressLog(filePath);
    assert.ok(result !== null, 'Should return non-null for WAVE_SPAWNED line');
    assert.equal(result.wave, 3, 'Should extract wave=3');
    assert.equal(result.step, EVENT_STEP_MAP.WAVE_SPAWNED);
  } finally {
    cleanup(sessionDir);
  }
});
