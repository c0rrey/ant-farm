'use strict';

/**
 * uninstall.js — Uninstall support for the ant-farm-cc installer.
 *
 * Reads ~/.claude/.ant-farm-manifest.json (written by the installer) and
 * removes only the files listed in it.  Files not in the manifest are left
 * untouched (the installer is conservative — it never guesses).
 *
 * Partial install handling:
 *   If the manifest exists but is incomplete (e.g., crash during a previous
 *   install left some files not recorded), this function warns the caller
 *   via the returned warnings array rather than silently leaving orphaned files.
 *
 * CLAUDE.md sentinel:
 *   The installer owns only the sentinel block inside CLAUDE.md, not the whole
 *   file. Uninstall calls removeClaudeMdBlock() to strip the block while
 *   preserving any user content outside the sentinels.
 */

const fs = require('fs/promises');
const path = require('path');
const { readInstalledManifest } = require('./manifest');
const { pathExists } = require('./file-ops');
const { removeClaudeMdBlock } = require('./claude-md');

/**
 * Runs the uninstall workflow.
 *
 * @param {string} claudeDir   Absolute path to ~/.claude/
 * @param {object} [options]
 * @param {boolean} [options.dryRun=false]   If true, no files are removed.
 * @param {object|null} [options.collector]  DryRunCollector instance (required
 *   when dryRun is true).
 * @returns {Promise<{removed: string[], skipped: string[], warnings: string[]}>}
 *   removed:  paths of files that were (or would be) removed
 *   skipped:  paths listed in the manifest that did not exist on disk
 *   warnings: non-fatal issues found during uninstall
 */
async function runUninstall(claudeDir, { dryRun = false, collector = null } = {}) {
  const removed = [];
  const skipped = [];
  const warnings = [];

  // ------------------------------------------------------------------
  // Step 1: Read the installed manifest
  // ------------------------------------------------------------------
  let manifest;
  try {
    manifest = await readInstalledManifest(claudeDir);
  } catch (err) {
    // If the manifest exists but is corrupted, surface the error.
    throw new Error(`Failed to read install manifest: ${err.message}`);
  }

  if (!manifest) {
    warnings.push(
      'Install manifest not found. ant-farm-cc may not have been installed via npm, ' +
      'or the manifest was deleted. Cannot determine which files to remove safely.\n' +
      `Expected manifest at: ${path.join(claudeDir, '.ant-farm-manifest.json')}`
    );
    return { removed, skipped, warnings };
  }

  // ------------------------------------------------------------------
  // Step 2: Validate manifest structure
  // ------------------------------------------------------------------
  if (!Array.isArray(manifest.files)) {
    warnings.push(
      'Install manifest exists but has no "files" array — it may be corrupt or ' +
      'from an incompatible version. Cannot determine which files to remove safely.'
    );
    return { removed, skipped, warnings };
  }

  if (manifest.files.length === 0) {
    warnings.push('Install manifest is present but lists no installed files.');
    return { removed, skipped, warnings };
  }

  console.log(`Found manifest with ${manifest.files.length} file(s) (installed v${manifest.version || 'unknown'}).`);
  console.log('');

  // ------------------------------------------------------------------
  // Step 3: Remove each file listed in the manifest
  // ------------------------------------------------------------------
  for (const entry of manifest.files) {
    const filePath = path.join(claudeDir, entry.path);

    const exists = await pathExists(filePath);
    if (!exists) {
      skipped.push(filePath);
      console.log(`  skip (not found): ${filePath}`);
      continue;
    }

    if (dryRun) {
      collector.add('remove', null, filePath);
      removed.push(filePath);
      continue;
    }

    try {
      await fs.unlink(filePath);
      console.log(`  removed: ${filePath}`);
      removed.push(filePath);
    } catch (err) {
      warnings.push(`Failed to remove ${filePath}: ${err.message}`);
      console.warn(`  WARNING: failed to remove ${filePath}: ${err.message}`);
    }
  }

  // ------------------------------------------------------------------
  // Step 4: Remove the CLAUDE.md sentinel block (owns only the block, not
  //         the whole file)
  // ------------------------------------------------------------------
  const claudeMdPath = path.join(claudeDir, 'CLAUDE.md');
  try {
    await removeClaudeMdBlock(claudeMdPath, { dryRun, collector });
  } catch (err) {
    // Non-fatal: warn but continue so the manifest itself still gets removed
    warnings.push(`Could not remove ant-farm block from CLAUDE.md: ${err.message}`);
    console.warn(`  WARNING: ${err.message}`);
  }

  // ------------------------------------------------------------------
  // Step 5: Remove the manifest file itself (last — records completion)
  // ------------------------------------------------------------------
  const manifestPath = path.join(claudeDir, '.ant-farm-manifest.json');
  if (!dryRun) {
    try {
      await fs.unlink(manifestPath);
      console.log(`  removed manifest: ${manifestPath}`);
    } catch (err) {
      if (err.code !== 'ENOENT') {
        warnings.push(`Failed to remove manifest: ${err.message}`);
        console.warn(`  WARNING: failed to remove manifest: ${err.message}`);
      }
    }
  } else {
    collector.add('remove', null, manifestPath);
  }

  // ------------------------------------------------------------------
  // Step 6: Partial install detection
  //   If skipped files are suspiciously many relative to total, warn that
  //   the installation may have been partial.
  // ------------------------------------------------------------------
  if (skipped.length > 0) {
    const pct = Math.round((skipped.length / manifest.files.length) * 100);
    if (pct >= 50) {
      warnings.push(
        `${skipped.length} of ${manifest.files.length} manifest entries were not found on disk ` +
        `(${pct}%). The installation may have been incomplete or partially cleaned up manually.`
      );
    }
  }

  return { removed, skipped, warnings };
}

module.exports = { runUninstall };
