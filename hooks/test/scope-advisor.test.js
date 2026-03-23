'use strict';

/**
 * scope-advisor.test.js — Tests for enforcing mode in ant-farm-scope-advisor.js.
 *
 * Tests cover:
 *   - Advisory mode (default): out-of-scope write returns { continue: true }
 *   - Advisory mode explicit: out-of-scope write returns { continue: true }
 *   - Advisory mode: in-scope write returns empty string (silent)
 *   - Enforcing mode: out-of-scope write returns { continue: false, reason: 'BLOCKED: ...' }
 *   - Enforcing mode: in-scope write returns empty string (silent)
 *   - Enforcing mode: permitted_exceptions file returns empty string (silent)
 *   - Enforcing mode: permitted_exceptions with :line-range suffix is still matched
 *   - No sidecar: returns empty string (silently inactive)
 *   - No target path: returns empty string (silent no-op)
 *   - isPermittedException: correctly identifies exception paths
 *   - isPermittedException: returns false for non-exception paths
 *   - Enforcing mode: blocked reason includes file name and crumb_id
 *   - Advisory mode is default when mode field is absent
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { handler, extractTargetPath, isPermittedException, ADVISORY_MESSAGE } = require('../ant-farm-scope-advisor');
const { SCOPE_SIDECAR_FILENAME } = require('../lib/scope-reader');

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Creates a tmp dir with a .ant-farm-scope.json and returns the dir path.
 * Callers are responsible for cleanup.
 */
function createSidecar(data) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scope-advisor-test-'));
  const sidecarPath = path.join(tmpDir, SCOPE_SIDECAR_FILENAME);
  fs.writeFileSync(sidecarPath, JSON.stringify(data), 'utf8');
  return tmpDir;
}

function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

/**
 * Builds a minimal PreToolUse input object for the handler.
 */
function makeInput(projectDir, targetFile) {
  return {
    workspace: { project_dir: projectDir },
    tool_input: { path: targetFile },
  };
}

// ===========================================================================
// Advisory mode (default and explicit)
// ===========================================================================

test('handler: advisory mode (absent) — out-of-scope write returns { continue: true }', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-1',
    allowed_files: ['src/foo.js'],
  });
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'src/bar.js'));
    const result = await handler(input);

    assert.ok(result !== '', 'Should return a non-empty advisory response');
    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, true, 'Advisory mode must return continue: true');
    assert.ok(typeof parsed.reason === 'string' && parsed.reason.length > 0, 'Should include a reason');
  } finally {
    cleanup(tmpDir);
  }
});

test('handler: advisory mode explicit — out-of-scope write returns { continue: true }', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-1',
    allowed_files: ['src/foo.js'],
    mode: 'advisory',
  });
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'src/bar.js'));
    const result = await handler(input);

    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, true);
    assert.equal(parsed.reason, ADVISORY_MESSAGE);
  } finally {
    cleanup(tmpDir);
  }
});

test('handler: advisory mode — in-scope write returns empty string (silent)', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-1',
    allowed_files: ['src/foo.js'],
    mode: 'advisory',
  });
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'src/foo.js'));
    const result = await handler(input);
    assert.equal(result, '', 'In-scope write should produce no output');
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// Enforcing mode — block behavior
// ===========================================================================

test('handler: enforcing mode — out-of-scope write returns { continue: false }', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-42',
    allowed_files: ['src/foo.js'],
    mode: 'enforcing',
  });
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'src/bar.js'));
    const result = await handler(input);

    assert.ok(result !== '', 'Enforcing mode should return a response for out-of-scope write');
    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, false, 'Enforcing mode must block with continue: false');
    assert.ok(typeof parsed.reason === 'string', 'Should include a reason string');
    assert.ok(parsed.reason.startsWith('BLOCKED:'), 'Reason should start with BLOCKED:');
  } finally {
    cleanup(tmpDir);
  }
});

test('handler: enforcing mode — blocked reason includes crumb_id', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-42',
    allowed_files: ['src/foo.js'],
    mode: 'enforcing',
  });
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'src/bar.js'));
    const result = await handler(input);
    const parsed = JSON.parse(result);

    assert.ok(parsed.reason.includes('AF-42'), 'Blocked reason should include the crumb_id');
  } finally {
    cleanup(tmpDir);
  }
});

test('handler: enforcing mode — in-scope write returns empty string (silent)', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-42',
    allowed_files: ['src/foo.js'],
    mode: 'enforcing',
  });
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'src/foo.js'));
    const result = await handler(input);
    assert.equal(result, '', 'In-scope write in enforcing mode should be silent');
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// Enforcing mode — permitted_exceptions bypass
// ===========================================================================

test('handler: enforcing mode — permitted_exceptions file returns empty string (allowed)', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-42',
    allowed_files: ['src/foo.js'],
    mode: 'enforcing',
    permitted_exceptions: ['CHANGELOG.md'],
  });
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'CHANGELOG.md'));
    const result = await handler(input);
    assert.equal(result, '', 'Permitted exception in enforcing mode should produce no output');
  } finally {
    cleanup(tmpDir);
  }
});

test('handler: enforcing mode — non-exception file is still blocked', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-42',
    allowed_files: ['src/foo.js'],
    mode: 'enforcing',
    permitted_exceptions: ['CHANGELOG.md'],
  });
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'README.md'));
    const result = await handler(input);
    const parsed = JSON.parse(result);
    assert.equal(parsed.continue, false, 'Non-exception path should still be blocked');
  } finally {
    cleanup(tmpDir);
  }
});

test('handler: enforcing mode — permitted_exceptions with :line-range suffix is bypassed', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-42',
    allowed_files: ['src/foo.js'],
    mode: 'enforcing',
    permitted_exceptions: ['CHANGELOG.md:1-10'],
  });
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'CHANGELOG.md'));
    const result = await handler(input);
    assert.equal(result, '', 'permitted_exceptions with :line-range should still match the file');
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// Silent no-op conditions
// ===========================================================================

test('handler: no sidecar — returns empty string (silently inactive)', async () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scope-advisor-test-'));
  try {
    const input = makeInput(tmpDir, path.join(tmpDir, 'any-file.js'));
    const result = await handler(input);
    assert.equal(result, '', 'Missing sidecar should produce no output');
  } finally {
    cleanup(tmpDir);
  }
});

test('handler: no target path in tool_input — returns empty string (silent no-op)', async () => {
  const tmpDir = createSidecar({
    crumb_id: 'AF-1',
    allowed_files: ['src/foo.js'],
    mode: 'enforcing',
  });
  try {
    const input = {
      workspace: { project_dir: tmpDir },
      tool_input: {},
    };
    const result = await handler(input);
    assert.equal(result, '', 'Missing target path should produce no output');
  } finally {
    cleanup(tmpDir);
  }
});

test('handler: empty input object — returns empty string (silent no-op)', async () => {
  const result = await handler({});
  assert.equal(result, '', 'Empty input should produce no output');
});

// ===========================================================================
// isPermittedException unit tests
// ===========================================================================

test('isPermittedException: returns true for a path in permitted_exceptions', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scope-advisor-test-'));
  try {
    const scopeData = {
      crumb_id: 'AF-1',
      allowed_files: ['src/foo.js'],
      mode: 'enforcing',
      permitted_exceptions: ['CHANGELOG.md'],
    };
    const result = isPermittedException(path.join(tmpDir, 'CHANGELOG.md'), scopeData, tmpDir);
    assert.equal(result, true, 'Path in permitted_exceptions should return true');
  } finally {
    cleanup(tmpDir);
  }
});

test('isPermittedException: returns false for a path not in permitted_exceptions', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scope-advisor-test-'));
  try {
    const scopeData = {
      crumb_id: 'AF-1',
      allowed_files: ['src/foo.js'],
      mode: 'enforcing',
      permitted_exceptions: ['CHANGELOG.md'],
    };
    const result = isPermittedException(path.join(tmpDir, 'README.md'), scopeData, tmpDir);
    assert.equal(result, false, 'Path not in permitted_exceptions should return false');
  } finally {
    cleanup(tmpDir);
  }
});

test('isPermittedException: returns true when entry has :line-range suffix', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scope-advisor-test-'));
  try {
    const scopeData = {
      crumb_id: 'AF-1',
      allowed_files: [],
      mode: 'enforcing',
      permitted_exceptions: ['CHANGELOG.md:1-50'],
    };
    const result = isPermittedException(path.join(tmpDir, 'CHANGELOG.md'), scopeData, tmpDir);
    assert.equal(result, true, 'Line-range suffix should be stripped for file-level comparison');
  } finally {
    cleanup(tmpDir);
  }
});

test('isPermittedException: returns false when permitted_exceptions is empty', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scope-advisor-test-'));
  try {
    const scopeData = {
      crumb_id: 'AF-1',
      allowed_files: ['src/foo.js'],
      mode: 'enforcing',
      permitted_exceptions: [],
    };
    const result = isPermittedException(path.join(tmpDir, 'CHANGELOG.md'), scopeData, tmpDir);
    assert.equal(result, false, 'Empty permitted_exceptions should always return false');
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// extractTargetPath (unchanged behavior sanity check)
// ===========================================================================

test('extractTargetPath: returns path from tool_input', () => {
  const input = { tool_input: { path: '/tmp/some-file.js' } };
  assert.equal(extractTargetPath(input), '/tmp/some-file.js');
});

test('extractTargetPath: returns null when tool_input is absent', () => {
  assert.equal(extractTargetPath({}), null);
  assert.equal(extractTargetPath(null), null);
});
