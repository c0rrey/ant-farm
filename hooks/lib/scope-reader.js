'use strict';

/**
 * scope-reader.js — Scope sidecar JSON reader utility for ant-farm hooks.
 *
 * Reads .ant-farm-scope.json from the project root directory and returns the
 * parsed scope data. Returns null on any failure: file absent, partial/corrupt
 * JSON, wrong shape, or any unexpected error.
 *
 * Sidecar format:
 *   {
 *     "crumb_id": "AF-NNN",
 *     "allowed_files": ["path/to/file.js", "other/file.py:10-50", ...]
 *   }
 *
 * The caller is responsible for resolving allowed_files entries relative to
 * the project root before comparing against a target file path.
 *
 * No external dependencies. Uses synchronous fs.readFileSync so the hook
 * never introduces async complexity in the hot path.
 */

const fs = require('fs');
const path = require('path');

/** Name of the scope sidecar file. */
const SCOPE_SIDECAR_FILENAME = '.ant-farm-scope.json';

/**
 * Represents parsed scope data from the sidecar file.
 *
 * @typedef {Object} ScopeData
 * @property {string}   crumb_id      The crumb ID this scope is associated with.
 * @property {string[]} allowed_files List of allowed file paths (may include :line-range suffixes).
 */

/**
 * Reads and parses .ant-farm-scope.json from the given directory.
 *
 * Returns null (silently) when:
 *   - The sidecar file does not exist (most common case: no active scope)
 *   - The file contains invalid or partial JSON (TOCTOU / concurrent write)
 *   - The parsed value lacks a valid allowed_files array
 *   - Any unexpected I/O or parse error occurs
 *
 * @param {string} projectDir  Absolute path to the directory containing .ant-farm-scope.json.
 * @returns {ScopeData|null}
 */
function readScopeSidecar(projectDir) {
  const sidecarPath = path.join(projectDir, SCOPE_SIDECAR_FILENAME);

  let raw;
  try {
    raw = fs.readFileSync(sidecarPath, 'utf8');
  } catch (_err) {
    // File absent or not readable — silently inactive.
    return null;
  }

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (_err) {
    // Partial/corrupt JSON (e.g. mid-write TOCTOU) — fall back to silent no-op.
    return null;
  }

  // Validate shape: must be a plain object with a non-empty allowed_files array.
  if (
    parsed === null ||
    typeof parsed !== 'object' ||
    Array.isArray(parsed) ||
    !Array.isArray(parsed.allowed_files)
  ) {
    return null;
  }

  return {
    crumb_id: typeof parsed.crumb_id === 'string' ? parsed.crumb_id : '',
    allowed_files: parsed.allowed_files.filter((f) => typeof f === 'string'),
  };
}

/**
 * Checks whether a target file path is covered by the given ScopeData.
 *
 * Comparison strategy:
 *   1. Resolve both the target path and each allowed_files entry against
 *      projectDir to get absolute paths.
 *   2. Strip any :line-range suffix (e.g. ":10-50") from allowed_files entries
 *      before comparing — the advisory is file-level, not line-level.
 *   3. Use exact string equality on the resolved absolute paths.
 *
 * Returns true if the file is allowed (in scope), false if not.
 *
 * @param {string}    targetFile   Absolute or relative path of the file being written/edited.
 * @param {ScopeData} scopeData    Parsed scope data from readScopeSidecar().
 * @param {string}    projectDir   Absolute path to the project root (for resolving relative paths).
 * @returns {boolean}
 */
function isFileInScope(targetFile, scopeData, projectDir) {
  const resolvedTarget = path.resolve(projectDir, targetFile);

  for (const entry of scopeData.allowed_files) {
    // Strip optional :line-range suffix before resolving.
    const filePart = entry.replace(/:[0-9]+-[0-9]+$/, '');
    const resolvedEntry = path.resolve(projectDir, filePart);
    if (resolvedTarget === resolvedEntry) {
      return true;
    }
  }

  return false;
}

module.exports = { readScopeSidecar, isFileInScope, SCOPE_SIDECAR_FILENAME };
