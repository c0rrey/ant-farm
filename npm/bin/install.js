#!/usr/bin/env node
'use strict';

/**
 * install.js — Entry point for the ant-farm-cc npm package installer.
 *
 * Usage:
 *   npx ant-farm-cc@latest               # install
 *   npx ant-farm-cc@latest --dry-run     # preview without writing
 *   npx ant-farm-cc@latest --uninstall   # remove installed files
 *
 * Install workflow:
 *   1. Validates that Claude Code is installed (~/.claude/ must exist)
 *   2. Checks for a partial-install sentinel and warns if found
 *   3. Writes a .ant-farm-install-in-progress sentinel
 *   4. Reads file list from install-manifest.json (no hardcoded paths)
 *   5. Copies each file to ~/.claude/, backing up any existing files first
 *   6. Injects the ant-farm block into ~/.claude/CLAUDE.md (idempotent)
 *   7. Writes ~/.claude/.ant-farm-manifest.json with paths, checksums, version
 *   8. Removes the in-progress sentinel
 */

const path = require('path');
const fs = require('fs/promises');
const os = require('os');
const { readInstallManifest, writeInstalledManifest } = require('../lib/manifest');
const { copyWithBackup, writeSentinel, removeSentinel, pathExists } = require('../lib/file-ops');
const { DryRunCollector } = require('../lib/dry-run');
const { syncClaudeMdBlock } = require('../lib/claude-md');
const { runUninstall } = require('../lib/uninstall');

// The package root is the npm/ directory (one level up from bin/)
const PACKAGE_ROOT = path.resolve(__dirname, '..');

// Read version from package.json
const { version } = require('../package.json');

const CLAUDE_DIR = path.join(os.homedir(), '.claude');
const SENTINEL_PATH = path.join(CLAUDE_DIR, '.ant-farm-install-in-progress');
const CLAUDE_MD_PATH = path.join(CLAUDE_DIR, 'CLAUDE.md');

// The claude-block.md file lives at this path relative to the repo root
// (one level up from PACKAGE_ROOT which is npm/)
const CLAUDE_BLOCK_SRC = path.join(PACKAGE_ROOT, '..', 'orchestration', 'templates', 'claude-block.md');

/**
 * Parses CLI flags from process.argv.
 * @returns {{ dryRun: boolean, uninstall: boolean }}
 */
function parseFlags() {
  const args = process.argv.slice(2);
  return {
    dryRun: args.includes('--dry-run'),
    uninstall: args.includes('--uninstall'),
  };
}

async function main() {
  const { dryRun, uninstall } = parseFlags();

  console.log(`ant-farm-cc v${version} — installer`);
  if (dryRun) console.log('(dry-run mode — no files will be written)');
  if (uninstall) console.log('(uninstall mode)');
  console.log('');

  // -------------------------------------------------------------------------
  // Validate that Claude Code is installed (required for all modes)
  // -------------------------------------------------------------------------
  const claudeDirExists = await pathExists(CLAUDE_DIR);
  if (!claudeDirExists) {
    console.error('ERROR: Claude Code does not appear to be installed.');
    console.error('');
    console.error(`Expected directory not found: ${CLAUDE_DIR}`);
    console.error('');
    console.error('To fix this, install Claude Code first:');
    console.error('  https://claude.ai/download');
    console.error('');
    console.error('Then run the installer again:');
    console.error('  npx ant-farm-cc@latest');
    process.exit(1);
  }

  // -------------------------------------------------------------------------
  // Route: --uninstall
  // -------------------------------------------------------------------------
  if (uninstall) {
    await runUninstallMode(dryRun);
    return;
  }

  // -------------------------------------------------------------------------
  // Route: install (with optional --dry-run)
  // -------------------------------------------------------------------------
  await runInstallMode(dryRun);
}

// -----------------------------------------------------------------------------
// Uninstall mode
// -----------------------------------------------------------------------------
async function runUninstallMode(dryRun) {
  const collector = dryRun ? new DryRunCollector() : null;

  console.log('Uninstalling ant-farm-cc ...');
  console.log('');

  let result;
  try {
    result = await runUninstall(CLAUDE_DIR, { dryRun, collector });
  } catch (err) {
    console.error(`ERROR: ${err.message}`);
    process.exit(1);
  }

  const { removed, skipped, warnings } = result;

  console.log('');

  if (warnings.length > 0) {
    for (const w of warnings) {
      console.warn(`WARNING: ${w}`);
    }
    console.warn('');
  }

  if (dryRun) {
    collector.printReport();
  } else {
    if (removed.length > 0) {
      console.log(`Uninstall complete. ${removed.length} file(s) removed.`);
      if (skipped.length > 0) {
        console.log(`${skipped.length} file(s) listed in manifest were not found on disk (already removed?).`);
      }
    } else if (warnings.some(w => w.includes('manifest not found'))) {
      console.log('Uninstall could not proceed — see warnings above.');
      process.exit(1);
    } else {
      console.log('Nothing to uninstall.');
    }
  }
}

// -----------------------------------------------------------------------------
// Install mode
// -----------------------------------------------------------------------------
async function runInstallMode(dryRun) {
  const collector = dryRun ? new DryRunCollector() : null;

  // -------------------------------------------------------------------------
  // Step 1: Check for partial-install sentinel from a previous run
  // -------------------------------------------------------------------------
  const sentinelExists = await pathExists(SENTINEL_PATH);
  if (sentinelExists) {
    console.warn('WARNING: A previous installation did not complete cleanly.');
    console.warn(`  Sentinel file found: ${SENTINEL_PATH}`);
    console.warn('  Proceeding with installation — files may be partially installed.');
    console.warn('');
  }

  // -------------------------------------------------------------------------
  // Step 2: Write in-progress sentinel (skip in dry-run — no writes)
  // -------------------------------------------------------------------------
  if (!dryRun) {
    await writeSentinel(
      SENTINEL_PATH,
      `ant-farm installation in progress — started ${new Date().toISOString()}\n`
    );
  }

  // -------------------------------------------------------------------------
  // Step 3: Read install manifest
  // -------------------------------------------------------------------------
  let manifest;
  try {
    manifest = await readInstallManifest(PACKAGE_ROOT);
  } catch (err) {
    console.error(`ERROR: Failed to read install manifest: ${err.message}`);
    if (!dryRun) await removeSentinel(SENTINEL_PATH);
    process.exit(1);
  }

  const fileList = manifest.files;
  if (dryRun) {
    console.log(`Would install ${fileList.length} file(s) to ${CLAUDE_DIR} ...`);
  } else {
    console.log(`Installing ${fileList.length} file(s) to ${CLAUDE_DIR} ...`);
  }
  console.log('');

  // -------------------------------------------------------------------------
  // Step 4: Copy each file to ~/.claude/, backing up existing files first
  // -------------------------------------------------------------------------
  const installedFiles = [];
  const errors = [];

  for (const entry of fileList) {
    const src = path.join(PACKAGE_ROOT, '..', entry.src);
    const dst = path.join(CLAUDE_DIR, entry.dst);

    // Verify source file exists (package may be published without all files
    // if the manifest is out of sync — fail gracefully)
    const srcExists = await pathExists(src);
    if (!srcExists) {
      const msg = `Source file not found: ${src} (manifest entry: ${entry.src})`;
      errors.push(msg);
      console.error(`  SKIP (missing source): ${entry.src}`);
      continue;
    }

    if (dryRun) {
      // Determine what operation would occur
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

    try {
      const { checksum } = await copyWithBackup(src, dst, true);
      installedFiles.push({ dst: entry.dst, checksum });
    } catch (err) {
      const msg = `Failed to install ${entry.dst}: ${err.message}`;
      errors.push(msg);
      console.error(`  ERROR: ${msg}`);
    }
  }

  console.log('');

  if (errors.length > 0) {
    console.error(`${errors.length} file(s) failed to install:`);
    for (const e of errors) {
      console.error(`  - ${e}`);
    }
    if (!dryRun) await removeSentinel(SENTINEL_PATH);
    process.exit(1);
  }

  // -------------------------------------------------------------------------
  // Step 5: Inject CLAUDE.md sentinel block
  // -------------------------------------------------------------------------
  const claudeBlockExists = await pathExists(CLAUDE_BLOCK_SRC);
  if (!claudeBlockExists) {
    console.warn(`WARNING: claude-block.md not found at ${CLAUDE_BLOCK_SRC} — skipping CLAUDE.md injection.`);
  } else {
    const blockContent = await fs.readFile(CLAUDE_BLOCK_SRC, 'utf8');
    try {
      await syncClaudeMdBlock(blockContent, CLAUDE_MD_PATH, { dryRun, collector });
    } catch (err) {
      console.error(`ERROR: Failed to update CLAUDE.md: ${err.message}`);
      if (!dryRun) await removeSentinel(SENTINEL_PATH);
      process.exit(1);
    }
  }

  console.log('');

  if (dryRun) {
    collector.printReport();
    return;
  }

  // -------------------------------------------------------------------------
  // Step 6: Write ~/.claude/.ant-farm-manifest.json LAST
  // -------------------------------------------------------------------------
  let manifestPath;
  try {
    manifestPath = await writeInstalledManifest(CLAUDE_DIR, version, installedFiles);
  } catch (err) {
    console.error(`ERROR: Failed to write install manifest: ${err.message}`);
    await removeSentinel(SENTINEL_PATH);
    process.exit(1);
  }

  // -------------------------------------------------------------------------
  // Step 7: Remove in-progress sentinel
  // -------------------------------------------------------------------------
  await removeSentinel(SENTINEL_PATH);

  console.log(`Installation complete.`);
  console.log(`  ${installedFiles.length} file(s) installed`);
  console.log(`  Manifest written to: ${manifestPath}`);
  console.log('');
  console.log('Next step: open a new Claude Code session in your project');
  console.log('and run /ant-farm-init to complete setup.');
}

main().catch((err) => {
  console.error(`Unexpected error: ${err.message}`);
  process.exit(1);
});
