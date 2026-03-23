'use strict';

/**
 * scope-reader.test.js — Tests for scope-reader.js mode and permitted_exceptions parsing.
 *
 * Tests cover:
 *   - readScopeSidecar() returns mode: 'advisory' when field is absent
 *   - readScopeSidecar() returns mode: 'advisory' when field is explicitly 'advisory'
 *   - readScopeSidecar() returns mode: 'enforcing' when field is 'enforcing'
 *   - readScopeSidecar() defaults to 'advisory' for unrecognized mode values
 *   - readScopeSidecar() returns permitted_exceptions: [] when field is absent
 *   - readScopeSidecar() returns parsed permitted_exceptions array
 *   - readScopeSidecar() filters non-string entries from permitted_exceptions
 *   - readScopeSidecar() returns null for missing sidecar file
 *   - readScopeSidecar() returns null for malformed JSON
 *   - readScopeSidecar() returns null when allowed_files is absent
 *   - isFileInScope() still works correctly with updated ScopeData shape
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');

const { readScopeSidecar, isFileInScope, SCOPE_SIDECAR_FILENAME } = require('../scope-reader');

// ---------------------------------------------------------------------------
// Helper: write a temporary .ant-farm-scope.json and return the tmpDir path.
// ---------------------------------------------------------------------------
function withSidecar(data) {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scope-reader-test-'));
  const sidecarPath = path.join(tmpDir, SCOPE_SIDECAR_FILENAME);
  fs.writeFileSync(sidecarPath, JSON.stringify(data), 'utf8');
  return tmpDir;
}

function cleanup(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
}

// ===========================================================================
// mode field parsing
// ===========================================================================

test('readScopeSidecar: returns mode "advisory" when mode field is absent', () => {
  const tmpDir = withSidecar({ crumb_id: 'AF-1', allowed_files: ['foo.js'] });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.ok(result !== null, 'Should return data, not null');
    assert.equal(result.mode, 'advisory', 'Missing mode field should default to advisory');
  } finally {
    cleanup(tmpDir);
  }
});

test('readScopeSidecar: returns mode "advisory" when field is explicitly "advisory"', () => {
  const tmpDir = withSidecar({ crumb_id: 'AF-1', allowed_files: ['foo.js'], mode: 'advisory' });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.ok(result !== null);
    assert.equal(result.mode, 'advisory');
  } finally {
    cleanup(tmpDir);
  }
});

test('readScopeSidecar: returns mode "enforcing" when field is "enforcing"', () => {
  const tmpDir = withSidecar({ crumb_id: 'AF-1', allowed_files: ['foo.js'], mode: 'enforcing' });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.ok(result !== null);
    assert.equal(result.mode, 'enforcing');
  } finally {
    cleanup(tmpDir);
  }
});

test('readScopeSidecar: defaults to "advisory" for unrecognized mode values', () => {
  const tmpDir = withSidecar({ crumb_id: 'AF-1', allowed_files: ['foo.js'], mode: 'strict' });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.ok(result !== null);
    assert.equal(result.mode, 'advisory', 'Unrecognized mode should fall back to advisory');
  } finally {
    cleanup(tmpDir);
  }
});

test('readScopeSidecar: defaults to "advisory" when mode is null', () => {
  const tmpDir = withSidecar({ crumb_id: 'AF-1', allowed_files: ['foo.js'], mode: null });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.ok(result !== null);
    assert.equal(result.mode, 'advisory');
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// permitted_exceptions field parsing
// ===========================================================================

test('readScopeSidecar: returns permitted_exceptions [] when field is absent', () => {
  const tmpDir = withSidecar({ crumb_id: 'AF-1', allowed_files: ['foo.js'] });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.ok(result !== null);
    assert.deepEqual(result.permitted_exceptions, []);
  } finally {
    cleanup(tmpDir);
  }
});

test('readScopeSidecar: returns parsed permitted_exceptions array', () => {
  const tmpDir = withSidecar({
    crumb_id: 'AF-1',
    allowed_files: ['foo.js'],
    permitted_exceptions: ['CHANGELOG.md', 'README.md'],
  });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.ok(result !== null);
    assert.deepEqual(result.permitted_exceptions, ['CHANGELOG.md', 'README.md']);
  } finally {
    cleanup(tmpDir);
  }
});

test('readScopeSidecar: filters non-string entries from permitted_exceptions', () => {
  const tmpDir = withSidecar({
    crumb_id: 'AF-1',
    allowed_files: ['foo.js'],
    permitted_exceptions: ['valid.js', 42, null, 'also-valid.js', true],
  });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.ok(result !== null);
    assert.deepEqual(result.permitted_exceptions, ['valid.js', 'also-valid.js']);
  } finally {
    cleanup(tmpDir);
  }
});

test('readScopeSidecar: returns permitted_exceptions [] when field is not an array', () => {
  const tmpDir = withSidecar({
    crumb_id: 'AF-1',
    allowed_files: ['foo.js'],
    permitted_exceptions: 'CHANGELOG.md',
  });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.ok(result !== null);
    assert.deepEqual(result.permitted_exceptions, []);
  } finally {
    cleanup(tmpDir);
  }
});

// ===========================================================================
// Existing behavior preserved
// ===========================================================================

test('readScopeSidecar: returns null when sidecar file does not exist', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scope-reader-test-'));
  try {
    const result = readScopeSidecar(tmpDir);
    assert.equal(result, null, 'Should return null for missing sidecar');
  } finally {
    cleanup(tmpDir);
  }
});

test('readScopeSidecar: returns null for malformed JSON', () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'scope-reader-test-'));
  const sidecarPath = path.join(tmpDir, SCOPE_SIDECAR_FILENAME);
  fs.writeFileSync(sidecarPath, '{ bad json }', 'utf8');
  try {
    const result = readScopeSidecar(tmpDir);
    assert.equal(result, null, 'Should return null for malformed JSON');
  } finally {
    cleanup(tmpDir);
  }
});

test('readScopeSidecar: returns null when allowed_files is absent', () => {
  const tmpDir = withSidecar({ crumb_id: 'AF-1' });
  try {
    const result = readScopeSidecar(tmpDir);
    assert.equal(result, null, 'Should return null when allowed_files is missing');
  } finally {
    cleanup(tmpDir);
  }
});

test('isFileInScope: still works correctly with the updated ScopeData shape', () => {
  const tmpDir = withSidecar({
    crumb_id: 'AF-1',
    allowed_files: ['src/foo.js'],
    mode: 'enforcing',
    permitted_exceptions: ['CHANGELOG.md'],
  });
  try {
    const scopeData = readScopeSidecar(tmpDir);
    assert.ok(scopeData !== null);

    const inScope = isFileInScope(path.join(tmpDir, 'src/foo.js'), scopeData, tmpDir);
    assert.equal(inScope, true, 'In-scope file should still be recognized');

    const outOfScope = isFileInScope(path.join(tmpDir, 'src/bar.js'), scopeData, tmpDir);
    assert.equal(outOfScope, false, 'Out-of-scope file should still be rejected');
  } finally {
    cleanup(tmpDir);
  }
});
