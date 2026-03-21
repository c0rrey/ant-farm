'use strict';

/**
 * file-ops.js — File copy, backup, and SHA-256 checksum operations.
 */

const fs = require('fs/promises');
const crypto = require('crypto');
const path = require('path');

/**
 * Computes the SHA-256 hex digest of a file.
 *
 * @param {string} filePath  Absolute path to the file.
 * @returns {Promise<string>}  Hex string.
 */
async function sha256File(filePath) {
  const data = await fs.readFile(filePath);
  return crypto.createHash('sha256').update(data).digest('hex');
}

/**
 * Creates a timestamped .bak backup of an existing file.
 * The backup path is: <filePath>.bak.<ISO-timestamp-safe>
 * e.g. /home/user/.claude/agents/foo.md.bak.20240101T120000Z
 *
 * @param {string} filePath  Absolute path to the file to back up.
 * @returns {Promise<string>}  The backup path.
 */
async function backupFile(filePath) {
  // Format: YYYYMMDDTHHMMSSz — compact, filesystem-safe, lexicographically sortable
  const ts = new Date().toISOString().replace(/[-:.]/g, '').slice(0, 15) + 'Z';
  const bakPath = `${filePath}.bak.${ts}`;
  await fs.copyFile(filePath, bakPath);
  return bakPath;
}

/**
 * Copies src to dst, creating parent directories as needed.
 * If dst already exists, creates a timestamped .bak backup first.
 *
 * @param {string} src  Absolute source path.
 * @param {string} dst  Absolute destination path.
 * @param {boolean} [verbose=false]  Log progress to stdout.
 * @returns {Promise<{backed_up: string|null, checksum: string}>}
 *   backed_up: path to the backup file (or null if no backup was needed)
 *   checksum: SHA-256 hex digest of the installed file
 */
async function copyWithBackup(src, dst, verbose = false) {
  // Ensure the destination directory exists
  const dstDir = path.dirname(dst);
  await fs.mkdir(dstDir, { recursive: true });

  let backedUp = null;

  // Check if destination already exists
  try {
    await fs.access(dst);
    // File exists — back it up before overwriting
    backedUp = await backupFile(dst);
    if (verbose) {
      console.log(`  backed up: ${dst} → ${backedUp}`);
    }
  } catch {
    // File does not exist — no backup needed
  }

  await fs.copyFile(src, dst);

  const checksum = await sha256File(dst);

  if (verbose) {
    console.log(`  installed: ${dst}`);
  }

  return { backed_up: backedUp, checksum };
}

/**
 * Writes a sentinel file to the given path.
 *
 * @param {string} sentinelPath  Absolute path.
 * @param {string} [content]  Optional content.
 */
async function writeSentinel(sentinelPath, content = '') {
  await fs.writeFile(sentinelPath, content, 'utf8');
}

/**
 * Removes a sentinel file. Does nothing if the file does not exist.
 *
 * @param {string} sentinelPath  Absolute path.
 */
async function removeSentinel(sentinelPath) {
  try {
    await fs.unlink(sentinelPath);
  } catch (err) {
    if (err.code !== 'ENOENT') throw err;
  }
}

/**
 * Returns true if the given path exists (as a file or directory).
 *
 * @param {string} targetPath  Absolute path.
 * @returns {Promise<boolean>}
 */
async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

module.exports = { sha256File, backupFile, copyWithBackup, writeSentinel, removeSentinel, pathExists };
