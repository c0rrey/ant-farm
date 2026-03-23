#!/usr/bin/env node
'use strict';

/**
 * ant-farm-scope-advisor.js — Claude Code PreToolUse hook for ant-farm scope advisory.
 *
 * Claude Code invokes this script for every PreToolUse event on the Write and Edit
 * tools. It receives a JSON blob on stdin describing the tool call, then writes a
 * JSON response object to stdout.
 *
 * Behavior:
 *   - Reads .ant-farm-scope.json from the project root.
 *   - If the target file IS in allowed_files: no advisory (tool proceeds normally).
 *   - If the target file is NOT in allowed_files:
 *       advisory mode  → injects an advisory message ({ continue: true, reason: "..." }).
 *       enforcing mode → blocks the write ({ continue: false, reason: "BLOCKED: ..." }).
 *   - permitted_exceptions paths bypass enforcement even in enforcing mode.
 *   - If .ant-farm-scope.json does not exist: silently inactive (no output).
 *   - mode absent or 'advisory': advisory only — never blocks tool execution.
 *
 * Response format:
 *   Silent (no output)                          — in-scope, exception, or sidecar absent
 *   {"continue": true, "reason": "<msg>"}       — out-of-scope advisory (advisory mode)
 *   {"continue": false, "reason": "BLOCKED: …"} — out-of-scope block (enforcing mode)
 *
 * Silent no-op conditions (produces no stdout output):
 *   - .ant-farm-scope.json does not exist in the project root
 *   - Target file is in the allowed_files list
 *   - Sidecar is unreadable, malformed, or has an unexpected shape
 *   - Any unexpected runtime error
 *
 * Debug logging:
 *   Set ANT_FARM_DEBUG=1 to write trace events to ~/.claude/.ant-farm-hook-debug.log.
 *   When unset, all errors are silently swallowed.
 *
 * Usage (Claude Code settings.json):
 *   "PreToolUse": [{
 *     "matcher": "Write|Edit",
 *     "type": "command",
 *     "command": "node /path/to/ant-farm-scope-advisor.js"
 *   }]
 *
 * Exports:
 *   handler(input) — async function that accepts the parsed JSON input object
 *                    and returns the JSON response string (or empty string for silent).
 *                    Used by tests to exercise the logic without spawning a process.
 */

const fs = require('fs');
const path = require('path');
const { debugLog } = require('./lib/debug-log');
const { readScopeSidecar, isFileInScope } = require('./lib/scope-reader');

const HOOK_NAME = 'ant-farm-scope-advisor';

/** Advisory message injected when a file is outside the assigned scope (advisory mode). */
const ADVISORY_MESSAGE =
  'This file is outside your assigned scope. Check your crumb file list before proceeding.';

/**
 * Checks whether a target file matches any entry in scopeData.permitted_exceptions.
 * Uses the same resolution strategy as isFileInScope: resolves against projectDir and
 * strips optional :line-range suffixes before comparing.
 *
 * @param {string}    targetFile   Absolute or relative path of the file being written/edited.
 * @param {import('./lib/scope-reader').ScopeData} scopeData  Parsed scope data.
 * @param {string}    projectDir   Absolute path to the project root.
 * @returns {boolean}  True if the file is in permitted_exceptions, false otherwise.
 */
function isPermittedException(targetFile, scopeData, projectDir) {
  const resolvedTarget = path.resolve(projectDir, targetFile);
  for (const entry of scopeData.permitted_exceptions) {
    const filePart = entry.replace(/:[0-9]+-[0-9]+$/, '');
    const resolvedEntry = path.resolve(projectDir, filePart);
    if (resolvedTarget === resolvedEntry) {
      return true;
    }
  }
  return false;
}

/**
 * Extracts the target file path from a PreToolUse input object.
 *
 * Claude Code's PreToolUse input provides tool parameters under input.tool_input.
 * Write and Edit both carry the target file path as `path` within tool_input.
 *
 * Returns null if the path cannot be extracted.
 *
 * @param {object} input  Parsed JSON from Claude Code's PreToolUse stdin.
 * @returns {string|null}
 */
function extractTargetPath(input) {
  if (
    input &&
    input.tool_input &&
    typeof input.tool_input.path === 'string' &&
    input.tool_input.path.trim() !== ''
  ) {
    return input.tool_input.path.trim();
  }
  return null;
}

/**
 * Core handler: accepts the parsed JSON event object from Claude Code's
 * PreToolUse event, checks the target file against the scope sidecar, and
 * returns either an empty string (silent) or a JSON advisory response string.
 *
 * Returns an empty string for any silent no-op condition.
 *
 * @param {object} input  Parsed JSON from Claude Code's PreToolUse stdin.
 * @returns {Promise<string>}
 */
async function handler(input) {
  try {
    const projectDir =
      (input &&
        input.workspace &&
        typeof input.workspace.project_dir === 'string' &&
        input.workspace.project_dir) ||
      process.cwd();

    debugLog(HOOK_NAME, 'projectDir', projectDir);

    const targetFile = extractTargetPath(input);
    if (!targetFile) {
      debugLog(HOOK_NAME, 'no target path in tool_input — silent no-op');
      return '';
    }

    debugLog(HOOK_NAME, 'targetFile', targetFile);

    const scopeData = readScopeSidecar(projectDir);
    if (!scopeData) {
      // Sidecar absent or unreadable — silently inactive.
      debugLog(HOOK_NAME, 'sidecar absent or unreadable — silent no-op');
      return '';
    }

    debugLog(HOOK_NAME, 'scopeData', scopeData);

    const inScope = isFileInScope(targetFile, scopeData, projectDir);
    debugLog(HOOK_NAME, 'isFileInScope', inScope);

    if (inScope) {
      // File is within scope — proceed normally with no output.
      return '';
    }

    // File is outside scope. Check mode to decide advisory vs. block.
    const mode = scopeData.mode; // 'advisory' | 'enforcing'

    if (mode === 'enforcing') {
      // Check permitted_exceptions before blocking.
      const isException = isPermittedException(targetFile, scopeData, projectDir);
      debugLog(HOOK_NAME, 'isPermittedException', isException);

      if (isException) {
        // Explicitly permitted — proceed silently.
        debugLog(HOOK_NAME, 'permitted exception — silent no-op', targetFile);
        return '';
      }

      // Block the write and log context for traceability.
      const crumbId = scopeData.crumb_id || '(unknown)';
      const allowedList = scopeData.allowed_files.join(', ') || '(none)';
      const agentContext =
        (input && input.agent && typeof input.agent === 'string' ? input.agent : null) ||
        (input && input.session_id ? `session:${input.session_id}` : 'unknown-agent');

      debugLog(
        HOOK_NAME,
        `BLOCKED write | agent: ${agentContext} | file: ${targetFile} | crumb: ${crumbId} | scope: ${allowedList}`
      );

      const blockReason = `BLOCKED: ${targetFile} is outside declared scope for ${crumbId}`;
      return JSON.stringify({ continue: false, reason: blockReason });
    }

    // Advisory mode (default) — emit warning but allow write.
    debugLog(HOOK_NAME, 'out-of-scope advisory injected', targetFile);
    return JSON.stringify({ continue: true, reason: ADVISORY_MESSAGE });
  } catch (err) {
    debugLog(HOOK_NAME, 'unexpected error', err && err.message);
    return '';
  }
}

/**
 * Main entrypoint: reads JSON from stdin, invokes handler(), writes result to stdout.
 * Exits with code 0 regardless of outcome — the hook must never crash Claude Code.
 */
async function main() {
  let inputText = '';
  try {
    inputText = fs.readFileSync('/dev/stdin', 'utf8');
  } catch (_err) {
    // stdin not available (e.g. during testing) — proceed with empty input.
  }

  let input = {};
  try {
    if (inputText && inputText.trim() !== '') {
      input = JSON.parse(inputText);
    }
  } catch (err) {
    debugLog(HOOK_NAME, 'failed to parse stdin JSON', err && err.message);
  }

  const result = await handler(input);
  if (result) {
    process.stdout.write(result + '\n');
  }
}

// Run main() only when this file is the direct entry point (not when required by tests).
if (require.main === module) {
  main().catch((_err) => {
    // Swallow all errors — never surface to Claude Code's error handling.
    process.exit(0);
  });
}

module.exports = { handler, extractTargetPath, isPermittedException, ADVISORY_MESSAGE };
