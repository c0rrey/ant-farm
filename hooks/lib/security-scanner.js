'use strict';

/**
 * security-scanner.js — Shared content security scanner for ant-farm hooks.
 *
 * Provides scanContent() which checks file content against a set of regex
 * patterns and returns an array of matches with name, line number, and text.
 *
 * Design decisions:
 *   - Patterns are accepted as plain objects (from security-patterns.json) so
 *     the JSON file is the single source of truth and extensible without code
 *     changes (AC-6).
 *   - Regexes are compiled per scanContent() call. With ~15 patterns this is
 *     negligible; the 512 KB guard prevents runaway scan time on large files.
 *   - exceptions is an array of pattern names to skip, giving callers fine-
 *     grained control over which checks to suppress for a specific file.
 *
 * No external dependencies. Uses the shared debug-log utility for advisory
 * messages so scan events appear in ANT_FARM_DEBUG=1 output.
 */

const { debugLog } = require('./debug-log');

/** Maximum content size in bytes before scanning is skipped. */
const MAX_CONTENT_BYTES = 512 * 1024; // 512 KB

const HOOK_NAME = 'security-scanner';

/**
 * @typedef {Object} PatternEntry
 * @property {string} name      - Unique pattern identifier.
 * @property {string} regex     - Regular expression source string.
 * @property {string} category  - Category label (e.g. 'secrets', 'injection', 'unsafe_code').
 * @property {string} severity  - Severity level (e.g. 'high', 'medium', 'critical').
 */

/**
 * @typedef {Object} ScanMatch
 * @property {string} name       - Pattern name that triggered the match.
 * @property {string} category   - Category from the pattern entry.
 * @property {string} severity   - Severity from the pattern entry.
 * @property {number} line       - 1-based line number of the match.
 * @property {string} matchedText - The matched text fragment.
 */

/**
 * Scans content against a set of patterns, returning all matches found.
 *
 * Skips scanning entirely when content exceeds 512 KB and logs an advisory.
 * Skips individual patterns whose name appears in the exceptions array.
 *
 * @param {string}         content    - File content to scan (UTF-8 string).
 * @param {PatternEntry[]} patterns   - Array of pattern entries (from security-patterns.json).
 * @param {string[]}       exceptions - Array of pattern names to skip for this scan.
 * @returns {ScanMatch[]}  Array of matches, empty if none found or scan skipped.
 */
function scanContent(content, patterns, exceptions) {
  if (typeof content !== 'string') {
    debugLog(HOOK_NAME, 'scanContent: content is not a string, skipping');
    return [];
  }

  const safePatterns = Array.isArray(patterns) ? patterns : [];
  const safeExceptions = Array.isArray(exceptions) ? exceptions : [];

  // Enforce 512 KB content size cap to prevent blocking the hook.
  const byteLength = Buffer.byteLength(content, 'utf8');
  if (byteLength > MAX_CONTENT_BYTES) {
    debugLog(HOOK_NAME, `scanContent: skipping scan — content exceeds 512 KB (${byteLength} bytes)`);
    return [];
  }

  const lines = content.split('\n');
  const matches = [];

  for (const entry of safePatterns) {
    if (!entry || typeof entry.name !== 'string' || typeof entry.regex !== 'string') {
      debugLog(HOOK_NAME, 'scanContent: skipping malformed pattern entry', entry);
      continue;
    }

    // Skip patterns listed in the exceptions array.
    if (safeExceptions.includes(entry.name)) {
      debugLog(HOOK_NAME, `scanContent: pattern "${entry.name}" skipped via exceptions`);
      continue;
    }

    let compiled;
    try {
      // Use 'i' flag for case-insensitive patterns that embed (?i) in their
      // source — strip the inline flag first so Node doesn't double-apply it.
      const regexSource = entry.regex.replace(/^\(\?i\)/, '');
      const flags = entry.regex.startsWith('(?i)') ? 'i' : '';
      compiled = new RegExp(regexSource, flags);
    } catch (err) {
      debugLog(HOOK_NAME, `scanContent: invalid regex for pattern "${entry.name}"`, err.message);
      continue;
    }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const m = compiled.exec(line);
      if (m !== null) {
        matches.push({
          name: entry.name,
          category: entry.category ?? '',
          severity: entry.severity ?? '',
          line: i + 1, // 1-based
          matchedText: m[0],
        });
      }
    }
  }

  debugLog(HOOK_NAME, `scanContent: found ${matches.length} match(es) across ${safePatterns.length} pattern(s)`);
  return matches;
}

module.exports = { scanContent, MAX_CONTENT_BYTES };
