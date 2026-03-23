'use strict';

/**
 * retry-tracker.test.js — Tests for retry-tracker.js
 *
 * Tests cover:
 *   - recordRetry() writes correct fields to retries.json
 *   - recordRetry() increments retry_number per task+type combination
 *   - recordRetry() sets max_allowed from RETRY_LIMITS
 *   - recordRetry() uses 0 as max_allowed for unknown failure types
 *   - canRetry() returns true when below per-type limit
 *   - canRetry() returns false when per-type limit is reached
 *   - canRetry() returns false when global cap (5) is reached
 *   - canRetry() returns false immediately for 'stuck' (limit 0)
 *   - getTotalRetries() returns 0 for a fresh session directory
 *   - getTotalRetries() returns correct count after multiple records
 *   - resetRetries() clears retries.json to an empty array
 *   - resetRetries() is idempotent on a fresh directory
 *   - Atomic write: retries.json does not leave a .tmp file behind
 *   - Global cap is enforced across different failure types
 *   - Per-type limit is per task_id (different tasks count separately)
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  recordRetry,
  canRetry,
  getTotalRetries,
  resetRetries,
  RETRY_LIMITS,
  GLOBAL_RETRY_CAP,
  RETRIES_FILE,
} = require('../retry-tracker');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Creates a temporary directory to serve as a session directory.
 *
 * @returns {string} Absolute path to the temp dir.
 */
function makeTempSession() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'retry-tracker-test-'));
}

/**
 * Removes the temp directory.
 *
 * @param {string} dir
 */
function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

/**
 * Reads and parses retries.json from the session dir.
 *
 * @param {string} sessionDir
 * @returns {Array<object>}
 */
function readRetries(sessionDir) {
  const filePath = path.join(sessionDir, RETRIES_FILE);
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

// ===========================================================================
// recordRetry
// ===========================================================================

test('recordRetry: writes timestamp, failure_type, task_id, retry_number, max_allowed', () => {
  const sessionDir = makeTempSession();
  try {
    const before = Date.now();
    const entry = recordRetry(sessionDir, 'checkpoint', 'AF-1');
    const after = Date.now();

    assert.equal(entry.failure_type, 'checkpoint');
    assert.equal(entry.task_id, 'AF-1');
    assert.equal(entry.retry_number, 1);
    assert.equal(entry.max_allowed, RETRY_LIMITS.checkpoint);

    const ts = new Date(entry.timestamp).getTime();
    assert.ok(ts >= before && ts <= after, 'timestamp should be within test window');

    const stored = readRetries(sessionDir);
    assert.equal(stored.length, 1);
    assert.deepEqual(stored[0], entry);
  } finally {
    cleanup(sessionDir);
  }
});

test('recordRetry: retry_number increments per task_id + failure_type combination', () => {
  const sessionDir = makeTempSession();
  try {
    const e1 = recordRetry(sessionDir, 'checkpoint', 'AF-1');
    const e2 = recordRetry(sessionDir, 'checkpoint', 'AF-1');
    assert.equal(e1.retry_number, 1);
    assert.equal(e2.retry_number, 2);
  } finally {
    cleanup(sessionDir);
  }
});

test('recordRetry: retry_number is independent across different task_ids', () => {
  const sessionDir = makeTempSession();
  try {
    const e1 = recordRetry(sessionDir, 'checkpoint', 'AF-1');
    const e2 = recordRetry(sessionDir, 'checkpoint', 'AF-2');
    assert.equal(e1.retry_number, 1, 'AF-1 first retry should be 1');
    assert.equal(e2.retry_number, 1, 'AF-2 first retry should be 1, not 2');
  } finally {
    cleanup(sessionDir);
  }
});

test('recordRetry: retry_number is independent across different failure types', () => {
  const sessionDir = makeTempSession();
  try {
    const e1 = recordRetry(sessionDir, 'checkpoint', 'AF-1');
    const e2 = recordRetry(sessionDir, 'agent_error', 'AF-1');
    assert.equal(e1.retry_number, 1);
    assert.equal(e2.retry_number, 1, 'different failure type starts at 1');
  } finally {
    cleanup(sessionDir);
  }
});

test('recordRetry: max_allowed is 0 for unknown failure type', () => {
  const sessionDir = makeTempSession();
  try {
    const entry = recordRetry(sessionDir, 'unknown_type', 'AF-1');
    assert.equal(entry.max_allowed, 0);
  } finally {
    cleanup(sessionDir);
  }
});

test('recordRetry: max_allowed is correct for each known failure type', () => {
  const sessionDir = makeTempSession();
  try {
    const eCheckpoint = recordRetry(sessionDir, 'checkpoint', 'AF-1');
    const eAgentError = recordRetry(sessionDir, 'agent_error', 'AF-2');
    const eStuck = recordRetry(sessionDir, 'stuck', 'AF-3');

    assert.equal(eCheckpoint.max_allowed, 2);
    assert.equal(eAgentError.max_allowed, 1);
    assert.equal(eStuck.max_allowed, 0);
  } finally {
    cleanup(sessionDir);
  }
});

test('recordRetry: appends to existing retries.json rather than overwriting', () => {
  const sessionDir = makeTempSession();
  try {
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    recordRetry(sessionDir, 'agent_error', 'AF-2');
    recordRetry(sessionDir, 'checkpoint', 'AF-3');

    const stored = readRetries(sessionDir);
    assert.equal(stored.length, 3);
  } finally {
    cleanup(sessionDir);
  }
});

// ===========================================================================
// canRetry
// ===========================================================================

test('canRetry: returns true when no retries have been recorded', () => {
  const sessionDir = makeTempSession();
  try {
    assert.equal(canRetry(sessionDir, 'checkpoint', 'AF-1'), true);
  } finally {
    cleanup(sessionDir);
  }
});

test('canRetry: returns true when below per-type limit', () => {
  const sessionDir = makeTempSession();
  try {
    // checkpoint limit is 2; after 1 retry, should still be allowed
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    assert.equal(canRetry(sessionDir, 'checkpoint', 'AF-1'), true);
  } finally {
    cleanup(sessionDir);
  }
});

test('canRetry: returns false when per-type limit is reached', () => {
  const sessionDir = makeTempSession();
  try {
    // checkpoint limit is 2
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    assert.equal(canRetry(sessionDir, 'checkpoint', 'AF-1'), false);
  } finally {
    cleanup(sessionDir);
  }
});

test('canRetry: returns false immediately for "stuck" (limit 0)', () => {
  const sessionDir = makeTempSession();
  try {
    assert.equal(canRetry(sessionDir, 'stuck', 'AF-1'), false);
  } finally {
    cleanup(sessionDir);
  }
});

test('canRetry: returns false when global cap of 5 is reached', () => {
  const sessionDir = makeTempSession();
  try {
    // Fill up to global cap using different tasks to avoid per-type limit
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    recordRetry(sessionDir, 'checkpoint', 'AF-2');
    recordRetry(sessionDir, 'checkpoint', 'AF-2');
    recordRetry(sessionDir, 'checkpoint', 'AF-3');

    assert.equal(getTotalRetries(sessionDir), GLOBAL_RETRY_CAP);
    // Even a fresh task that hasn't been retried should be blocked
    assert.equal(canRetry(sessionDir, 'checkpoint', 'AF-99'), false);
  } finally {
    cleanup(sessionDir);
  }
});

test('canRetry: global cap enforced across different failure types', () => {
  const sessionDir = makeTempSession();
  try {
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    recordRetry(sessionDir, 'checkpoint', 'AF-2');
    recordRetry(sessionDir, 'checkpoint', 'AF-2');
    recordRetry(sessionDir, 'agent_error', 'AF-3');

    assert.equal(getTotalRetries(sessionDir), 5);
    assert.equal(canRetry(sessionDir, 'agent_error', 'AF-4'), false);
  } finally {
    cleanup(sessionDir);
  }
});

test('canRetry: per-type limit is independent for different task_ids', () => {
  const sessionDir = makeTempSession();
  try {
    // Exhaust checkpoint retries for AF-1
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    assert.equal(canRetry(sessionDir, 'checkpoint', 'AF-1'), false);

    // AF-2 should still be allowed since it hasn't been retried
    assert.equal(canRetry(sessionDir, 'checkpoint', 'AF-2'), true);
  } finally {
    cleanup(sessionDir);
  }
});

test('canRetry: returns false for unknown failure type (limit 0)', () => {
  const sessionDir = makeTempSession();
  try {
    assert.equal(canRetry(sessionDir, 'unknown_type', 'AF-1'), false);
  } finally {
    cleanup(sessionDir);
  }
});

// ===========================================================================
// getTotalRetries
// ===========================================================================

test('getTotalRetries: returns 0 for a fresh session directory', () => {
  const sessionDir = makeTempSession();
  try {
    assert.equal(getTotalRetries(sessionDir), 0);
  } finally {
    cleanup(sessionDir);
  }
});

test('getTotalRetries: returns correct count after multiple records', () => {
  const sessionDir = makeTempSession();
  try {
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    assert.equal(getTotalRetries(sessionDir), 1);

    recordRetry(sessionDir, 'agent_error', 'AF-2');
    assert.equal(getTotalRetries(sessionDir), 2);

    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    assert.equal(getTotalRetries(sessionDir), 3);
  } finally {
    cleanup(sessionDir);
  }
});

// ===========================================================================
// resetRetries
// ===========================================================================

test('resetRetries: clears retries.json to an empty array', () => {
  const sessionDir = makeTempSession();
  try {
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    recordRetry(sessionDir, 'agent_error', 'AF-2');
    assert.equal(getTotalRetries(sessionDir), 2);

    resetRetries(sessionDir);

    const stored = readRetries(sessionDir);
    assert.deepEqual(stored, []);
    assert.equal(getTotalRetries(sessionDir), 0);
  } finally {
    cleanup(sessionDir);
  }
});

test('resetRetries: is idempotent on a fresh session directory', () => {
  const sessionDir = makeTempSession();
  try {
    // Should not throw even though retries.json doesn't exist yet
    resetRetries(sessionDir);
    const stored = readRetries(sessionDir);
    assert.deepEqual(stored, []);
  } finally {
    cleanup(sessionDir);
  }
});

test('resetRetries: canRetry returns true again after reset', () => {
  const sessionDir = makeTempSession();
  try {
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    recordRetry(sessionDir, 'checkpoint', 'AF-1');
    assert.equal(canRetry(sessionDir, 'checkpoint', 'AF-1'), false);

    resetRetries(sessionDir);
    assert.equal(canRetry(sessionDir, 'checkpoint', 'AF-1'), true);
  } finally {
    cleanup(sessionDir);
  }
});

// ===========================================================================
// Atomic write
// ===========================================================================

test('atomic write: no .tmp file left behind after recordRetry', () => {
  const sessionDir = makeTempSession();
  try {
    recordRetry(sessionDir, 'checkpoint', 'AF-1');

    const tmpPath = path.join(sessionDir, RETRIES_FILE + '.tmp');
    assert.equal(
      fs.existsSync(tmpPath),
      false,
      '.tmp file should be cleaned up after atomic rename'
    );
  } finally {
    cleanup(sessionDir);
  }
});

test('atomic write: no .tmp file left behind after resetRetries', () => {
  const sessionDir = makeTempSession();
  try {
    resetRetries(sessionDir);

    const tmpPath = path.join(sessionDir, RETRIES_FILE + '.tmp');
    assert.equal(
      fs.existsSync(tmpPath),
      false,
      '.tmp file should be cleaned up after atomic rename'
    );
  } finally {
    cleanup(sessionDir);
  }
});
