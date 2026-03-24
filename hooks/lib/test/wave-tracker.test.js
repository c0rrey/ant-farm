'use strict';

/**
 * wave-tracker.test.js — Tests for wave-tracker.js.
 *
 * Tests cover:
 *   - recordAgentResult(): writes success entry to per-wave file
 *   - recordAgentResult(): writes failure entry to per-wave file
 *   - recordAgentResult(): multiple agents accumulate in the same wave file
 *   - recordAgentResult(): concurrent writes use atomic tmp+rename pattern (no orphaned tmp file)
 *   - recordAgentResult(): rejects invalid status values
 *   - getWaveStatus(): returns { total:0, succeeded:0, failed:0, failureRate:0 } when no file exists
 *   - getWaveStatus(): returns correct counts after recording successes and failures
 *   - getWaveStatus(): failureRate = failed / total (not 1/0)
 *   - getWaveStatus(): failureRate is 0 when total is 0 (no divide-by-zero)
 *   - getWaveStatus(): correctly tracks separate wave files independently
 *   - WAVE_RESULTS_FILENAME is exported and follows the expected pattern
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  recordAgentResult,
  getWaveStatus,
  WAVE_RESULTS_FILENAME,
} = require('../wave-tracker');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Create an isolated tmp directory for a test. Caller must clean up. */
function mkTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'wave-tracker-test-'));
}

/** Remove a tmp directory and all its contents. */
function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

// ---------------------------------------------------------------------------
// WAVE_RESULTS_FILENAME helper
// ---------------------------------------------------------------------------

describe('WAVE_RESULTS_FILENAME', () => {
  test('is a function that returns a per-wave filename', () => {
    const name = WAVE_RESULTS_FILENAME(1);
    assert.equal(typeof name, 'string', 'WAVE_RESULTS_FILENAME(1) must return a string');
    assert.ok(name.includes('1'), 'filename must include the wave number');
  });

  test('returns different filenames for different wave numbers', () => {
    const name1 = WAVE_RESULTS_FILENAME(1);
    const name2 = WAVE_RESULTS_FILENAME(2);
    assert.notEqual(name1, name2, 'Different waves must have different filenames');
  });
});

// ---------------------------------------------------------------------------
// recordAgentResult()
// ---------------------------------------------------------------------------

describe('recordAgentResult', () => {
  test('creates per-wave file on first write (success)', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 1, 'agent-1', 'success');
      const filePath = path.join(tmpDir, WAVE_RESULTS_FILENAME(1));
      assert.ok(fs.existsSync(filePath), 'wave results file should be created');

      const raw = fs.readFileSync(filePath, 'utf8');
      const parsed = JSON.parse(raw);
      assert.ok(Array.isArray(parsed), 'file content must be a JSON array');
      assert.equal(parsed.length, 1, 'should have exactly one entry');
      assert.equal(parsed[0].agent_id, 'agent-1');
      assert.equal(parsed[0].status, 'success');
      assert.equal(typeof parsed[0].timestamp, 'string');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('creates per-wave file on first write (failure)', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 2, 'agent-x', 'failure');
      const filePath = path.join(tmpDir, WAVE_RESULTS_FILENAME(2));
      assert.ok(fs.existsSync(filePath), 'wave results file should be created');

      const raw = fs.readFileSync(filePath, 'utf8');
      const parsed = JSON.parse(raw);
      assert.equal(parsed.length, 1);
      assert.equal(parsed[0].status, 'failure');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('accumulates multiple agents in the same wave file', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 1, 'agent-a', 'success');
      recordAgentResult(tmpDir, 1, 'agent-b', 'failure');
      recordAgentResult(tmpDir, 1, 'agent-c', 'success');

      const filePath = path.join(tmpDir, WAVE_RESULTS_FILENAME(1));
      const raw = fs.readFileSync(filePath, 'utf8');
      const parsed = JSON.parse(raw);
      assert.equal(parsed.length, 3, 'all three agent results should be in the file');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('stores wave number in each entry', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 3, 'agent-q', 'success');
      const filePath = path.join(tmpDir, WAVE_RESULTS_FILENAME(3));
      const parsed = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      assert.equal(parsed[0].wave, 3, 'wave number must be stored in the entry');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('atomic write: no orphaned tmp file left on disk after successful write', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 1, 'agent-1', 'success');
      const files = fs.readdirSync(tmpDir);
      const tmpFiles = files.filter((f) => f.endsWith('.tmp'));
      assert.equal(tmpFiles.length, 0, 'No tmp files should remain after write');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('throws (or propagates) when status is neither success nor failure', () => {
    const tmpDir = mkTmpDir();
    try {
      assert.throws(
        () => recordAgentResult(tmpDir, 1, 'agent-1', 'invalid-status'),
        { message: /invalid status/i },
        'Should throw for invalid status values'
      );
    } finally {
      cleanup(tmpDir);
    }
  });

  test('does not overwrite existing entries (append-style)', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 1, 'agent-a', 'success');
      const before = JSON.parse(fs.readFileSync(path.join(tmpDir, WAVE_RESULTS_FILENAME(1)), 'utf8'));
      assert.equal(before.length, 1);

      recordAgentResult(tmpDir, 1, 'agent-b', 'success');
      const after = JSON.parse(fs.readFileSync(path.join(tmpDir, WAVE_RESULTS_FILENAME(1)), 'utf8'));
      assert.equal(after.length, 2, 'second write must append, not overwrite');
      assert.equal(after[0].agent_id, 'agent-a', 'first entry must be preserved');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('separate waves go to separate files', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 1, 'agent-a', 'success');
      recordAgentResult(tmpDir, 2, 'agent-b', 'failure');

      const wave1 = JSON.parse(fs.readFileSync(path.join(tmpDir, WAVE_RESULTS_FILENAME(1)), 'utf8'));
      const wave2 = JSON.parse(fs.readFileSync(path.join(tmpDir, WAVE_RESULTS_FILENAME(2)), 'utf8'));

      assert.equal(wave1.length, 1, 'wave 1 should have 1 entry');
      assert.equal(wave2.length, 1, 'wave 2 should have 1 entry');
      assert.equal(wave1[0].agent_id, 'agent-a');
      assert.equal(wave2[0].agent_id, 'agent-b');
    } finally {
      cleanup(tmpDir);
    }
  });
});

// ---------------------------------------------------------------------------
// getWaveStatus()
// ---------------------------------------------------------------------------

describe('getWaveStatus', () => {
  test('returns zero counts when no results file exists', () => {
    const tmpDir = mkTmpDir();
    try {
      const status = getWaveStatus(tmpDir, 1);
      assert.deepEqual(status, { total: 0, succeeded: 0, failed: 0, failureRate: 0 });
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns correct counts after recording only successes', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 1, 'agent-a', 'success');
      recordAgentResult(tmpDir, 1, 'agent-b', 'success');

      const status = getWaveStatus(tmpDir, 1);
      assert.equal(status.total, 2);
      assert.equal(status.succeeded, 2);
      assert.equal(status.failed, 0);
      assert.equal(status.failureRate, 0);
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns correct counts after recording only failures', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 1, 'agent-a', 'failure');
      recordAgentResult(tmpDir, 1, 'agent-b', 'failure');

      const status = getWaveStatus(tmpDir, 1);
      assert.equal(status.total, 2);
      assert.equal(status.succeeded, 0);
      assert.equal(status.failed, 2);
      assert.equal(status.failureRate, 1);
    } finally {
      cleanup(tmpDir);
    }
  });

  test('computes failureRate as failed/total', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 1, 'agent-a', 'success');
      recordAgentResult(tmpDir, 1, 'agent-b', 'failure');
      recordAgentResult(tmpDir, 1, 'agent-c', 'success');
      recordAgentResult(tmpDir, 1, 'agent-d', 'failure');

      const status = getWaveStatus(tmpDir, 1);
      assert.equal(status.total, 4);
      assert.equal(status.succeeded, 2);
      assert.equal(status.failed, 2);
      assert.equal(status.failureRate, 0.5);
    } finally {
      cleanup(tmpDir);
    }
  });

  test('failureRate is 0 when total is 0 (no divide-by-zero)', () => {
    const tmpDir = mkTmpDir();
    try {
      // Write an empty array file manually
      const filePath = path.join(tmpDir, WAVE_RESULTS_FILENAME(1));
      fs.writeFileSync(filePath, '[]', 'utf8');

      const status = getWaveStatus(tmpDir, 1);
      assert.equal(status.total, 0);
      assert.equal(status.failureRate, 0, 'failureRate must be 0 when total is 0');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('tracks separate wave files independently', () => {
    const tmpDir = mkTmpDir();
    try {
      // Wave 1: all success
      recordAgentResult(tmpDir, 1, 'agent-a', 'success');
      recordAgentResult(tmpDir, 1, 'agent-b', 'success');
      // Wave 2: all failure
      recordAgentResult(tmpDir, 2, 'agent-c', 'failure');
      recordAgentResult(tmpDir, 2, 'agent-d', 'failure');

      const status1 = getWaveStatus(tmpDir, 1);
      const status2 = getWaveStatus(tmpDir, 2);

      assert.equal(status1.failureRate, 0, 'wave 1 should have 0% failure rate');
      assert.equal(status2.failureRate, 1, 'wave 2 should have 100% failure rate');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns zero counts for a wave number that has no results even when other waves exist', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 1, 'agent-a', 'success');

      const status = getWaveStatus(tmpDir, 99);
      assert.deepEqual(status, { total: 0, succeeded: 0, failed: 0, failureRate: 0 });
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns correct counts for a mixed wave result (1 success, 3 failures)', () => {
    const tmpDir = mkTmpDir();
    try {
      recordAgentResult(tmpDir, 4, 'agent-1', 'success');
      recordAgentResult(tmpDir, 4, 'agent-2', 'failure');
      recordAgentResult(tmpDir, 4, 'agent-3', 'failure');
      recordAgentResult(tmpDir, 4, 'agent-4', 'failure');

      const status = getWaveStatus(tmpDir, 4);
      assert.equal(status.total, 4);
      assert.equal(status.succeeded, 1);
      assert.equal(status.failed, 3);
      assert.equal(status.failureRate, 0.75);
    } finally {
      cleanup(tmpDir);
    }
  });
});
