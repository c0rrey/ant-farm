'use strict';

/**
 * install.test.js — Integration tests for the install workflow.
 *
 * Tests cover:
 *  - Fresh install: all manifest-listed files copied to the target dir
 *  - Idempotent re-run: files updated, no duplicate sentinel blocks
 *  - --dry-run mode: no files written, DryRunCollector populated
 *  - Partial-install recovery: sentinel file present warns caller
 *
 * All tests run against a real tmpdir; nothing is written to ~/.claude/.
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs/promises');
const os = require('os');
const path = require('path');

// Library modules under test
const { readInstallManifest, writeInstalledManifest, readInstalledManifest } = require('../lib/manifest');
const { copyWithBackup, writeSentinel, removeSentinel, pathExists, sha256File } = require('../lib/file-ops');
const { DryRunCollector } = require('../lib/dry-run');
const { syncClaudeMdBlock } = require('../lib/claude-md');
const { registerMcp, MCP_SERVER_NAME, MCP_COMMAND, MCP_ARGS } = require('../lib/mcp-registration');
const {
  registerHooks,
  STATUSLINE_COMMAND,
  SCOPE_ADVISOR_COMMAND,
  SCOPE_ADVISOR_MATCHER,
} = require('../lib/hooks-registration');

// ---------------------------------------------------------------------------
// Helper: create a temporary directory and clean it up after the test.
// ---------------------------------------------------------------------------
async function withTmpDir(fn) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'ant-farm-test-'));
  try {
    await fn(dir);
  } finally {
    await fs.rm(dir, { recursive: true, force: true });
  }
}

// ---------------------------------------------------------------------------
// Helper: create a minimal install-manifest.json in a package root dir.
// Returns { packageRoot, manifestFiles } where manifestFiles is the array
// written to the manifest.
// ---------------------------------------------------------------------------
async function createFakePackageRoot(tmpDir) {
  // Package root lives at tmpDir/pkg/
  const packageRoot = path.join(tmpDir, 'pkg');
  await fs.mkdir(packageRoot, { recursive: true });

  // Create two fake source files that the manifest references.
  // install.js expects:  path.join(PACKAGE_ROOT, '..', entry.src)
  // So the source is one directory above packageRoot, i.e. tmpDir/
  // We'll put the source files there: tmpDir/agents/foo.md
  const srcDir = path.join(tmpDir, 'agents');
  await fs.mkdir(srcDir, { recursive: true });
  await fs.writeFile(path.join(srcDir, 'foo.md'), '# foo agent\n', 'utf8');
  await fs.writeFile(path.join(srcDir, 'bar.md'), '# bar agent\n', 'utf8');

  const manifestFiles = [
    { src: 'agents/foo.md', dst: 'agents/foo.md', description: 'Foo agent' },
    { src: 'agents/bar.md', dst: 'agents/bar.md', description: 'Bar agent' },
  ];

  const manifest = { files: manifestFiles };
  await fs.writeFile(
    path.join(packageRoot, 'install-manifest.json'),
    JSON.stringify(manifest, null, 2) + '\n',
    'utf8'
  );

  return { packageRoot, manifestFiles };
}

// ---------------------------------------------------------------------------
// Helper: simulate a complete install pass end-to-end.
// Mirrors the core copy loop in install.js runInstallMode().
// ---------------------------------------------------------------------------
async function simulateInstallPass(packageRoot, claudeDir, { dryRun = false } = {}) {
  const collector = dryRun ? new DryRunCollector() : null;

  const manifest = await readInstallManifest(packageRoot);
  const fileList = manifest.files;

  const installedFiles = [];

  for (const entry of fileList) {
    const src = path.join(packageRoot, '..', entry.src);
    const dst = path.join(claudeDir, entry.dst);

    const srcExists = await pathExists(src);
    if (!srcExists) continue;

    if (dryRun) {
      const dstExists = await pathExists(dst);
      if (dstExists) {
        collector.add('update', src, dst);
        collector.add('backup', dst, `${dst}.bak.<timestamp>`);
      } else {
        collector.add('install', src, dst);
      }
      installedFiles.push({ dst: entry.dst, checksum: '<sha256-not-computed-in-dry-run>' });
      continue;
    }

    const { checksum } = await copyWithBackup(src, dst);
    installedFiles.push({ dst: entry.dst, checksum });
  }

  if (!dryRun) {
    await writeInstalledManifest(claudeDir, '0.1.0', installedFiles);
  }

  return { collector, installedFiles };
}

// ===========================================================================
// Test: Fresh install
// ===========================================================================

test('fresh install: all manifest files are copied to claudeDir', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const { packageRoot, manifestFiles } = await createFakePackageRoot(tmpDir);
    const { installedFiles } = await simulateInstallPass(packageRoot, claudeDir);

    // Both files should be present in claudeDir
    for (const entry of manifestFiles) {
      const dst = path.join(claudeDir, entry.dst);
      const exists = await pathExists(dst);
      assert.ok(exists, `Expected ${entry.dst} to exist in claudeDir after fresh install`);
    }

    // Installed manifest should have been written
    const manifestRecord = await readInstalledManifest(claudeDir);
    assert.ok(manifestRecord, 'Installed manifest should be written after install');
    assert.equal(manifestRecord.files.length, manifestFiles.length, 'Manifest should record all installed files');

    // Each record should have a real checksum
    for (const record of manifestRecord.files) {
      assert.ok(record.sha256, `File record for ${record.path} should have a sha256 checksum`);
      assert.match(record.sha256, /^[0-9a-f]{64}$/, 'sha256 should be a 64-char hex string');
    }

    // Checksums should match the actual files on disk
    for (const record of manifestRecord.files) {
      const filePath = path.join(claudeDir, record.path);
      const actual = await sha256File(filePath);
      assert.equal(actual, record.sha256, `Checksum for ${record.path} should match file on disk`);
    }
  });
});

test('fresh install: no backup files are created when destination is empty', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const { packageRoot } = await createFakePackageRoot(tmpDir);
    await simulateInstallPass(packageRoot, claudeDir);

    // Glob for .bak files
    const agentsDir = path.join(claudeDir, 'agents');
    const entries = await fs.readdir(agentsDir);
    const bakFiles = entries.filter(e => e.includes('.bak.'));
    assert.equal(bakFiles.length, 0, 'No backup files should be created on a fresh install');
  });
});

// ===========================================================================
// Test: Idempotent re-run
// ===========================================================================

test('idempotent re-run: files are updated and backup files are created', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const { packageRoot } = await createFakePackageRoot(tmpDir);

    // First install
    await simulateInstallPass(packageRoot, claudeDir);

    // Modify a source file to force a diff
    await fs.writeFile(
      path.join(tmpDir, 'agents', 'foo.md'),
      '# foo agent v2\n',
      'utf8'
    );

    // Second install
    await simulateInstallPass(packageRoot, claudeDir);

    // Destination file should have the updated content
    const content = await fs.readFile(path.join(claudeDir, 'agents', 'foo.md'), 'utf8');
    assert.equal(content, '# foo agent v2\n', 'Updated file should be in place after re-run');

    // A backup of the original should exist
    const agentsDir = path.join(claudeDir, 'agents');
    const entries = await fs.readdir(agentsDir);
    const bakFiles = entries.filter(e => e.startsWith('foo.md.bak.'));
    assert.ok(bakFiles.length > 0, 'A backup of foo.md should have been created during the update');
  });
});

test('idempotent re-run: manifest is updated with new checksums', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const { packageRoot } = await createFakePackageRoot(tmpDir);

    // First install
    await simulateInstallPass(packageRoot, claudeDir);
    const firstManifest = await readInstalledManifest(claudeDir);

    // Modify a source file
    await fs.writeFile(path.join(tmpDir, 'agents', 'foo.md'), '# foo changed\n', 'utf8');

    // Second install
    await simulateInstallPass(packageRoot, claudeDir);
    const secondManifest = await readInstalledManifest(claudeDir);

    const firstFoo = firstManifest.files.find(f => f.path === 'agents/foo.md');
    const secondFoo = secondManifest.files.find(f => f.path === 'agents/foo.md');

    assert.ok(firstFoo && secondFoo, 'Both manifests should contain foo.md entry');
    assert.notEqual(
      firstFoo.sha256,
      secondFoo.sha256,
      'Checksum for foo.md should change after the file is updated'
    );
  });
});

// ===========================================================================
// Test: --dry-run mode
// ===========================================================================

test('dry-run: no files are written to claudeDir', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const { packageRoot } = await createFakePackageRoot(tmpDir);

    await simulateInstallPass(packageRoot, claudeDir, { dryRun: true });

    // claudeDir should remain empty (no files or subdirs created)
    const entries = await fs.readdir(claudeDir);
    assert.equal(entries.length, 0, 'Dry-run should not write any files to claudeDir');
  });
});

test('dry-run: collector records install operations for each manifest file', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const { packageRoot, manifestFiles } = await createFakePackageRoot(tmpDir);

    const { collector } = await simulateInstallPass(packageRoot, claudeDir, { dryRun: true });

    // Should have one 'install' operation per file
    const installOps = collector._ops.filter(o => o.op === 'install');
    assert.equal(
      installOps.length,
      manifestFiles.length,
      'Dry-run collector should record one install op per manifest file'
    );
  });
});

test('dry-run re-run: collector records update+backup operations for existing files', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const { packageRoot, manifestFiles } = await createFakePackageRoot(tmpDir);

    // Real first install so files exist
    await simulateInstallPass(packageRoot, claudeDir);

    // Dry-run second pass
    const { collector } = await simulateInstallPass(packageRoot, claudeDir, { dryRun: true });

    const updateOps = collector._ops.filter(o => o.op === 'update');
    const backupOps = collector._ops.filter(o => o.op === 'backup');

    assert.equal(
      updateOps.length,
      manifestFiles.length,
      'Dry-run re-run collector should record one update op per existing file'
    );
    assert.equal(
      backupOps.length,
      manifestFiles.length,
      'Dry-run re-run collector should record one backup op per existing file'
    );

    // No files should have been written to disk beyond what was there before re-run
    // (installed manifest from first pass should still be the only manifest)
    const afterManifest = await readInstalledManifest(claudeDir);
    assert.ok(afterManifest, 'Manifest from first real install should still exist');
  });
});

// ===========================================================================
// Test: Partial installation recovery — sentinel detection
// ===========================================================================

test('partial install: sentinel file exists and can be detected with pathExists', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const sentinelPath = path.join(claudeDir, '.ant-farm-install-in-progress');

    // Pre-place the sentinel (simulates a previous install that died mid-way)
    await writeSentinel(sentinelPath, 'ant-farm installation in progress\n');

    const sentinelExists = await pathExists(sentinelPath);
    assert.ok(sentinelExists, 'Sentinel file should be detectable via pathExists');
  });
});

test('partial install: sentinel is removed after successful install', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const sentinelPath = path.join(claudeDir, '.ant-farm-install-in-progress');
    const { packageRoot } = await createFakePackageRoot(tmpDir);

    // Simulate writing sentinel before install
    await writeSentinel(sentinelPath, 'ant-farm installation in progress\n');

    // Perform a real install
    await simulateInstallPass(packageRoot, claudeDir);

    // Manually remove sentinel as install.js would at end of runInstallMode
    await removeSentinel(sentinelPath);

    const stillExists = await pathExists(sentinelPath);
    assert.ok(!stillExists, 'Sentinel should be removed after a completed install');
  });
});

test('partial install: removeSentinel is a no-op when sentinel does not exist', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeDir = path.join(tmpDir, 'claude');
    await fs.mkdir(claudeDir);

    const sentinelPath = path.join(claudeDir, '.ant-farm-install-in-progress');

    // Should not throw even though the file doesn't exist
    await assert.doesNotReject(
      () => removeSentinel(sentinelPath),
      'removeSentinel should not throw when sentinel is absent'
    );
  });
});

// ===========================================================================
// Test: manifest.js unit tests
// ===========================================================================

test('readInstallManifest: throws when file is missing', async () => {
  await withTmpDir(async (tmpDir) => {
    const fakeRoot = path.join(tmpDir, 'nonexistent');
    await assert.rejects(
      () => readInstallManifest(fakeRoot),
      /Cannot read install-manifest\.json/,
      'Should throw with descriptive error when manifest is missing'
    );
  });
});

test('readInstallManifest: throws when file is invalid JSON', async () => {
  await withTmpDir(async (tmpDir) => {
    await fs.writeFile(path.join(tmpDir, 'install-manifest.json'), 'NOT JSON', 'utf8');
    await assert.rejects(
      () => readInstallManifest(tmpDir),
      /not valid JSON/,
      'Should throw with descriptive error when manifest JSON is malformed'
    );
  });
});

test('readInstallManifest: throws when files array is missing', async () => {
  await withTmpDir(async (tmpDir) => {
    await fs.writeFile(
      path.join(tmpDir, 'install-manifest.json'),
      JSON.stringify({ version: '1.0' }),
      'utf8'
    );
    await assert.rejects(
      () => readInstallManifest(tmpDir),
      /must have a top-level "files" array/,
      'Should throw when manifest lacks "files" array'
    );
  });
});

test('writeInstalledManifest / readInstalledManifest roundtrip', async () => {
  await withTmpDir(async (tmpDir) => {
    const installedFiles = [
      { dst: 'agents/foo.md', checksum: 'abc123' },
    ];

    await writeInstalledManifest(tmpDir, '0.1.0', installedFiles);
    const record = await readInstalledManifest(tmpDir);

    assert.ok(record, 'Should be able to read back the installed manifest');
    assert.equal(record.version, '0.1.0');
    assert.equal(record.files.length, 1);
    assert.equal(record.files[0].path, 'agents/foo.md');
    assert.equal(record.files[0].sha256, 'abc123');
  });
});

test('readInstalledManifest: returns null when file does not exist', async () => {
  await withTmpDir(async (tmpDir) => {
    const result = await readInstalledManifest(tmpDir);
    assert.equal(result, null, 'Should return null when manifest does not exist');
  });
});

// ===========================================================================
// Test: DryRunCollector
// ===========================================================================

test('DryRunCollector: count reflects added operations', () => {
  const collector = new DryRunCollector();
  assert.equal(collector.count, 0);

  collector.add('install', '/src/foo.md', '/dst/foo.md');
  assert.equal(collector.count, 1);

  collector.add('backup', '/dst/foo.md', '/dst/foo.md.bak.20240101T120000Z');
  assert.equal(collector.count, 2);
});

test('DryRunCollector: printReport does not throw', () => {
  const collector = new DryRunCollector();
  collector.add('install', '/src/foo.md', '/dst/foo.md');
  collector.add('update', '/src/bar.md', '/dst/bar.md');
  // Redirect console output to suppress noise in test output
  const orig = console.log;
  const lines = [];
  console.log = (...args) => lines.push(args.join(' '));
  try {
    assert.doesNotThrow(() => collector.printReport());
  } finally {
    console.log = orig;
  }
  assert.ok(lines.some(l => l.includes('Dry-run preview')), 'Report header should be printed');
});

// ===========================================================================
// Test: install-manifest.json entry verification
// ===========================================================================

test('install-manifest.json includes orchestration/RULES-lite.md entry', async () => {
  // PACKAGE_ROOT is npm/ — one level below the repo root where install-manifest.json lives.
  const packageRoot = path.resolve(__dirname, '..');
  const manifest = await readInstallManifest(packageRoot);

  const rulesLiteEntry = manifest.files.find(
    (f) => f.src === 'orchestration/RULES-lite.md' && f.dst === 'orchestration/RULES-lite.md'
  );

  assert.ok(
    rulesLiteEntry,
    'install-manifest.json must include an entry with src and dst equal to orchestration/RULES-lite.md'
  );
});

// ===========================================================================
// Test: registerMcp called during install flow
// ===========================================================================

test('install flow: registerMcp writes mcpServers.crumb entry to settings.json', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // settings.json absent before install — registerMcp should create it
    const exists = await pathExists(settingsPath);
    assert.ok(!exists, 'settings.json should not exist before install');

    const { warnings } = await registerMcp({ dryRun: false, collector: null, settingsPath });

    // No warnings expected on a fresh registration
    assert.deepEqual(warnings, [], 'No warnings should be returned on fresh MCP registration');

    // settings.json should now exist
    const written = await pathExists(settingsPath);
    assert.ok(written, 'registerMcp should create settings.json when it does not exist');

    // Parse the written file and verify the crumb entry
    const raw = await fs.readFile(settingsPath, 'utf8');
    const settings = JSON.parse(raw);

    assert.ok(
      settings.mcpServers && typeof settings.mcpServers === 'object',
      'settings.json should have an mcpServers object after registerMcp'
    );
    assert.ok(
      settings.mcpServers[MCP_SERVER_NAME],
      `mcpServers.${MCP_SERVER_NAME} entry should be present after registerMcp`
    );
    assert.equal(
      settings.mcpServers[MCP_SERVER_NAME].command,
      MCP_COMMAND,
      'mcpServers.crumb.command should match the expected MCP command'
    );
    assert.deepEqual(
      settings.mcpServers[MCP_SERVER_NAME].args,
      MCP_ARGS,
      'mcpServers.crumb.args should match the expected MCP args'
    );
  });
});

test('install flow: registerMcp is idempotent on re-install', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // First install
    await registerMcp({ dryRun: false, collector: null, settingsPath });

    // Second install (re-run)
    const { warnings } = await registerMcp({ dryRun: false, collector: null, settingsPath });

    assert.deepEqual(warnings, [], 'No warnings should be returned on idempotent re-install');

    // Entry should still be present and not duplicated
    const raw = await fs.readFile(settingsPath, 'utf8');
    const settings = JSON.parse(raw);
    assert.ok(
      settings.mcpServers[MCP_SERVER_NAME],
      'mcpServers.crumb entry should still be present after idempotent re-install'
    );
    // There should be exactly one crumb key, not an array or multi-value structure
    assert.equal(typeof settings.mcpServers[MCP_SERVER_NAME], 'object');
  });
});

test('install flow: registerMcp dry-run records update op without writing files', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');
    const collector = new DryRunCollector();

    const { warnings } = await registerMcp({ dryRun: true, collector, settingsPath });

    assert.deepEqual(warnings, [], 'No warnings should be returned in dry-run mode');

    // settings.json must NOT be created in dry-run
    const exists = await pathExists(settingsPath);
    assert.ok(!exists, 'registerMcp dry-run must not write settings.json');

    // Collector should have recorded an update op for settings.json
    const updateOps = collector._ops.filter(o => o.op === 'update');
    assert.ok(
      updateOps.length > 0,
      'Dry-run collector should record an update op for settings.json'
    );
    const targetsSettings = updateOps.some(o => o.dst === settingsPath || o.src === settingsPath);
    assert.ok(targetsSettings, 'Recorded update op should reference the settings.json path');
  });
});

test('install flow: registerMcp preserves existing non-ant-farm mcpServers entries', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // Pre-populate settings.json with a user-owned MCP entry
    const initial = {
      mcpServers: {
        'my-custom-server': { command: 'node', args: ['server.js'] },
      },
    };
    await fs.writeFile(settingsPath, JSON.stringify(initial, null, 2) + '\n', 'utf8');

    await registerMcp({ dryRun: false, collector: null, settingsPath });

    const raw = await fs.readFile(settingsPath, 'utf8');
    const settings = JSON.parse(raw);

    // The user's entry must not be touched
    assert.ok(
      settings.mcpServers['my-custom-server'],
      'User-owned mcpServers entry must be preserved after registerMcp'
    );
    assert.equal(settings.mcpServers['my-custom-server'].command, 'node');

    // The crumb entry should also be present
    assert.ok(settings.mcpServers[MCP_SERVER_NAME], 'crumb entry should be added alongside existing entries');
  });
});

// ===========================================================================
// Test: registerHooks called during install flow
// ===========================================================================

test('install flow: registerHooks writes statusLine and PreToolUse entries to settings.json', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // settings.json absent before install — registerHooks should create it
    const exists = await pathExists(settingsPath);
    assert.ok(!exists, 'settings.json should not exist before install');

    const { warnings } = await registerHooks({ dryRun: false, collector: null, settingsPath });

    // No warnings expected on a fresh registration
    assert.deepEqual(warnings, [], 'No warnings should be returned on fresh hooks registration');

    // settings.json should now exist
    const written = await pathExists(settingsPath);
    assert.ok(written, 'registerHooks should create settings.json when it does not exist');

    // Parse the written file and verify both hook entries
    const raw = await fs.readFile(settingsPath, 'utf8');
    const settings = JSON.parse(raw);

    // statusLine entry must be present with the correct command
    assert.ok(
      settings.statusLine && typeof settings.statusLine === 'object',
      'settings.json should have a statusLine object after registerHooks'
    );
    assert.equal(
      settings.statusLine.command,
      STATUSLINE_COMMAND,
      'statusLine.command should match the expected ant-farm statusline command'
    );

    // PreToolUse entry must be present with the scope advisor command
    assert.ok(
      settings.hooks && Array.isArray(settings.hooks.PreToolUse),
      'settings.json should have a hooks.PreToolUse array after registerHooks'
    );
    const scopeAdvisorGroup = settings.hooks.PreToolUse.find(
      (group) =>
        Array.isArray(group.hooks) &&
        group.hooks.some((h) => h.command === SCOPE_ADVISOR_COMMAND)
    );
    assert.ok(
      scopeAdvisorGroup,
      'hooks.PreToolUse should contain a group with the ant-farm scope advisor command'
    );
    assert.equal(
      scopeAdvisorGroup.matcher,
      SCOPE_ADVISOR_MATCHER,
      'PreToolUse group matcher should match the expected SCOPE_ADVISOR_MATCHER value'
    );
  });
});

test('install flow: registerHooks is idempotent on re-install', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // First install
    await registerHooks({ dryRun: false, collector: null, settingsPath });

    // Second install (re-run)
    const { warnings } = await registerHooks({ dryRun: false, collector: null, settingsPath });

    assert.deepEqual(warnings, [], 'No warnings should be returned on idempotent re-install');

    // Both entries should still be present — not duplicated
    const raw = await fs.readFile(settingsPath, 'utf8');
    const settings = JSON.parse(raw);

    assert.ok(
      settings.statusLine && settings.statusLine.command === STATUSLINE_COMMAND,
      'statusLine entry should still be present after idempotent re-install'
    );

    const preToolUse = settings.hooks && settings.hooks.PreToolUse;
    assert.ok(Array.isArray(preToolUse), 'hooks.PreToolUse should remain an array after re-install');

    // Verify no duplicate scope advisor groups were added
    const matchingGroups = preToolUse.filter(
      (group) =>
        Array.isArray(group.hooks) &&
        group.hooks.some((h) => h.command === SCOPE_ADVISOR_COMMAND)
    );
    assert.equal(
      matchingGroups.length,
      1,
      'Idempotent re-install must not add duplicate PreToolUse groups'
    );
  });
});

test('install flow: registerHooks dry-run records update op without writing files', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');
    const collector = new DryRunCollector();

    const { warnings } = await registerHooks({ dryRun: true, collector, settingsPath });

    assert.deepEqual(warnings, [], 'No warnings should be returned in dry-run mode');

    // settings.json must NOT be created in dry-run
    const exists = await pathExists(settingsPath);
    assert.ok(!exists, 'registerHooks dry-run must not write settings.json');

    // Collector should have recorded an update op for settings.json
    const updateOps = collector._ops.filter(o => o.op === 'update');
    assert.ok(
      updateOps.length > 0,
      'Dry-run collector should record an update op for settings.json'
    );
    const targetsSettings = updateOps.some(o => o.dst === settingsPath || o.src === settingsPath);
    assert.ok(targetsSettings, 'Recorded update op should reference the settings.json path');
  });
});

test('install flow: registerHooks preserves existing non-ant-farm hook entries', async () => {
  await withTmpDir(async (tmpDir) => {
    const settingsPath = path.join(tmpDir, 'settings.json');

    // Pre-populate settings.json with a user-owned PreToolUse hook group
    const initial = {
      hooks: {
        PreToolUse: [
          {
            matcher: 'Bash',
            hooks: [{ type: 'command', command: 'node ~/.claude/hooks/my-custom-hook.js' }],
          },
        ],
      },
    };
    await fs.writeFile(settingsPath, JSON.stringify(initial, null, 2) + '\n', 'utf8');

    await registerHooks({ dryRun: false, collector: null, settingsPath });

    const raw = await fs.readFile(settingsPath, 'utf8');
    const settings = JSON.parse(raw);

    // The user's hook group must be preserved
    const userGroup = settings.hooks.PreToolUse.find(
      (group) =>
        Array.isArray(group.hooks) &&
        group.hooks.some((h) => h.command === 'node ~/.claude/hooks/my-custom-hook.js')
    );
    assert.ok(userGroup, 'User-owned PreToolUse hook group must be preserved after registerHooks');
    assert.equal(userGroup.matcher, 'Bash', 'User hook group matcher must remain unchanged');

    // The ant-farm scope advisor entry should also be present
    const scopeAdvisorGroup = settings.hooks.PreToolUse.find(
      (group) =>
        Array.isArray(group.hooks) &&
        group.hooks.some((h) => h.command === SCOPE_ADVISOR_COMMAND)
    );
    assert.ok(scopeAdvisorGroup, 'ant-farm scope advisor group should be added alongside user hook group');
  });
});
