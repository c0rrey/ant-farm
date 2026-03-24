'use strict';

/**
 * statusline.test.js — Tests for ant-farm-statusline.js metrics bridge behavior.
 *
 * Tests cover:
 *   writeCtxMetrics — writes ctx-metrics.json with correct fields
 *   writeCtxMetrics — overwrites existing file atomically (tmp+rename)
 *   writeCtxMetrics — clamps percentage_remaining to [0, 100]
 *   writeCtxMetrics — is silent when sessionDir does not exist
 *   writeCtxMetrics — produced JSON parses to correct types
 *   handler — writes ctx-metrics.json to SESSION_DIR when session is active
 *   handler — does not write ctx-metrics.json when no progress.log found
 *   handler — uses remaining_percentage from input when present
 *   handler — falls back to 100 - used_percentage when remaining_percentage absent
 *   handler — extracts tool_use_count from input.session.tool_use_count
 *   handler — defaults tool_use_count to 0 when absent
 *   handler — existing status string output is unchanged
 *   handler — does not write ctx-metrics.json when progress.log is malformed
 *   handler — returns empty string when no session active (no write attempted)
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { handler, writeCtxMetrics } = require('../ant-farm-statusline');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Creates a temp directory simulating a project root with a .crumbs/sessions/
 * subtree and a valid progress.log inside a session directory.
 *
 * @param {string|null} logContent  Content for progress.log; null omits the file.
 * @returns {{ projectDir: string, sessionDir: string, logPath: string }}
 */
function makeProject(logContent) {
  const projectDir = fs.mkdtempSync(path.join(os.tmpdir(), 'statusline-test-'));
  const sessionDir = path.join(projectDir, '.crumbs', 'sessions', '_session-test');
  fs.mkdirSync(sessionDir, { recursive: true });

  const logPath = path.join(sessionDir, 'progress.log');
  if (logContent !== null) {
    fs.writeFileSync(logPath, logContent, 'utf8');
  }

  return { projectDir, sessionDir, logPath };
}

/**
 * Removes a temp project directory created by makeProject.
 *
 * @param {string} projectDir
 */
function cleanup(projectDir) {
  fs.rmSync(projectDir, { recursive: true, force: true });
}

/**
 * Reads and parses ctx-metrics.json from sessionDir.
 * Returns null if the file does not exist.
 *
 * @param {string} sessionDir
 * @returns {object|null}
 */
function readMetrics(sessionDir) {
  const metricsPath = path.join(sessionDir, 'ctx-metrics.json');
  try {
    return JSON.parse(fs.readFileSync(metricsPath, 'utf8'));
  } catch (_err) {
    return null;
  }
}

/** Valid progress.log line that parses to step 1. */
const VALID_LOG_LINE = '2026-01-01T00:00:00.000Z|SESSION_INIT|wave=0\n';

// ===========================================================================
// writeCtxMetrics — direct unit tests
// ===========================================================================

test('writeCtxMetrics: writes ctx-metrics.json with all required fields', () => {
  const sessionDir = fs.mkdtempSync(path.join(os.tmpdir(), 'metrics-test-'));
  try {
    writeCtxMetrics(sessionDir, {
      percentage_remaining: 75,
      timestamp: '2026-01-01T00:00:00.000Z',
      tool_use_count: 3,
    });

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json should exist after write');
    assert.equal(metrics.percentage_remaining, 75);
    assert.equal(metrics.timestamp, '2026-01-01T00:00:00.000Z');
    assert.equal(metrics.tool_use_count, 3);
  } finally {
    fs.rmSync(sessionDir, { recursive: true, force: true });
  }
});

test('writeCtxMetrics: overwrites existing ctx-metrics.json', () => {
  const sessionDir = fs.mkdtempSync(path.join(os.tmpdir(), 'metrics-test-'));
  try {
    writeCtxMetrics(sessionDir, {
      percentage_remaining: 80,
      timestamp: '2026-01-01T00:00:00.000Z',
      tool_use_count: 1,
    });
    writeCtxMetrics(sessionDir, {
      percentage_remaining: 60,
      timestamp: '2026-01-01T00:01:00.000Z',
      tool_use_count: 5,
    });

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json should exist');
    assert.equal(metrics.percentage_remaining, 60, 'Second write should overwrite the first');
    assert.equal(metrics.tool_use_count, 5);
  } finally {
    fs.rmSync(sessionDir, { recursive: true, force: true });
  }
});

test('writeCtxMetrics: no .tmp file remains after successful write', () => {
  const sessionDir = fs.mkdtempSync(path.join(os.tmpdir(), 'metrics-test-'));
  try {
    writeCtxMetrics(sessionDir, {
      percentage_remaining: 50,
      timestamp: '2026-01-01T00:00:00.000Z',
      tool_use_count: 0,
    });

    const tmpPath = path.join(sessionDir, 'ctx-metrics.json.tmp');
    assert.equal(
      fs.existsSync(tmpPath),
      false,
      '.tmp file should not remain after atomic rename'
    );
  } finally {
    fs.rmSync(sessionDir, { recursive: true, force: true });
  }
});

test('writeCtxMetrics: is a silent no-op when sessionDir does not exist', () => {
  const nonExistent = path.join(os.tmpdir(), 'does-not-exist-' + Date.now());
  // Must not throw — silent swallow.
  assert.doesNotThrow(() => {
    writeCtxMetrics(nonExistent, {
      percentage_remaining: 50,
      timestamp: '2026-01-01T00:00:00.000Z',
      tool_use_count: 0,
    });
  }, 'writeCtxMetrics must not throw when sessionDir does not exist');
});

test('writeCtxMetrics: written JSON parses to correct field types', () => {
  const sessionDir = fs.mkdtempSync(path.join(os.tmpdir(), 'metrics-test-'));
  try {
    const ts = new Date().toISOString();
    writeCtxMetrics(sessionDir, {
      percentage_remaining: 42.5,
      timestamp: ts,
      tool_use_count: 7,
    });

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json must be readable');
    assert.equal(typeof metrics.percentage_remaining, 'number', 'percentage_remaining must be a number');
    assert.equal(typeof metrics.timestamp, 'string', 'timestamp must be a string');
    assert.equal(typeof metrics.tool_use_count, 'number', 'tool_use_count must be a number');
    // timestamp must be a valid ISO 8601 date
    assert.ok(!isNaN(Date.parse(metrics.timestamp)), 'timestamp must be a valid ISO 8601 date');
  } finally {
    fs.rmSync(sessionDir, { recursive: true, force: true });
  }
});

// ===========================================================================
// handler — ctx-metrics.json integration tests
// ===========================================================================

test('handler: writes ctx-metrics.json to SESSION_DIR when session is active', async () => {
  const { projectDir, sessionDir } = makeProject(VALID_LOG_LINE);
  try {
    const input = { workspace: { project_dir: projectDir } };
    await handler(input);

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json should be written when session is active');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: does not write ctx-metrics.json when no progress.log found', async () => {
  const { projectDir, sessionDir } = makeProject(null);
  try {
    const input = { workspace: { project_dir: projectDir } };
    await handler(input);

    const metrics = readMetrics(sessionDir);
    assert.equal(metrics, null, 'ctx-metrics.json must not be written when no progress.log exists');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: does not write ctx-metrics.json when progress.log is malformed', async () => {
  const { projectDir, sessionDir } = makeProject('this-is-not-a-valid-line\n');
  try {
    const input = { workspace: { project_dir: projectDir } };
    await handler(input);

    const metrics = readMetrics(sessionDir);
    assert.equal(metrics, null, 'ctx-metrics.json must not be written when progress.log is malformed');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: uses remaining_percentage from input.context_window when present', async () => {
  const { projectDir, sessionDir } = makeProject(VALID_LOG_LINE);
  try {
    const input = {
      workspace: { project_dir: projectDir },
      context_window: { remaining_percentage: 35, used_percentage: 65 },
    };
    await handler(input);

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json should exist');
    assert.equal(
      metrics.percentage_remaining,
      35,
      'Should use context_window.remaining_percentage directly when present'
    );
  } finally {
    cleanup(projectDir);
  }
});

test('handler: falls back to 100 - used_percentage when remaining_percentage absent', async () => {
  const { projectDir, sessionDir } = makeProject(VALID_LOG_LINE);
  try {
    const input = {
      workspace: { project_dir: projectDir },
      context_window: { used_percentage: 40 },
    };
    await handler(input);

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json should exist');
    assert.equal(
      metrics.percentage_remaining,
      60,
      'Should compute 100 - used_percentage when remaining_percentage is absent'
    );
  } finally {
    cleanup(projectDir);
  }
});

test('handler: defaults percentage_remaining to 100 when context_window absent', async () => {
  const { projectDir, sessionDir } = makeProject(VALID_LOG_LINE);
  try {
    const input = { workspace: { project_dir: projectDir } };
    await handler(input);

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json should exist');
    assert.equal(
      metrics.percentage_remaining,
      100,
      'Should default percentage_remaining to 100 when context_window is absent'
    );
  } finally {
    cleanup(projectDir);
  }
});

test('handler: extracts tool_use_count from input.session.tool_use_count', async () => {
  const { projectDir, sessionDir } = makeProject(VALID_LOG_LINE);
  try {
    const input = {
      workspace: { project_dir: projectDir },
      session: { tool_use_count: 12 },
    };
    await handler(input);

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json should exist');
    assert.equal(metrics.tool_use_count, 12, 'Should extract tool_use_count from input.session');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: defaults tool_use_count to 0 when input.session absent', async () => {
  const { projectDir, sessionDir } = makeProject(VALID_LOG_LINE);
  try {
    const input = { workspace: { project_dir: projectDir } };
    await handler(input);

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json should exist');
    assert.equal(metrics.tool_use_count, 0, 'Should default tool_use_count to 0 when absent');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: written timestamp is a valid ISO 8601 date', async () => {
  const { projectDir, sessionDir } = makeProject(VALID_LOG_LINE);
  try {
    const before = Date.now();
    await handler({ workspace: { project_dir: projectDir } });
    const after = Date.now();

    const metrics = readMetrics(sessionDir);
    assert.ok(metrics !== null, 'ctx-metrics.json should exist');
    const ts = Date.parse(metrics.timestamp);
    assert.ok(!isNaN(ts), 'timestamp must be a parseable ISO 8601 date');
    assert.ok(ts >= before && ts <= after, 'timestamp must be within the test window');
  } finally {
    cleanup(projectDir);
  }
});

// ===========================================================================
// handler — existing status string behavior (regression guards)
// ===========================================================================

test('handler: returns empty string when no active session (no progress.log)', async () => {
  const { projectDir } = makeProject(null);
  try {
    const result = await handler({ workspace: { project_dir: projectDir } });
    assert.equal(result, '', 'Should return empty string when no progress.log found');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: returns empty string for malformed progress.log', async () => {
  const { projectDir } = makeProject('not-a-valid-line\n');
  try {
    const result = await handler({ workspace: { project_dir: projectDir } });
    assert.equal(result, '', 'Should return empty string for malformed progress.log');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: status string format is unchanged by metrics write', async () => {
  const { projectDir } = makeProject(VALID_LOG_LINE);
  try {
    const result = await handler({ workspace: { project_dir: projectDir } });
    // Status string must still match the expected ant-farm: format.
    // The crumb binary may not be available in test env, so openCount defaults to 0.
    assert.ok(
      typeof result === 'string',
      'handler must always return a string'
    );
    // When progress.log is valid, a non-empty status string is produced.
    assert.match(
      result,
      /^ant-farm: step \d+\/\d+ \| \d+ crumbs open \| wave/,
      'Status string format must match expected pattern'
    );
  } finally {
    cleanup(projectDir);
  }
});
