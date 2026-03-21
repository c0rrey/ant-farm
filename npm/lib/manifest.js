'use strict';

/**
 * manifest.js — Read the install-manifest.json file list and write/read
 * the ~/.claude/.ant-farm-manifest.json tracking file.
 */

const fs = require('fs/promises');
const path = require('path');

/**
 * Reads install-manifest.json from the package root and returns the parsed
 * object. Throws if the file is missing or malformed.
 *
 * @param {string} packageRoot  Absolute path to the npm/ package directory.
 * @returns {Promise<{files: Array<{src: string, dst: string, description: string}>}>}
 */
async function readInstallManifest(packageRoot) {
  const manifestPath = path.join(packageRoot, 'install-manifest.json');
  let raw;
  try {
    raw = await fs.readFile(manifestPath, 'utf8');
  } catch (err) {
    throw new Error(`Cannot read install-manifest.json at ${manifestPath}: ${err.message}`);
  }
  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (err) {
    throw new Error(`install-manifest.json is not valid JSON: ${err.message}`);
  }
  if (!parsed || !Array.isArray(parsed.files)) {
    throw new Error('install-manifest.json must have a top-level "files" array');
  }
  return parsed;
}

/**
 * Writes the installed-files record to ~/.claude/.ant-farm-manifest.json.
 * Must be called AFTER all files are successfully installed.
 *
 * @param {string} claudeDir    Absolute path to ~/.claude/
 * @param {string} version      Package version string (from package.json)
 * @param {Array<{dst: string, checksum: string}>} installedFiles
 *   Each entry has the destination path (relative to claudeDir) and its
 *   SHA-256 hex checksum.
 */
async function writeInstalledManifest(claudeDir, version, installedFiles) {
  const manifestPath = path.join(claudeDir, '.ant-farm-manifest.json');
  const record = {
    version,
    installedAt: new Date().toISOString(),
    files: installedFiles.map(({ dst, checksum }) => ({ path: dst, sha256: checksum })),
  };
  await fs.writeFile(manifestPath, JSON.stringify(record, null, 2) + '\n', 'utf8');
  return manifestPath;
}

/**
 * Reads ~/.claude/.ant-farm-manifest.json if it exists.
 * Returns null if the file does not exist.
 * Throws if the file exists but cannot be parsed.
 *
 * @param {string} claudeDir  Absolute path to ~/.claude/
 * @returns {Promise<object|null>}
 */
async function readInstalledManifest(claudeDir) {
  const manifestPath = path.join(claudeDir, '.ant-farm-manifest.json');
  try {
    const raw = await fs.readFile(manifestPath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === 'ENOENT') return null;
    throw new Error(`Cannot read ${manifestPath}: ${err.message}`);
  }
}

module.exports = { readInstallManifest, writeInstalledManifest, readInstalledManifest };
