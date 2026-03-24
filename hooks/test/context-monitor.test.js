'use strict';

/**
 * context-monitor.test.js — Tests for ant-farm-context-monitor.js PostToolUse hook.
 *
 * Tests cover:
 *   - No session directory → silent no-op
 *   - ctx-metrics.json absent → silent no-op
 *   - Below both thresholds → silent no-op
 *   - At warning threshold (35%) → WARNING advisory
 *   - At critical threshold (25%) → CRITICAL advisory
 *   - Below critical threshold (20%) → CRITICAL advisory
 *   - Hook never returns continue: false
 *   - Debounce: second warning within 5 tool uses → silent
 *   - Debounce: warning fires again after 5 tool uses
 *   - Severity escalation (warning → critical) bypasses debounce
 *   - Same severity within debounce window → silent
 *   - Thresholds configurable via config.json
 *   - Default thresholds used when config.json absent
 *   - readCtxMetrics: returns null for absent file
 *   - readCtxMetrics: returns null for malformed JSON
 *   - readDebounceState: returns defaults for absent file
 *   - writeDebounceState: persists and readDebounceState reads it back
 *   - findLatestSessionDir: returns null when sessions dir absent
 *   - findLatestSessionDir: returns most recently modified dir
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  handler,
  findLatestSessionDir,
  readCtxMetrics,
  readDebounceState,
  writeDebounceState,
  readThresholds,
  DEBOUNCE_TOOL_COUNT,
  DEBOUNCE_FILENAME,
  CTX_METRICS_FILENAME,
} = require('../ant-farm-context-monitor');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Creates a temporary project directory with .crumbs/sessions/ structure.
 *
 * @returns {{ projectDir: string, sessionDir: string }}
 */
function createProject() {
  const projectDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  const sessionsDir = path.join(projectDir, '.crumbs', 'sessions');
  fs.mkdirSync(sessionsDir, { recursive: true });
  const sessionDir = fs.mkdtempSync(path.join(sessionsDir, '_session-'));
  return { projectDir, sessionDir };
}

function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

/**
 * Writes ctx-metrics.json to the session directory.
 *
 * @param {string} sessionDir
 * @param {number} percentageRemaining
 * @param {number} [toolUseCount]
 */
function writeMetrics(sessionDir, percentageRemaining, toolUseCount) {
  const metrics = {
    percentage_remaining: percentageRemaining,
    tool_use_count: toolUseCount !== undefined ? toolUseCount : 10,
    timestamp: new Date().toISOString(),
  };
  fs.writeFileSync(
    path.join(sessionDir, CTX_METRICS_FILENAME),
    JSON.stringify(metrics),
    'utf8'
  );
}

/**
 * Writes config.json to the .crumbs directory.
 *
 * @param {string} projectDir
 * @param {object} config
 */
function writeConfig(projectDir, config) {
  const crumbsDir = path.join(projectDir, '.crumbs');
  fs.mkdirSync(crumbsDir, { recursive: true });
  fs.writeFileSync(path.join(crumbsDir, 'config.json'), JSON.stringify(config), 'utf8');
}

/**
 * Builds a minimal PostToolUse input object.
 *
 * @param {string} projectDir
 */
function makeInput(projectDir) {
  return { workspace: { project_dir: projectDir } };
}

// ===========================================================================
// Silent no-op conditions
// ===========================================================================

test('handler: no sessions directory → silent no-op', async () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    const result = await handler(makeInput(tmpDir));
    assert.equal(result, '', 'No session directory should produce no output');
  } finally {
    cleanup(tmpDir);
  }
});

test('handler: ctx-metrics.json absent → silent no-op', async () => {
  const { projectDir, sessionDir } = createProject();
  void sessionDir; // session dir exists but no metrics file
  try {
    const result = await handler(makeInput(projectDir));
    assert.equal(result, '', 'Missing metrics file should produce no output');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: context well above thresholds → silent no-op', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeMetrics(sessionDir, 80, 20);
    const result = await handler(makeInput(projectDir));
    assert.equal(result, '', 'Context above thresholds should produce no output');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: context exactly above warning threshold → silent no-op', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeMetrics(sessionDir, 36, 20); // 36% > 35% threshold
    const result = await handler(makeInput(projectDir));
    assert.equal(result, '');
  } finally {
    cleanup(projectDir);
  }
});

// ===========================================================================
// WARNING threshold
// ===========================================================================

test('handler: at warning threshold (35%) → WARNING advisory', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeMetrics(sessionDir, 35, 10);
    const result = await handler(makeInput(projectDir));

    assert.ok(result !== '', 'Should return advisory at warning threshold');
    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, true, 'Advisory hook must not block (continue: true)');
    assert.ok(typeof parsed.additionalContext === 'string', 'Should include additionalContext');
    assert.ok(parsed.additionalContext.startsWith('WARNING:'), 'Should start with WARNING:');
    assert.ok(parsed.additionalContext.includes('35'), 'Should include the percentage');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: below warning threshold (30%) → WARNING advisory', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeMetrics(sessionDir, 30, 10);
    const result = await handler(makeInput(projectDir));

    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, true);
    assert.ok(parsed.additionalContext.startsWith('WARNING:'));
  } finally {
    cleanup(projectDir);
  }
});

// ===========================================================================
// CRITICAL threshold
// ===========================================================================

test('handler: at critical threshold (25%) → CRITICAL advisory', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeMetrics(sessionDir, 25, 20);
    const result = await handler(makeInput(projectDir));

    assert.ok(result !== '', 'Should return advisory at critical threshold');
    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, true);
    assert.ok(parsed.additionalContext.startsWith('CRITICAL:'), 'Should start with CRITICAL:');
    assert.ok(parsed.additionalContext.includes('25'), 'Should include the percentage');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: well below critical (10%) → CRITICAL advisory', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeMetrics(sessionDir, 10, 50);
    const result = await handler(makeInput(projectDir));

    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, true);
    assert.ok(parsed.additionalContext.startsWith('CRITICAL:'));
  } finally {
    cleanup(projectDir);
  }
});

test('handler: CRITICAL advisory mentions /ant-farm-pause', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeMetrics(sessionDir, 20, 50);
    const result = await handler(makeInput(projectDir));
    const parsed = JSON.parse(result);
    assert.ok(
      parsed.additionalContext.includes('ant-farm-pause'),
      'CRITICAL message should mention /ant-farm-pause'
    );
  } finally {
    cleanup(projectDir);
  }
});

// ===========================================================================
// Advisory-only: never continue: false
// ===========================================================================

test('handler: never returns continue: false (warning level)', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeMetrics(sessionDir, 35, 10);
    const result = await handler(makeInput(projectDir));
    if (result) {
      const parsed = JSON.parse(result);
      assert.notEqual(parsed.continue, false, 'Hook must never block (continue: false)');
    }
  } finally {
    cleanup(projectDir);
  }
});

test('handler: never returns continue: false (critical level)', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeMetrics(sessionDir, 20, 50);
    const result = await handler(makeInput(projectDir));
    if (result) {
      const parsed = JSON.parse(result);
      assert.notEqual(parsed.continue, false, 'Hook must never block (continue: false)');
    }
  } finally {
    cleanup(projectDir);
  }
});

// ===========================================================================
// Debounce behavior
// ===========================================================================

test('handler: warning fires once, then debounced for next 4 tool uses', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    // First call: tool count = 10, threshold = 35%, debounce window = 5
    writeMetrics(sessionDir, 35, 10);
    const first = await handler(makeInput(projectDir));
    assert.ok(first !== '', 'First call should fire warning');

    // Second call: tool count = 11 (within debounce window of 5)
    writeMetrics(sessionDir, 35, 11);
    const second = await handler(makeInput(projectDir));
    assert.equal(second, '', 'Second call within debounce window should be silent');

    // Fourth call: tool count = 14 (still within window: 14 - 10 = 4 < 5)
    writeMetrics(sessionDir, 35, 14);
    const fourth = await handler(makeInput(projectDir));
    assert.equal(fourth, '', 'Fourth call within debounce window should be silent');

    // Fifth call: tool count = 15 — at boundary: 15 - 10 = 5 >= DEBOUNCE_TOOL_COUNT (5), so NOT debounced → fires
    writeMetrics(sessionDir, 35, 15);
    const fifth = await handler(makeInput(projectDir));
    assert.ok(fifth !== '', 'Fifth call (at boundary) should fire warning again');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: warning re-fires after debounce window expires', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    // Fire first warning at tool count 10
    writeMetrics(sessionDir, 35, 10);
    const first = await handler(makeInput(projectDir));
    assert.ok(first !== '', 'First warning should fire');

    // tool count = 16 (16 - 10 = 6 >= 5, debounce expired)
    writeMetrics(sessionDir, 35, 16);
    const second = await handler(makeInput(projectDir));
    assert.ok(second !== '', 'Warning should re-fire after debounce window expires');
  } finally {
    cleanup(projectDir);
  }
});

// ===========================================================================
// Severity escalation bypasses debounce
// ===========================================================================

test('handler: severity escalation (warning → critical) bypasses debounce', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    // Fire warning at tool count 10
    writeMetrics(sessionDir, 32, 10); // 32% → warning
    const first = await handler(makeInput(projectDir));
    assert.ok(first !== '', 'First warning should fire');
    const firstParsed = JSON.parse(first);
    assert.ok(firstParsed.additionalContext.startsWith('WARNING:'));

    // Tool count 11 (within debounce window), but severity escalates to critical
    writeMetrics(sessionDir, 20, 11); // 20% → critical
    const second = await handler(makeInput(projectDir));
    assert.ok(second !== '', 'Severity escalation should bypass debounce');
    const secondParsed = JSON.parse(second);
    assert.ok(secondParsed.additionalContext.startsWith('CRITICAL:'), 'Should upgrade to CRITICAL');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: same critical severity within window → debounced', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    // Fire critical at tool count 10
    writeMetrics(sessionDir, 20, 10);
    const first = await handler(makeInput(projectDir));
    assert.ok(first !== '');
    const firstParsed = JSON.parse(first);
    assert.ok(firstParsed.additionalContext.startsWith('CRITICAL:'));

    // Same critical level, still within window
    writeMetrics(sessionDir, 18, 12); // 12 - 10 = 2 < 5
    const second = await handler(makeInput(projectDir));
    assert.equal(second, '', 'Same severity within debounce window should be silent');
  } finally {
    cleanup(projectDir);
  }
});

// ===========================================================================
// Configurable thresholds
// ===========================================================================

test('handler: thresholds from config.json override defaults', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    // Set custom thresholds: warning at 50%, critical at 40%
    writeConfig(projectDir, {
      context_warning_threshold: 50,
      context_critical_threshold: 40,
    });
    // 45% is below 50% → warning
    writeMetrics(sessionDir, 45, 10);
    const result = await handler(makeInput(projectDir));

    assert.ok(result !== '', 'Custom threshold should trigger at 45%');
    const parsed = JSON.parse(result);
    assert.ok(parsed.additionalContext.startsWith('WARNING:'));
  } finally {
    cleanup(projectDir);
  }
});

test('handler: custom thresholds — above custom warning threshold → silent', async () => {
  const { projectDir, sessionDir } = createProject();
  try {
    writeConfig(projectDir, {
      context_warning_threshold: 30,
      context_critical_threshold: 15,
    });
    // 35% is above 30% custom threshold → silent
    writeMetrics(sessionDir, 35, 10);
    const result = await handler(makeInput(projectDir));
    assert.equal(result, '', 'Above custom threshold should be silent');
  } finally {
    cleanup(projectDir);
  }
});

test('readThresholds: returns defaults when config.json absent', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    const { warningThreshold, criticalThreshold } = readThresholds(tmpDir);
    assert.equal(warningThreshold, 35);
    assert.equal(criticalThreshold, 25);
  } finally {
    cleanup(tmpDir);
  }
});

test('readThresholds: returns values from config.json', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    writeConfig(tmpDir, { context_warning_threshold: 40, context_critical_threshold: 20 });
    const { warningThreshold, criticalThreshold } = readThresholds(tmpDir);
    assert.equal(warningThreshold, 40);
    assert.equal(criticalThreshold, 20);
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// Unit: readCtxMetrics
// ===========================================================================

test('readCtxMetrics: returns null for absent file', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    assert.equal(readCtxMetrics(tmpDir), null);
  } finally {
    cleanup(tmpDir);
  }
});

test('readCtxMetrics: returns null for malformed JSON', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    fs.writeFileSync(path.join(tmpDir, CTX_METRICS_FILENAME), '{ bad json }', 'utf8');
    assert.equal(readCtxMetrics(tmpDir), null);
  } finally {
    cleanup(tmpDir);
  }
});

test('readCtxMetrics: returns null when percentage_remaining missing', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    fs.writeFileSync(path.join(tmpDir, CTX_METRICS_FILENAME), '{"tool_use_count": 5}', 'utf8');
    assert.equal(readCtxMetrics(tmpDir), null);
  } finally {
    cleanup(tmpDir);
  }
});

test('readCtxMetrics: returns metrics for valid file', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    const metrics = { percentage_remaining: 30, tool_use_count: 7, timestamp: '2026-01-01T00:00:00Z' };
    fs.writeFileSync(path.join(tmpDir, CTX_METRICS_FILENAME), JSON.stringify(metrics), 'utf8');
    const result = readCtxMetrics(tmpDir);
    assert.equal(result.percentage_remaining, 30);
    assert.equal(result.tool_use_count, 7);
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// Unit: readDebounceState / writeDebounceState
// ===========================================================================

test('readDebounceState: returns defaults when file absent', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    const state = readDebounceState(tmpDir);
    assert.ok(state.last_warning_tool_count < 0, 'Default count should be -Infinity');
    assert.equal(state.last_severity, 'none');
  } finally {
    cleanup(tmpDir);
  }
});

test('readDebounceState: returns defaults for malformed JSON', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    fs.writeFileSync(path.join(tmpDir, DEBOUNCE_FILENAME), '{ bad }', 'utf8');
    const state = readDebounceState(tmpDir);
    assert.ok(state.last_warning_tool_count < 0);
  } finally {
    cleanup(tmpDir);
  }
});

test('writeDebounceState + readDebounceState: round-trip persists state', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    writeDebounceState(tmpDir, { last_warning_tool_count: 42, last_severity: 'critical' });
    const state = readDebounceState(tmpDir);
    assert.equal(state.last_warning_tool_count, 42);
    assert.equal(state.last_severity, 'critical');
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// Unit: findLatestSessionDir
// ===========================================================================

test('findLatestSessionDir: returns null when sessions dir absent', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    assert.equal(findLatestSessionDir(tmpDir), null);
  } finally {
    cleanup(tmpDir);
  }
});

test('findLatestSessionDir: returns null when sessions dir empty', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    fs.mkdirSync(path.join(tmpDir, '.crumbs', 'sessions'), { recursive: true });
    assert.equal(findLatestSessionDir(tmpDir), null);
  } finally {
    cleanup(tmpDir);
  }
});

test('findLatestSessionDir: returns the only session dir', () => {
  const { projectDir, sessionDir } = createProject();
  try {
    const result = findLatestSessionDir(projectDir);
    assert.equal(result, sessionDir);
  } finally {
    cleanup(projectDir);
  }
});

test('findLatestSessionDir: returns most recently modified dir', async () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'ctx-monitor-test-'));
  try {
    const sessionsDir = path.join(tmpDir, '.crumbs', 'sessions');
    fs.mkdirSync(sessionsDir, { recursive: true });

    const dir1 = path.join(sessionsDir, '_session-old');
    const dir2 = path.join(sessionsDir, '_session-new');
    fs.mkdirSync(dir1);

    // Small delay to ensure different mtime
    await new Promise((resolve) => setTimeout(resolve, 10));
    fs.mkdirSync(dir2);

    const result = findLatestSessionDir(tmpDir);
    assert.equal(result, dir2, 'Should return the most recently created/modified session dir');
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// DEBOUNCE_TOOL_COUNT constant
// ===========================================================================

test('DEBOUNCE_TOOL_COUNT is 5', () => {
  assert.equal(DEBOUNCE_TOOL_COUNT, 5);
});
