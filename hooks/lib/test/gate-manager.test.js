'use strict';

/**
 * gate-manager.test.js — Tests for gate-manager.js.
 *
 * Tests cover:
 *   - GATE_CHAIN constant: defined, ordered array of strings, expected members
 *   - readGateStatus(): returns null when file absent
 *   - readGateStatus(): returns null for malformed JSON
 *   - readGateStatus(): returns null when `gates` key is missing
 *   - readGateStatus(): returns null when `gates` is not a plain object
 *   - readGateStatus(): returns parsed GateStatus when file is valid
 *   - writeGateVerdict(): creates gate-status.json when absent
 *   - writeGateVerdict(): overwrites an existing gate entry
 *   - writeGateVerdict(): preserves other gate entries on write
 *   - writeGateVerdict(): merges extra meta fields into the entry
 *   - writeGateVerdict(): uses tmp+rename pattern (atomic write)
 *   - writeGateVerdict(): ignores non-object meta gracefully
 *   - isGatePassed(): returns false when file absent
 *   - isGatePassed(): returns true when gate verdict is 'PASS'
 *   - isGatePassed(): returns false when gate verdict is 'FAIL'
 *   - isGatePassed(): returns false when gate has no entry
 *   - isGatePassed(): returns false for any non-'PASS' verdict value
 */

const { test, describe } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  GATE_CHAIN,
  GATE_STATUS_FILENAME,
  readGateStatus,
  writeGateVerdict,
  isGatePassed,
} = require('../gate-manager');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Create an isolated tmp directory for a test. Caller must clean up. */
function mkTmpDir() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'gate-manager-test-'));
}

/** Remove a tmp directory and all its contents. */
function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

/** Write raw JSON directly to gate-status.json (bypasses atomic path). */
function writeRawGateFile(dir, data) {
  fs.writeFileSync(path.join(dir, GATE_STATUS_FILENAME), JSON.stringify(data), 'utf8');
}

// ---------------------------------------------------------------------------
// GATE_CHAIN constant
// ---------------------------------------------------------------------------

describe('GATE_CHAIN', () => {
  test('is a non-empty array of strings', () => {
    assert.ok(Array.isArray(GATE_CHAIN), 'GATE_CHAIN must be an array');
    assert.ok(GATE_CHAIN.length > 0, 'GATE_CHAIN must not be empty');
    for (const item of GATE_CHAIN) {
      assert.equal(typeof item, 'string', `Each entry must be a string, got: ${typeof item}`);
    }
  });

  test('contains the expected gate names in the correct order', () => {
    assert.ok(GATE_CHAIN.includes('startup-check'), 'should include startup-check');
    assert.ok(GATE_CHAIN.includes('pre-spawn-check'), 'should include pre-spawn-check');
    assert.ok(GATE_CHAIN.includes('scope-verify'), 'should include scope-verify');
    assert.ok(GATE_CHAIN.includes('claims-vs-code'), 'should include claims-vs-code');
    assert.ok(GATE_CHAIN.includes('review-integrity'), 'should include review-integrity');
    assert.ok(GATE_CHAIN.includes('session-complete'), 'should include session-complete');

    // Order assertions: startup-check comes before session-complete
    assert.ok(
      GATE_CHAIN.indexOf('startup-check') < GATE_CHAIN.indexOf('session-complete'),
      'startup-check must precede session-complete'
    );
    assert.ok(
      GATE_CHAIN.indexOf('startup-check') < GATE_CHAIN.indexOf('pre-spawn-check'),
      'startup-check must precede pre-spawn-check'
    );
    assert.ok(
      GATE_CHAIN.indexOf('pre-spawn-check') < GATE_CHAIN.indexOf('scope-verify'),
      'pre-spawn-check must precede scope-verify'
    );
    assert.ok(
      GATE_CHAIN.indexOf('scope-verify') < GATE_CHAIN.indexOf('claims-vs-code'),
      'scope-verify must precede claims-vs-code'
    );
    assert.ok(
      GATE_CHAIN.indexOf('claims-vs-code') < GATE_CHAIN.indexOf('review-integrity'),
      'claims-vs-code must precede review-integrity'
    );
    assert.ok(
      GATE_CHAIN.indexOf('review-integrity') < GATE_CHAIN.indexOf('session-complete'),
      'review-integrity must precede session-complete'
    );
  });
});

// ---------------------------------------------------------------------------
// readGateStatus()
// ---------------------------------------------------------------------------

describe('readGateStatus', () => {
  test('returns null when gate-status.json does not exist', () => {
    const tmpDir = mkTmpDir();
    try {
      const result = readGateStatus(tmpDir);
      assert.equal(result, null, 'Should return null when file is absent');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns null for malformed JSON', () => {
    const tmpDir = mkTmpDir();
    try {
      fs.writeFileSync(path.join(tmpDir, GATE_STATUS_FILENAME), '{ bad json }', 'utf8');
      const result = readGateStatus(tmpDir);
      assert.equal(result, null, 'Should return null for invalid JSON');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns null when `gates` key is missing', () => {
    const tmpDir = mkTmpDir();
    try {
      writeRawGateFile(tmpDir, { something_else: {} });
      const result = readGateStatus(tmpDir);
      assert.equal(result, null, 'Should return null when `gates` is absent');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns null when `gates` is an array (wrong shape)', () => {
    const tmpDir = mkTmpDir();
    try {
      writeRawGateFile(tmpDir, { gates: [] });
      const result = readGateStatus(tmpDir);
      assert.equal(result, null, 'Should return null when `gates` is an array');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns null when `gates` is null', () => {
    const tmpDir = mkTmpDir();
    try {
      writeRawGateFile(tmpDir, { gates: null });
      const result = readGateStatus(tmpDir);
      assert.equal(result, null, 'Should return null when `gates` is null');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns null when top-level value is an array', () => {
    const tmpDir = mkTmpDir();
    try {
      fs.writeFileSync(
        path.join(tmpDir, GATE_STATUS_FILENAME),
        JSON.stringify([{ gates: {} }]),
        'utf8'
      );
      const result = readGateStatus(tmpDir);
      assert.equal(result, null, 'Should return null when root is an array');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns parsed GateStatus with correct shape for valid file', () => {
    const tmpDir = mkTmpDir();
    try {
      writeRawGateFile(tmpDir, {
        gates: {
          'startup-check': { verdict: 'PASS', timestamp: '2026-01-01T00:00:00.000Z' },
        },
      });
      const result = readGateStatus(tmpDir);
      assert.ok(result !== null, 'Should return a GateStatus object');
      assert.ok(typeof result.gates === 'object', '`gates` should be an object');
      assert.equal(result.gates['startup-check'].verdict, 'PASS');
      assert.equal(result.gates['startup-check'].timestamp, '2026-01-01T00:00:00.000Z');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns GateStatus with multiple gate entries', () => {
    const tmpDir = mkTmpDir();
    try {
      writeRawGateFile(tmpDir, {
        gates: {
          'startup-check': { verdict: 'PASS', timestamp: '2026-01-01T00:00:00.000Z' },
          'pre-spawn-check': { verdict: 'FAIL', timestamp: '2026-01-01T00:01:00.000Z' },
        },
      });
      const result = readGateStatus(tmpDir);
      assert.ok(result !== null);
      assert.equal(result.gates['startup-check'].verdict, 'PASS');
      assert.equal(result.gates['pre-spawn-check'].verdict, 'FAIL');
    } finally {
      cleanup(tmpDir);
    }
  });
});

// ---------------------------------------------------------------------------
// writeGateVerdict()
// ---------------------------------------------------------------------------

describe('writeGateVerdict', () => {
  test('creates gate-status.json when file is absent', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'PASS');
      const filePath = path.join(tmpDir, GATE_STATUS_FILENAME);
      assert.ok(fs.existsSync(filePath), 'gate-status.json should be created');

      const result = readGateStatus(tmpDir);
      assert.ok(result !== null);
      assert.equal(result.gates['startup-check'].verdict, 'PASS');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('includes a valid ISO timestamp in the written entry', () => {
    const tmpDir = mkTmpDir();
    try {
      const before = new Date();
      writeGateVerdict(tmpDir, 'startup-check', 'PASS');
      const after = new Date();

      const result = readGateStatus(tmpDir);
      assert.ok(result !== null);
      const ts = new Date(result.gates['startup-check'].timestamp);
      assert.ok(!isNaN(ts.getTime()), 'timestamp must be a valid date');
      assert.ok(ts >= before, 'timestamp must be after write start');
      assert.ok(ts <= after, 'timestamp must be before write end');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('overwrites an existing gate entry for the same gate name', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'FAIL');
      writeGateVerdict(tmpDir, 'startup-check', 'PASS');

      const result = readGateStatus(tmpDir);
      assert.ok(result !== null);
      assert.equal(result.gates['startup-check'].verdict, 'PASS', 'Second write should win');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('preserves other gate entries when writing a new gate', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'PASS');
      writeGateVerdict(tmpDir, 'pre-spawn-check', 'PASS');

      const result = readGateStatus(tmpDir);
      assert.ok(result !== null);
      assert.equal(result.gates['startup-check'].verdict, 'PASS', 'startup-check must be preserved');
      assert.equal(result.gates['pre-spawn-check'].verdict, 'PASS', 'pre-spawn-check must be written');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('merges extra meta fields into the gate entry', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'session-complete', 'PASS', { run_id: 'abc123', checks: 5 });

      const result = readGateStatus(tmpDir);
      assert.ok(result !== null);
      const entry = result.gates['session-complete'];
      assert.equal(entry.verdict, 'PASS');
      assert.equal(entry.run_id, 'abc123');
      assert.equal(entry.checks, 5);
    } finally {
      cleanup(tmpDir);
    }
  });

  test('handles null meta gracefully (no extra fields beyond verdict+timestamp)', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'FAIL', null);

      const result = readGateStatus(tmpDir);
      assert.ok(result !== null);
      const entry = result.gates['startup-check'];
      assert.equal(entry.verdict, 'FAIL');
      assert.ok('timestamp' in entry, 'timestamp must be present');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('handles array meta gracefully (ignored, not spread)', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'PASS', ['not', 'an', 'object']);

      const result = readGateStatus(tmpDir);
      assert.ok(result !== null);
      // Should just have verdict + timestamp, not array indices as keys
      const entry = result.gates['startup-check'];
      assert.equal(entry.verdict, 'PASS');
      assert.ok(!('0' in entry), 'Array entries must not be spread into the entry');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('atomic write: no orphaned tmp file left on disk after successful write', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'PASS');
      const files = fs.readdirSync(tmpDir);
      const tmpFiles = files.filter((f) => f.startsWith('.gate-status.tmp.'));
      assert.equal(tmpFiles.length, 0, 'No tmp files should remain after successful write');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('written JSON is valid and re-readable', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'claims-vs-code', 'FAIL');
      const raw = fs.readFileSync(path.join(tmpDir, GATE_STATUS_FILENAME), 'utf8');
      // Must not throw
      const parsed = JSON.parse(raw);
      assert.equal(parsed.gates['claims-vs-code'].verdict, 'FAIL');
    } finally {
      cleanup(tmpDir);
    }
  });
});

// ---------------------------------------------------------------------------
// isGatePassed()
// ---------------------------------------------------------------------------

describe('isGatePassed', () => {
  test('returns false when gate-status.json does not exist', () => {
    const tmpDir = mkTmpDir();
    try {
      const result = isGatePassed(tmpDir, 'startup-check');
      assert.equal(result, false, 'Should return false when file is absent');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns false when the gate has no entry in the file', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'PASS');
      const result = isGatePassed(tmpDir, 'pre-spawn-check');
      assert.equal(result, false, 'Should return false for a gate with no entry');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns true when gate verdict is PASS', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'PASS');
      const result = isGatePassed(tmpDir, 'startup-check');
      assert.equal(result, true, 'Should return true for PASS verdict');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns false when gate verdict is FAIL', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'FAIL');
      const result = isGatePassed(tmpDir, 'startup-check');
      assert.equal(result, false, 'Should return false for FAIL verdict');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns false for any non-PASS verdict value (e.g. unknown string)', () => {
    const tmpDir = mkTmpDir();
    try {
      writeRawGateFile(tmpDir, {
        gates: {
          'startup-check': { verdict: 'PENDING', timestamp: '2026-01-01T00:00:00.000Z' },
        },
      });
      const result = isGatePassed(tmpDir, 'startup-check');
      assert.equal(result, false, 'Non-PASS verdict must return false');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('returns false when gate entry has no verdict field', () => {
    const tmpDir = mkTmpDir();
    try {
      writeRawGateFile(tmpDir, {
        gates: {
          'startup-check': { timestamp: '2026-01-01T00:00:00.000Z' },
        },
      });
      const result = isGatePassed(tmpDir, 'startup-check');
      assert.equal(result, false, 'Missing verdict field must return false');
    } finally {
      cleanup(tmpDir);
    }
  });

  test('correctly checks multiple gates independently', () => {
    const tmpDir = mkTmpDir();
    try {
      writeGateVerdict(tmpDir, 'startup-check', 'PASS');
      writeGateVerdict(tmpDir, 'pre-spawn-check', 'FAIL');
      writeGateVerdict(tmpDir, 'scope-verify', 'PASS');

      assert.equal(isGatePassed(tmpDir, 'startup-check'), true);
      assert.equal(isGatePassed(tmpDir, 'pre-spawn-check'), false);
      assert.equal(isGatePassed(tmpDir, 'scope-verify'), true);
      assert.equal(isGatePassed(tmpDir, 'claims-vs-code'), false);  // not written yet
    } finally {
      cleanup(tmpDir);
    }
  });
});
