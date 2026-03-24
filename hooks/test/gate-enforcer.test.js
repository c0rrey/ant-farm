'use strict';

/**
 * gate-enforcer.test.js — Tests for ant-farm-gate-enforcer.js PreToolUse hook.
 *
 * Tests cover:
 *   handler — tool bypass (TeamCreate, SendMessage)
 *   handler — silent no-op when no session detected
 *   handler — blocks when startup-check gate not passed
 *   handler — allows when startup-check gate has passed
 *   handler — bypass_gates=true allows spawn with no block
 *   handler — bypass_gates read failure does not bypass
 *   handler — SESSION_DIR env var fast-path (valid path)
 *   handler — SESSION_DIR env var non-existent path falls through to path-scan
 *   handler — returns { continue: false } with Gate blocked reason
 *   handler — empty input is silent no-op
 *   extractSessionDirFromText — finds session dir from inline text
 *   extractSessionDirFromText — returns null when marker absent
 *   extractSessionDirFromText — handles quoted paths
 *   extractSessionDirFromText — handles paths with preceding text
 *   detectSessionDir — env var takes priority over path-scan
 *   detectSessionDir — falls through to path-scan when env var absent
 *   isBypassEnabled — returns true when bypass_gates is true
 *   isBypassEnabled — returns false when bypass_gates is false
 *   isBypassEnabled — returns false when config absent
 *   isBypassEnabled — returns false on malformed JSON
 */

const { test, afterEach, before } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
  handler,
  detectSessionDir,
  extractSessionDirFromText,
  isBypassEnabled,
  extractTaskIdFromPrompt,
  checkStuckAgents,
  RETRY_FAILURE_TYPE,
  SESSION_PATH_MARKER,
  PREDECESSOR_GATE,
} = require('../ant-farm-gate-enforcer');

const { writeGateVerdict, GATE_STATUS_FILENAME, readGateStatus, appendAgentSpawn, readAgentSpawns } = require('../lib/gate-manager');
const { recordRetry } = require('../lib/retry-tracker');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Creates a temporary session directory with optional gate-status.json.
 *
 * @param {object} [gateEntries]  Map of gate-name → verdict ('PASS'|'FAIL') to pre-write.
 * @returns {{ sessionDir: string, projectDir: string }}
 */
function createSessionDir(gateEntries) {
  const projectDir = fs.mkdtempSync(path.join(os.tmpdir(), 'gate-enforcer-test-'));
  // Session dirs live under .crumbs/sessions/_session-<id>
  const crumbsDir = path.join(projectDir, '.crumbs', 'sessions');
  fs.mkdirSync(crumbsDir, { recursive: true });
  const sessionDir = fs.mkdtempSync(path.join(crumbsDir, '_session-'));

  if (gateEntries) {
    for (const [gateName, verdict] of Object.entries(gateEntries)) {
      writeGateVerdict(sessionDir, gateName, verdict);
    }
  }

  return { sessionDir, projectDir };
}

/**
 * Creates .crumbs/config.json in the given project directory.
 *
 * @param {string} projectDir  Absolute path to the project root.
 * @param {object} config      Config object to write.
 */
function writeConfig(projectDir, config) {
  const crumbsDir = path.join(projectDir, '.crumbs');
  fs.mkdirSync(crumbsDir, { recursive: true });
  fs.writeFileSync(path.join(crumbsDir, 'config.json'), JSON.stringify(config), 'utf8');
}

function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

/**
 * Builds a minimal Task PreToolUse input with a prompt containing the sessionDir path.
 *
 * @param {string} projectDir
 * @param {string} sessionDir
 * @returns {object}
 */
function makeTaskInput(projectDir, sessionDir) {
  return {
    tool_name: 'Task',
    workspace: { project_dir: projectDir },
    tool_input: {
      prompt: `Run the implementer agent. Session: ${sessionDir}/task-123.md`,
    },
  };
}

// ---------------------------------------------------------------------------
// Save and restore SESSION_DIR env var between tests that manipulate it.
// ---------------------------------------------------------------------------

let _savedSessionDir;

function saveEnv() {
  _savedSessionDir = process.env.SESSION_DIR;
  delete process.env.SESSION_DIR;
}

function restoreEnv() {
  if (_savedSessionDir !== undefined) {
    process.env.SESSION_DIR = _savedSessionDir;
  } else {
    delete process.env.SESSION_DIR;
  }
}

// ===========================================================================
// Tool bypass
// ===========================================================================

test('handler: TeamCreate bypasses gate check — returns empty string', async () => {
  const { projectDir, sessionDir } = createSessionDir(); // no gates written
  try {
    const input = {
      tool_name: 'TeamCreate',
      workspace: { project_dir: projectDir },
      tool_input: { prompt: `Session: ${sessionDir}/task.md` },
    };
    const result = await handler(input);
    assert.equal(result, '', 'TeamCreate must bypass gate check and return silent');
  } finally {
    cleanup(projectDir);
  }
});

test('handler: SendMessage bypasses gate check — returns empty string', async () => {
  const { projectDir, sessionDir } = createSessionDir(); // no gates written
  try {
    const input = {
      tool_name: 'SendMessage',
      workspace: { project_dir: projectDir },
      tool_input: { prompt: `Session: ${sessionDir}/task.md` },
    };
    const result = await handler(input);
    assert.equal(result, '', 'SendMessage must bypass gate check and return silent');
  } finally {
    cleanup(projectDir);
  }
});

// ===========================================================================
// Session detection — no session
// ===========================================================================

test('handler: no session detected — returns empty string (silent no-op)', async () => {
  saveEnv();
  try {
    const input = {
      tool_name: 'Task',
      workspace: { project_dir: '/tmp' },
      tool_input: { prompt: 'Run the agent with no crumbs path here.' },
    };
    const result = await handler(input);
    assert.equal(result, '', 'Missing session must produce no output');
  } finally {
    restoreEnv();
  }
});

test('handler: empty input object — returns empty string (silent no-op)', async () => {
  saveEnv();
  try {
    const result = await handler({});
    assert.equal(result, '', 'Empty input must produce no output');
  } finally {
    restoreEnv();
  }
});

// ===========================================================================
// Gate blocking — startup-check not passed
// ===========================================================================

test('handler: blocks spawn when startup-check has not been written', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir(); // no gate entries
  try {
    const input = makeTaskInput(projectDir, sessionDir);
    const result = await handler(input);

    assert.ok(result !== '', 'Should return a block response');
    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, false, 'Must block with continue: false');
    assert.ok(typeof parsed.reason === 'string', 'Must include a reason');
    assert.ok(parsed.reason.startsWith('Gate blocked:'), 'Reason must start with "Gate blocked:"');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

test('handler: blocks spawn when startup-check verdict is FAIL', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'FAIL' });
  try {
    const input = makeTaskInput(projectDir, sessionDir);
    const result = await handler(input);

    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, false, 'FAIL verdict must block with continue: false');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

test('handler: block reason includes gate name and session path', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir();
  try {
    const input = makeTaskInput(projectDir, sessionDir);
    const result = await handler(input);
    const parsed = JSON.parse(result);

    assert.ok(parsed.reason.includes(PREDECESSOR_GATE), 'Reason must include predecessor gate name');
    assert.ok(parsed.reason.includes(sessionDir), 'Reason must include session directory path');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

// ===========================================================================
// Gate passing — startup-check passed
// ===========================================================================

test('handler: allows spawn when startup-check has PASS verdict', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });
  try {
    const input = makeTaskInput(projectDir, sessionDir);
    const result = await handler(input);
    assert.equal(result, '', 'Passed gate must produce silent allow');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

// ===========================================================================
// bypass_gates config
// ===========================================================================

test('handler: bypass_gates=true allows spawn without checking gate', async () => {
  saveEnv();
  // No gate written — would normally block.
  const { projectDir, sessionDir } = createSessionDir();
  writeConfig(projectDir, { bypass_gates: true });
  try {
    const input = makeTaskInput(projectDir, sessionDir);
    const result = await handler(input);
    assert.equal(result, '', 'bypass_gates=true must allow spawn silently');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

test('handler: bypass_gates=false does not bypass — still enforces gate', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir(); // no gates — would block
  writeConfig(projectDir, { bypass_gates: false });
  try {
    const input = makeTaskInput(projectDir, sessionDir);
    const result = await handler(input);

    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, false, 'bypass_gates=false must not bypass gate check');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

test('handler: absent config does not bypass — gate still enforced', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir(); // no gates written, no config
  try {
    const input = makeTaskInput(projectDir, sessionDir);
    const result = await handler(input);
    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, false, 'Absent config must not bypass gate enforcement');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

// ===========================================================================
// SESSION_DIR env var fast-path
// ===========================================================================

test('handler: SESSION_DIR env var used as fast-path when path exists', async () => {
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });
  const oldVal = process.env.SESSION_DIR;
  process.env.SESSION_DIR = sessionDir;
  try {
    // Prompt does NOT contain session path — env var is the only detection source.
    const input = {
      tool_name: 'Task',
      workspace: { project_dir: projectDir },
      tool_input: { prompt: 'Run the agent with no crumbs path.' },
    };
    const result = await handler(input);
    assert.equal(result, '', 'SESSION_DIR fast-path with passing gate must allow silently');
  } finally {
    if (oldVal !== undefined) {
      process.env.SESSION_DIR = oldVal;
    } else {
      delete process.env.SESSION_DIR;
    }
    cleanup(projectDir);
  }
});

test('handler: SESSION_DIR set to non-existent path falls through to path-scan', async () => {
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });
  const oldVal = process.env.SESSION_DIR;
  process.env.SESSION_DIR = '/nonexistent/session/path';
  try {
    // Prompt DOES contain session path — path-scan picks it up after env fallthrough.
    const input = makeTaskInput(projectDir, sessionDir);
    const result = await handler(input);
    assert.equal(result, '', 'Fallthrough to path-scan should find session and allow when gate passed');
  } finally {
    if (oldVal !== undefined) {
      process.env.SESSION_DIR = oldVal;
    } else {
      delete process.env.SESSION_DIR;
    }
    cleanup(projectDir);
  }
});

// ===========================================================================
// extractSessionDirFromText unit tests
// ===========================================================================

test('extractSessionDirFromText: returns null when no marker in text', () => {
  assert.equal(
    extractSessionDirFromText('Run the agent with no paths here.'),
    null,
    'No marker means null'
  );
});

test('extractSessionDirFromText: returns null for non-string input', () => {
  assert.equal(extractSessionDirFromText(null), null);
  assert.equal(extractSessionDirFromText(undefined), null);
  assert.equal(extractSessionDirFromText(42), null);
});

test('extractSessionDirFromText: extracts session dir from absolute path in text', () => {
  const sessionDir = '/home/user/project/.crumbs/sessions/_session-abc123';
  const text = `Step 0: Read context from ${sessionDir}/prompts/task.md`;
  const result = extractSessionDirFromText(text);
  assert.equal(result, sessionDir, 'Should extract up to end of session-id token');
});

test('extractSessionDirFromText: extracts session dir from path at start of line', () => {
  const sessionDir = '/tmp/project/.crumbs/sessions/_session-xyz-456';
  const text = `${sessionDir}/task.md is the file to read`;
  const result = extractSessionDirFromText(text);
  assert.equal(result, sessionDir, 'Should extract session dir from line start');
});

test('extractSessionDirFromText: handles quoted path', () => {
  const sessionDir = '/tmp/.crumbs/sessions/_session-q789';
  const text = `prompt: "${sessionDir}/prompts/task.md"`;
  const result = extractSessionDirFromText(text);
  assert.equal(result, sessionDir, 'Should handle quoted paths by stopping at opening quote');
});

test('extractSessionDirFromText: marker present but empty session-id returns something', () => {
  // Edge case: marker with no session-id following. Returns the marker path as-is.
  const text = '/project/.crumbs/sessions/_session-';
  const result = extractSessionDirFromText(text);
  // Should return the full string since marker is present (empty session-id allowed).
  assert.equal(typeof result, 'string', 'Should return a string even for empty session-id');
});

// ===========================================================================
// isBypassEnabled unit tests
// ===========================================================================

test('isBypassEnabled: returns true when bypass_gates is true', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'bypass-test-'));
  try {
    writeConfig(tmpDir, { bypass_gates: true });
    assert.equal(isBypassEnabled(tmpDir), true, 'bypass_gates: true must return true');
  } finally {
    cleanup(tmpDir);
  }
});

test('isBypassEnabled: returns false when bypass_gates is false', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'bypass-test-'));
  try {
    writeConfig(tmpDir, { bypass_gates: false });
    assert.equal(isBypassEnabled(tmpDir), false, 'bypass_gates: false must return false');
  } finally {
    cleanup(tmpDir);
  }
});

test('isBypassEnabled: returns false when config.json is absent', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'bypass-test-'));
  try {
    assert.equal(isBypassEnabled(tmpDir), false, 'Absent config must return false');
  } finally {
    cleanup(tmpDir);
  }
});

test('isBypassEnabled: returns false on malformed JSON', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'bypass-test-'));
  try {
    const crumbsDir = path.join(tmpDir, '.crumbs');
    fs.mkdirSync(crumbsDir);
    fs.writeFileSync(path.join(crumbsDir, 'config.json'), '{not: json}', 'utf8');
    assert.equal(isBypassEnabled(tmpDir), false, 'Malformed JSON must return false');
  } finally {
    cleanup(tmpDir);
  }
});

test('isBypassEnabled: returns false when bypass_gates field absent', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'bypass-test-'));
  try {
    writeConfig(tmpDir, { other_field: true });
    assert.equal(isBypassEnabled(tmpDir), false, 'Missing bypass_gates field must return false');
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// detectSessionDir unit tests
// ===========================================================================

test('detectSessionDir: returns null when prompt has no session path and env absent', () => {
  saveEnv();
  try {
    const input = {
      tool_name: 'Task',
      tool_input: { prompt: 'Run an agent with nothing crumbs-related.' },
    };
    assert.equal(detectSessionDir(input), null, 'No session in prompt or env must return null');
  } finally {
    restoreEnv();
  }
});

test('detectSessionDir: returns path from prompt scan when env var absent', () => {
  saveEnv();
  const sessionPath = '/tmp/project/.crumbs/sessions/_session-scan42';
  try {
    const input = {
      tool_name: 'Task',
      tool_input: { prompt: `Step 0: ${sessionPath}/task.md` },
    };
    const result = detectSessionDir(input);
    assert.equal(result, sessionPath, 'Path-scan should return extracted session dir');
  } finally {
    restoreEnv();
  }
});

test('detectSessionDir: returns null when tool_input has no prompt', () => {
  saveEnv();
  try {
    const input = { tool_name: 'Task', tool_input: {} };
    assert.equal(detectSessionDir(input), null, 'Missing prompt must return null');
  } finally {
    restoreEnv();
  }
});

// ===========================================================================
// extractTaskIdFromPrompt unit tests
// ===========================================================================

test('extractTaskIdFromPrompt: extracts AF-NNN task ID from prompt', () => {
  assert.equal(
    extractTaskIdFromPrompt('Execute task for AF-466. Step 0: Read context.'),
    'AF-466',
    'Should extract AF-NNN id'
  );
});

test('extractTaskIdFromPrompt: extracts first task ID when multiple present', () => {
  assert.equal(
    extractTaskIdFromPrompt('Task AF-100 depends on AF-99.'),
    'AF-100',
    'Should return first match'
  );
});

test('extractTaskIdFromPrompt: returns "unknown" when no task ID in prompt', () => {
  assert.equal(
    extractTaskIdFromPrompt('Run the agent with no task ID here.'),
    'unknown',
    'No task ID should return "unknown"'
  );
});

test('extractTaskIdFromPrompt: returns "unknown" for non-string input', () => {
  assert.equal(extractTaskIdFromPrompt(null), 'unknown');
  assert.equal(extractTaskIdFromPrompt(undefined), 'unknown');
  assert.equal(extractTaskIdFromPrompt(42), 'unknown');
});

// ===========================================================================
// Integration: retry limit blocking (AC-1, AC-5)
// ===========================================================================

test('handler: blocks spawn when checkpoint retry limit exceeded (3 attempts, limit 2)', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });
  // Pre-populate retries.json with 2 checkpoint entries for AF-466.
  // canRetry() limit for 'checkpoint' is 2, so 2 existing entries → not allowed.
  recordRetry(sessionDir, 'checkpoint', 'AF-466');
  recordRetry(sessionDir, 'checkpoint', 'AF-466');
  try {
    const input = {
      tool_name: 'Task',
      workspace: { project_dir: projectDir },
      tool_input: {
        prompt: `Execute task for AF-466. Session: ${sessionDir}/task-466.md`,
      },
    };
    const result = await handler(input);

    assert.ok(result !== '', 'Should return a block response when retry limit exceeded');
    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, false, 'Must block with continue: false');
    assert.ok(typeof parsed.reason === 'string', 'Must include a reason string');
    assert.ok(
      parsed.reason.includes('Retry limit exceeded'),
      `Reason must mention retry limit; got: "${parsed.reason}"`
    );
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

test('handler: allows spawn when below checkpoint retry limit (1 attempt, limit 2)', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });
  // 1 existing retry — still under the limit of 2.
  recordRetry(sessionDir, 'checkpoint', 'AF-42');
  try {
    const input = {
      tool_name: 'Task',
      workspace: { project_dir: projectDir },
      tool_input: {
        prompt: `Execute task for AF-42. Session: ${sessionDir}/task-42.md`,
      },
    };
    const result = await handler(input);
    assert.equal(result, '', 'Should allow spawn when retry count is under the limit');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

// ===========================================================================
// Integration: position mismatch blocking (AC-2, AC-6)
// ===========================================================================

test('handler: blocks spawn when position check mismatches expected next step', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });

  // Write a progress.log with next_step=pre-spawn-check.
  const progressLog = path.join(sessionDir, 'progress.log');
  fs.writeFileSync(
    progressLog,
    '2026-01-01T00:00:00Z|WAVE_SPAWNED|wave=1|next_step=pre-spawn-check\n',
    'utf8'
  );

  try {
    const input = {
      tool_name: 'Task',
      workspace: { project_dir: projectDir },
      tool_input: {
        // Prompt mentions 'scope-verify' but expected is 'pre-spawn-check'.
        prompt: `Run scope-verify agent. Session: ${sessionDir}/task.md`,
      },
    };
    const result = await handler(input);

    assert.ok(result !== '', 'Should return a block response on position mismatch');
    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, false, 'Must block with continue: false');
    assert.ok(typeof parsed.reason === 'string', 'Must include a reason string');
    assert.ok(
      parsed.reason.includes('Position check failed'),
      `Reason must mention position check; got: "${parsed.reason}"`
    );
    assert.ok(
      parsed.reason.includes('pre-spawn-check'),
      `Reason must include expected step; got: "${parsed.reason}"`
    );
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

test('handler: allows spawn when position matches expected next step', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });

  // Write a progress.log with next_step=scope-verify.
  const progressLog = path.join(sessionDir, 'progress.log');
  fs.writeFileSync(
    progressLog,
    '2026-01-01T00:00:00Z|WAVE_VERIFIED|wave=1|next_step=scope-verify\n',
    'utf8'
  );

  try {
    const input = {
      tool_name: 'Task',
      workspace: { project_dir: projectDir },
      tool_input: {
        // Prompt mentions 'scope-verify' which matches the expected step.
        prompt: `Run scope-verify agent. Session: ${sessionDir}/task.md`,
      },
    };
    const result = await handler(input);
    assert.equal(result, '', 'Should allow spawn when position matches expected next step');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

// ===========================================================================
// Integration: agent-spawn timestamp recorded in gate-status.json (AC-3)
// ===========================================================================

test('handler: records agent-spawn timestamp in gate-status.json when spawn allowed', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });
  try {
    const input = makeTaskInput(projectDir, sessionDir);
    const before = Date.now();
    const result = await handler(input);
    const after = Date.now();

    assert.equal(result, '', 'Gate-passed spawn must be silent');

    const status = readGateStatus(sessionDir);
    assert.ok(status !== null, 'gate-status.json must be readable after spawn');
    assert.ok(
      status.gates['agent-spawn'] !== undefined,
      'gate-status.json must contain an agent-spawn entry'
    );
    assert.equal(
      status.gates['agent-spawn'].verdict,
      'PASS',
      'agent-spawn verdict must be PASS'
    );

    const spawnTs = new Date(status.gates['agent-spawn'].timestamp).getTime();
    assert.ok(spawnTs >= before && spawnTs <= after, 'agent-spawn timestamp must be within test window');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

// ===========================================================================
// Integration: agent spawn record accumulation in agents.json (AC-15.1)
// ===========================================================================

test('handler: records agent spawn in agents.json when spawn is allowed', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });
  try {
    const input = makeTaskInput(projectDir, sessionDir);
    const before = Date.now();
    await handler(input);
    const after = Date.now();

    const spawns = readAgentSpawns(sessionDir);
    assert.ok(Array.isArray(spawns), 'agents.json must be an array');
    assert.equal(spawns.length, 1, 'one spawn record must be written');
    assert.ok(typeof spawns[0].task_id === 'string', 'spawn record must have task_id');
    assert.ok(typeof spawns[0].spawned_at === 'string', 'spawn record must have spawned_at');

    const spawnTs = new Date(spawns[0].spawned_at).getTime();
    assert.ok(spawnTs >= before && spawnTs <= after, 'spawned_at must be within test window');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

test('handler: accumulates multiple agent spawns in agents.json', async () => {
  saveEnv();
  const { projectDir, sessionDir } = createSessionDir({ 'startup-check': 'PASS' });
  try {
    // First spawn
    await handler(makeTaskInput(projectDir, sessionDir));
    // Second spawn (different task ID)
    const input2 = {
      tool_name: 'Task',
      workspace: { project_dir: projectDir },
      tool_input: { prompt: `Run task AF-200. Session: ${sessionDir}/task-200.md` },
    };
    await handler(input2);

    const spawns = readAgentSpawns(sessionDir);
    assert.equal(spawns.length, 2, 'Both spawn records must be accumulated in agents.json');
  } finally {
    cleanup(projectDir);
    restoreEnv();
  }
});

// ===========================================================================
// Unit: appendAgentSpawn / readAgentSpawns in gate-manager (AC-15.1)
// ===========================================================================

test('appendAgentSpawn: creates agents.json on first call', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'spawn-test-'));
  try {
    appendAgentSpawn(tmpDir, { task_id: 'AF-1', spawned_at: new Date().toISOString() });
    const spawns = readAgentSpawns(tmpDir);
    assert.equal(spawns.length, 1, 'First append creates file with one entry');
  } finally {
    cleanup(tmpDir);
  }
});

test('appendAgentSpawn: accumulates entries without overwriting', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'spawn-test-'));
  try {
    appendAgentSpawn(tmpDir, { task_id: 'AF-1', spawned_at: new Date().toISOString() });
    appendAgentSpawn(tmpDir, { task_id: 'AF-2', spawned_at: new Date().toISOString() });
    const spawns = readAgentSpawns(tmpDir);
    assert.equal(spawns.length, 2, 'Both entries must be present');
    assert.equal(spawns[0].task_id, 'AF-1');
    assert.equal(spawns[1].task_id, 'AF-2');
  } finally {
    cleanup(tmpDir);
  }
});

test('readAgentSpawns: returns empty array when agents.json absent', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'spawn-test-'));
  try {
    const result = readAgentSpawns(tmpDir);
    assert.deepEqual(result, [], 'Missing file returns empty array');
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// Unit: checkStuckAgents (AC-15.2, AC-15.3, AC-15.4)
// ===========================================================================

test('checkStuckAgents: returns null when no agents have been spawned', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stuck-test-'));
  try {
    const result = checkStuckAgents(tmpDir, tmpDir);
    assert.equal(result, null, 'No spawns means no stuck agent advisory');
  } finally {
    cleanup(tmpDir);
  }
});

test('checkStuckAgents: returns null when agent was spawned recently (under timeout)', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stuck-test-'));
  try {
    // Spawn recorded 1 minute ago — well under 10 min default
    const recentTs = new Date(Date.now() - 60 * 1000).toISOString();
    appendAgentSpawn(tmpDir, { task_id: 'AF-1', spawned_at: recentTs });

    const result = checkStuckAgents(tmpDir, tmpDir);
    assert.equal(result, null, 'Recently spawned agent should not trigger advisory');
  } finally {
    cleanup(tmpDir);
  }
});

test('checkStuckAgents: returns WARNING when agent exceeds timeout (default 10 min)', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stuck-test-'));
  try {
    // Spawn recorded 11 minutes ago — over default 10 min timeout
    const oldTs = new Date(Date.now() - 11 * 60 * 1000).toISOString();
    appendAgentSpawn(tmpDir, { task_id: 'AF-1', spawned_at: oldTs });

    const result = checkStuckAgents(tmpDir, tmpDir);
    assert.ok(result !== null, 'Should return advisory when agent exceeds timeout');
    assert.ok(typeof result === 'string', 'Advisory must be a string');
    assert.ok(result.toUpperCase().includes('WARNING'), 'Advisory must include WARNING for first timeout');
  } finally {
    cleanup(tmpDir);
  }
});

test('checkStuckAgents: returns CRITICAL when agent exceeds escalation threshold (default 15 min)', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'stuck-test-'));
  try {
    // Spawn recorded 16 minutes ago — over default 15 min escalation
    const oldTs = new Date(Date.now() - 16 * 60 * 1000).toISOString();
    appendAgentSpawn(tmpDir, { task_id: 'AF-1', spawned_at: oldTs });

    const result = checkStuckAgents(tmpDir, tmpDir);
    assert.ok(result !== null, 'Should return advisory when agent exceeds escalation timeout');
    assert.ok(result.toUpperCase().includes('CRITICAL'), 'Advisory must include CRITICAL for escalation');
  } finally {
    cleanup(tmpDir);
  }
});
