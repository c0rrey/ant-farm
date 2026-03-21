'use strict';

/**
 * uninstall.test.js — Tests for the uninstall workflow.
 *
 * Tests cover:
 *  - --uninstall with manifest: only manifest-listed files are removed
 *  - --uninstall without manifest: warning printed, no files deleted
 *  - Dry-run uninstall: remove ops recorded, nothing deleted
 *  - Partial uninstall: some manifest files missing from disk
 *  - unregisterMcp: called during uninstall flow
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs/promises');
const os = require('os');
const path = require('path');

const { runUninstall } = require('../lib/uninstall');
const { writeInstalledManifest, readInstalledManifest } = require('../lib/manifest');
const { pathExists } = require('../lib/file-ops');
const { DryRunCollector } = require('../lib/dry-run');
const { registerMcp, unregisterMcp, MCP_SERVER_NAME, MCP_COMMAND, MCP_ARGS } = require('../lib/mcp-registration');

// ---------------------------------------------------------------------------
// Helper: create a temporary directory and clean it up after the test.
// ---------------------------------------------------------------------------
async function withTmpDir(fn) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'ant-farm-uninstall-test-'));
  try {
    await fn(dir);
  } finally {
    await fs.rm(dir, { recursive: true, force: true });
  }
}

// ---------------------------------------------------------------------------
// Helper: set up a fake claudeDir with installed files and a manifest.
// Returns { claudeDir, installedPaths } where installedPaths are relative to claudeDir.
// ---------------------------------------------------------------------------
async function setupInstalledClaudeDir(tmpDir) {
  const claudeDir = path.join(tmpDir, 'claude');
  await fs.mkdir(claudeDir, { recursive: true });

  // Create some installed files
  const relPaths = ['agents/foo.md', 'agents/bar.md'];
  for (const rel of relPaths) {
    const abs = path.join(claudeDir, rel);
    await fs.mkdir(path.dirname(abs), { recursive: true });
    await fs.writeFile(abs, `# ${rel}\n`, 'utf8');
  }

  // Write the manifest (the installer normally does this)
  const installedFiles = relPaths.map(p => ({ dst: p, checksum: 'fakechecksum' }));
  await writeInstalledManifest(claudeDir, '0.1.0', installedFiles);

  return { claudeDir, relPaths };
}

// ===========================================================================
// Test: uninstall with manifest
// ===========================================================================

test('uninstall with manifest: removes all manifest-listed files', async () => {
  await withTmpDir(async (tmpDir) => {
    const { claudeDir, relPaths } = await setupInstalledClaudeDir(tmpDir);

    const result = await runUninstall(claudeDir);

    // All manifest files should be gone
    for (const rel of relPaths) {
      const abs = path.join(claudeDir, rel);
      const exists = await pathExists(abs);
      assert.ok(!exists, `${rel} should be removed after uninstall`);
    }

    // The manifest itself should be removed
    const manifest = await readInstalledManifest(claudeDir);
    assert.equal(manifest, null, 'Installed manifest should be removed after uninstall');

    // Result should list removed files
    assert.equal(result.removed.length, relPaths.length, 'removed array should list all files');
    assert.equal(result.skipped.length, 0, 'No files should be skipped when all are present');
    assert.equal(result.warnings.length, 0, 'No warnings should be issued when uninstall succeeds');
  });
});

test('uninstall with manifest: does not remove files outside the manifest', async () => {
  await withTmpDir(async (tmpDir) => {
    const { claudeDir } = await setupInstalledClaudeDir(tmpDir);

    // Create a file NOT in the manifest
    const extraFile = path.join(claudeDir, 'my-custom-file.md');
    await fs.writeFile(extraFile, '# custom\n', 'utf8');

    await runUninstall(claudeDir);

    // Extra file must still be present
    const exists = await pathExists(extraFile);
    assert.ok(exists, 'Files not listed in the manifest must not be removed during uninstall');
  });
});

// ===========================================================================
// Test: uninstall without manifest
// ===========================================================================

test('uninstall without manifest: returns warning and removes nothing', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    // Place a file that WOULD be removed if there were a manifest
    const someFile = path.join(claudeDir, 'agents', 'foo.md');
    await fs.mkdir(path.dirname(someFile), { recursive: true });
    await fs.writeFile(someFile, '# foo\n', 'utf8');

    const result = await runUninstall(claudeDir);

    // File must be untouched
    const stillExists = await pathExists(someFile);
    assert.ok(stillExists, 'File should not be removed when no manifest exists');

    // Warning should be emitted
    assert.ok(result.warnings.length > 0, 'A warning should be returned when manifest is not found');
    const hasManifestWarning = result.warnings.some(w =>
      w.toLowerCase().includes('manifest') || w.toLowerCase().includes('not found')
    );
    assert.ok(hasManifestWarning, 'Warning message should mention manifest or not found');

    // Nothing removed
    assert.equal(result.removed.length, 0, 'No files should be in removed list when there is no manifest');
  });
});

// ===========================================================================
// Test: dry-run uninstall
// ===========================================================================

test('dry-run uninstall: records remove ops without deleting files', async () => {
  await withTmpDir(async (tmpDir) => {
    const { claudeDir, relPaths } = await setupInstalledClaudeDir(tmpDir);

    const collector = new DryRunCollector();
    const result = await runUninstall(claudeDir, { dryRun: true, collector });

    // All manifest-listed files should still exist on disk
    for (const rel of relPaths) {
      const abs = path.join(claudeDir, rel);
      const exists = await pathExists(abs);
      assert.ok(exists, `${rel} should NOT be deleted during a dry-run uninstall`);
    }

    // Collector should have recorded 'remove' operations
    const removeOps = collector._ops.filter(o => o.op === 'remove');
    // Expects at least one remove per manifest file (manifest itself is also queued for removal)
    assert.ok(removeOps.length >= relPaths.length,
      'Dry-run collector should record a remove op for each manifest-listed file'
    );

    // Result should still list the files in 'removed' (dry-run records intent)
    assert.equal(result.removed.length, relPaths.length,
      'Dry-run result.removed should list the files that would be removed'
    );
  });
});

// ===========================================================================
// Test: partial uninstall (some files already gone from disk)
// ===========================================================================

test('partial uninstall: skips files not on disk, removes those that are', async () => {
  await withTmpDir(async (tmpDir) => {
    const { claudeDir, relPaths } = await setupInstalledClaudeDir(tmpDir);

    // Manually delete one file before running uninstall
    const deletedRel = relPaths[0];
    await fs.unlink(path.join(claudeDir, deletedRel));

    const result = await runUninstall(claudeDir);

    // The manually-deleted file should appear in skipped
    const skippedRelPaths = result.skipped.map(p => path.relative(claudeDir, p));
    assert.ok(
      skippedRelPaths.includes(deletedRel),
      'Pre-deleted file should appear in skipped list'
    );

    // The remaining file should be in removed
    assert.equal(
      result.removed.length,
      relPaths.length - 1,
      'Only files present on disk should appear in removed'
    );
  });
});

// ===========================================================================
// Test: uninstall with a corrupted manifest
// ===========================================================================

test('uninstall with corrupt manifest: rejects with descriptive error', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    // Write a malformed manifest
    const manifestPath = path.join(claudeDir, '.ant-farm-manifest.json');
    await fs.writeFile(manifestPath, 'THIS IS NOT JSON', 'utf8');

    await assert.rejects(
      () => runUninstall(claudeDir),
      /Failed to read install manifest/,
      'runUninstall should reject with a descriptive error on corrupt manifest'
    );
  });
});

// ===========================================================================
// Test: unregisterMcp called during uninstall flow
// ===========================================================================

test('uninstall flow: unregisterMcp removes mcpServers.crumb entry from settings.json', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // First, register the MCP entry as the installer would
    await registerMcp({ dryRun: false, collector: null, settingsPath });

    // Verify it was written
    const before = JSON.parse(await fs.readFile(settingsPath, 'utf8'));
    assert.ok(before.mcpServers[MCP_SERVER_NAME], 'crumb entry should be present before unregister');

    // Now unregister, as the uninstaller would
    const { warnings } = await unregisterMcp({ dryRun: false, collector: null, settingsPath });

    assert.deepEqual(warnings, [], 'No warnings should be returned on clean unregister');

    // crumb entry should be gone
    const after = JSON.parse(await fs.readFile(settingsPath, 'utf8'));
    assert.ok(
      !after.mcpServers || !after.mcpServers[MCP_SERVER_NAME],
      'mcpServers.crumb entry should be absent after unregisterMcp'
    );
  });
});

test('uninstall flow: unregisterMcp is a no-op when crumb entry is absent', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // settings.json absent — should not throw
    await assert.doesNotReject(
      () => unregisterMcp({ dryRun: false, collector: null, settingsPath }),
      'unregisterMcp should not throw when settings.json does not exist'
    );
  });
});

test('uninstall flow: unregisterMcp preserves other mcpServers entries', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // Pre-populate settings.json with both the crumb entry and a user entry
    const initial = {
      mcpServers: {
        [MCP_SERVER_NAME]: { command: MCP_COMMAND, args: MCP_ARGS },
        'my-other-server': { command: 'node', args: ['other.js'] },
      },
    };
    await fs.writeFile(settingsPath, JSON.stringify(initial, null, 2) + '\n', 'utf8');

    await unregisterMcp({ dryRun: false, collector: null, settingsPath });

    const raw = await fs.readFile(settingsPath, 'utf8');
    const settings = JSON.parse(raw);

    // crumb entry should be gone
    assert.ok(
      !settings.mcpServers || !settings.mcpServers[MCP_SERVER_NAME],
      'mcpServers.crumb should be removed after unregisterMcp'
    );

    // User-owned entry must be preserved
    assert.ok(
      settings.mcpServers && settings.mcpServers['my-other-server'],
      'User-owned mcpServers entry must be preserved after unregisterMcp'
    );
  });
});

test('uninstall flow: unregisterMcp dry-run does not delete settings entry', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // Register the entry first
    await registerMcp({ dryRun: false, collector: null, settingsPath });

    const collector = new DryRunCollector();
    await unregisterMcp({ dryRun: true, collector, settingsPath });

    // Entry must still be present — dry-run writes nothing
    const raw = await fs.readFile(settingsPath, 'utf8');
    const settings = JSON.parse(raw);
    assert.ok(
      settings.mcpServers && settings.mcpServers[MCP_SERVER_NAME],
      'mcpServers.crumb entry must remain after dry-run unregisterMcp'
    );

    // Collector should have recorded an update op
    const updateOps = collector._ops.filter(o => o.op === 'update');
    assert.ok(updateOps.length > 0, 'Dry-run collector should record an update op');
  });
});
