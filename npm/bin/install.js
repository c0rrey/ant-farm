#!/usr/bin/env node
'use strict';

/**
 * install.js — Entry point for the ant-farm-cc npm package installer.
 *
 * Usage:
 *   npx ant-farm-cc@latest
 *
 * What it does:
 *   1. Validates that Claude Code is installed (~/.claude/ must exist)
 *   2. Checks for a partial-install sentinel and warns if found
 *   3. Writes a .ant-farm-install-in-progress sentinel
 *   4. Reads file list from install-manifest.json (no hardcoded paths)
 *   5. Copies each file to ~/.claude/, backing up any existing files first
 *   6. Writes ~/.claude/.ant-farm-manifest.json with paths, checksums, version
 *   7. Removes the in-progress sentinel
 */

const path = require('path');
const os = require('os');
const { readInstallManifest, writeInstalledManifest } = require('../lib/manifest');
const { copyWithBackup, writeSentinel, removeSentinel, pathExists } = require('../lib/file-ops');

// The package root is the npm/ directory (one level up from bin/)
const PACKAGE_ROOT = path.resolve(__dirname, '..');

// Read version from package.json
const { version } = require('../package.json');

const CLAUDE_DIR = path.join(os.homedir(), '.claude');
const SENTINEL_PATH = path.join(CLAUDE_DIR, '.ant-farm-install-in-progress');

async function main() {
  console.log(`ant-farm-cc v${version} — installer`);
  console.log('');

  // -------------------------------------------------------------------------
  // Step 1: Validate that Claude Code is installed
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
  // Step 2: Check for partial-install sentinel from a previous run
  // -------------------------------------------------------------------------
  const sentinelExists = await pathExists(SENTINEL_PATH);
  if (sentinelExists) {
    console.warn('WARNING: A previous installation did not complete cleanly.');
    console.warn(`  Sentinel file found: ${SENTINEL_PATH}`);
    console.warn('  Proceeding with installation — files may be partially installed.');
    console.warn('');
  }

  // -------------------------------------------------------------------------
  // Step 3: Write in-progress sentinel
  // -------------------------------------------------------------------------
  await writeSentinel(
    SENTINEL_PATH,
    `ant-farm installation in progress — started ${new Date().toISOString()}\n`
  );

  // -------------------------------------------------------------------------
  // Step 4: Read install manifest
  // -------------------------------------------------------------------------
  let manifest;
  try {
    manifest = await readInstallManifest(PACKAGE_ROOT);
  } catch (err) {
    console.error(`ERROR: Failed to read install manifest: ${err.message}`);
    await removeSentinel(SENTINEL_PATH);
    process.exit(1);
  }

  const fileList = manifest.files;
  console.log(`Installing ${fileList.length} file(s) to ${CLAUDE_DIR} ...`);
  console.log('');

  // -------------------------------------------------------------------------
  // Step 5: Copy each file to ~/.claude/, backing up existing files first
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
    // Remove sentinel even on partial failure so re-runs get the warning
    await removeSentinel(SENTINEL_PATH);
    process.exit(1);
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
