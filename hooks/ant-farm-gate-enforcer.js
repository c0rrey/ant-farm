#!/usr/bin/env node
'use strict';

/**
 * ant-farm-gate-enforcer.js — Claude Code PreToolUse hook for gate enforcement.
 *
 * Claude Code invokes this script for every PreToolUse event on Task, TeamCreate,
 * and SendMessage tools. It receives a JSON blob on stdin describing the tool call,
 * then writes a JSON response object to stdout.
 *
 * Behavior:
 *   - Detects active ant-farm sessions via path-scan of the Task prompt for
 *     '.crumbs/sessions/_session-' (primary). SESSION_DIR env var is an optional
 *     fast-path; if set but pointing to a non-existent path, falls through to scan.
 *   - For TeamCreate / SendMessage tool calls: bypass gate checks (review team
 *     operates within a gated phase and must not be blocked).
 *   - Reads gate-status.json from the detected session directory.
 *   - Checks that the 'startup-check' predecessor gate has passed.
 *   - If 'startup-check' has NOT passed: blocks the spawn ({ continue: false }).
 *   - If 'startup-check' has passed: allows the spawn (empty string / silent).
 *   - If bypass_gates is true in .crumbs/config.json: logs a warning and allows all spawns.
 *   - If no ant-farm session is detected: silent no-op.
 *
 * Response format:
 *   Silent (no output)                            — session absent, TeamCreate/SendMessage, or gate passed
 *   {"continue": false, "reason": "Gate blocked…"} — startup-check not yet passed
 *
 * Silent no-op conditions (produces no stdout output):
 *   - No ant-farm session detected in prompt or env
 *   - Tool is TeamCreate or SendMessage (bypass)
 *   - startup-check gate has passed
 *   - bypass_gates is true in config.json (warning logged, spawn allowed)
 *   - gate-status.json is absent or unreadable
 *   - Any unexpected runtime error
 *
 * Debug logging:
 *   Set ANT_FARM_DEBUG=1 to write trace events to ~/.claude/.ant-farm-hook-debug.log.
 *   When unset, all debug calls are no-ops.
 *
 * Usage (Claude Code settings.json):
 *   "PreToolUse": [{
 *     "matcher": "Task|TeamCreate|SendMessage",
 *     "type": "command",
 *     "command": "node /path/to/ant-farm-gate-enforcer.js"
 *   }]
 *
 * Exports:
 *   handler(input) — async function accepting the parsed JSON input object and
 *                    returning the JSON response string (or empty string for silent).
 *                    Used by tests to exercise logic without spawning a process.
 */

const fs = require('fs');
const path = require('path');
const { debugLog } = require('./lib/debug-log');
const { isGatePassed } = require('./lib/gate-manager');

const HOOK_NAME = 'ant-farm-gate-enforcer';

/** Marker string used to identify ant-farm session paths within a Task prompt. */
const SESSION_PATH_MARKER = '.crumbs/sessions/_session-';

/** Gate that must have passed before any Task-based agent spawn is allowed. */
const PREDECESSOR_GATE = 'startup-check';

/** Tools that bypass gate checks entirely (review team coordination). */
const BYPASS_TOOLS = new Set(['TeamCreate', 'SendMessage']);

// ---------------------------------------------------------------------------
// Session detection
// ---------------------------------------------------------------------------

/**
 * Attempts to detect the active session directory via SESSION_DIR env var.
 *
 * Returns the path only when SESSION_DIR is set and the directory actually
 * exists on disk. If the env var is set but the path does not exist, returns
 * null so the caller falls through to the path-scan strategy.
 *
 * @returns {string|null}  Absolute session directory path, or null.
 */
function detectSessionFromEnv() {
  const envDir = process.env.SESSION_DIR;
  if (!envDir || envDir.trim() === '') {
    return null;
  }
  try {
    if (fs.existsSync(envDir)) {
      debugLog(HOOK_NAME, 'session detected via SESSION_DIR env', envDir);
      return envDir;
    }
  } catch (_err) {
    // existsSync failure (e.g. permission error) — fall through to path-scan.
  }
  debugLog(HOOK_NAME, 'SESSION_DIR set but path does not exist — falling through to path-scan', envDir);
  return null;
}

/**
 * Scans a text string for a '.crumbs/sessions/_session-' path segment and
 * extracts the session directory path from the first match found.
 *
 * Strategy: find the marker, then scan backward for the preceding path root
 * (absolute path starting with /) and scan forward to the end of the session
 * directory segment (stops at whitespace, quote, or newline).
 *
 * Returns null if no session path marker is found in the text.
 *
 * @param {string} text  Text to scan (e.g. a Task prompt string).
 * @returns {string|null}  Extracted session directory path, or null.
 */
function extractSessionDirFromText(text) {
  if (typeof text !== 'string') {
    return null;
  }

  const markerIdx = text.indexOf(SESSION_PATH_MARKER);
  if (markerIdx === -1) {
    return null;
  }

  // Walk backward from the marker to find the start of the path.
  // A path starts at the most recent whitespace/quote/newline before the marker,
  // or at the beginning of the string.
  let start = markerIdx;
  while (start > 0) {
    const ch = text[start - 1];
    if (ch === ' ' || ch === '\t' || ch === '\n' || ch === '\r' || ch === '"' || ch === "'") {
      break;
    }
    start--;
  }

  // Walk forward from the marker past the session directory segment.
  // The session directory ends at whitespace, a quote, or a forward-slash
  // immediately following the session-id token, or end of string.
  // Session dir format: .../sessions/_session-<id>  (no trailing slash before deeper paths)
  // We want to capture through the end of the _session-<id> component.
  const markerEnd = markerIdx + SESSION_PATH_MARKER.length;
  let end = markerEnd;
  // Skip past the session-id token (alphanumeric, hyphens, underscores).
  while (end < text.length) {
    const ch = text[end];
    if (ch === ' ' || ch === '\t' || ch === '\n' || ch === '\r' || ch === '"' || ch === "'" || ch === '/') {
      break;
    }
    end++;
  }

  const candidate = text.slice(start, end);
  if (candidate.length === 0) {
    return null;
  }

  debugLog(HOOK_NAME, 'session detected via path-scan', candidate);
  return candidate;
}

/**
 * Detects the active session directory from a PreToolUse input object.
 *
 * Detection order:
 *   1. SESSION_DIR env var (fast-path) — used only if path exists on disk.
 *   2. Path-scan of tool_input.prompt (primary) — scans for SESSION_PATH_MARKER.
 *
 * Returns null if no session is detected.
 *
 * @param {object} input  Parsed JSON from Claude Code's PreToolUse stdin.
 * @returns {string|null}
 */
function detectSessionDir(input) {
  // Fast-path: SESSION_DIR env var (optional).
  const envResult = detectSessionFromEnv();
  if (envResult !== null) {
    return envResult;
  }

  // Primary: path-scan of the Task prompt.
  const prompt =
    input &&
    input.tool_input &&
    typeof input.tool_input.prompt === 'string'
      ? input.tool_input.prompt
      : null;

  if (prompt === null) {
    debugLog(HOOK_NAME, 'no prompt in tool_input — cannot path-scan');
    return null;
  }

  return extractSessionDirFromText(prompt);
}

// ---------------------------------------------------------------------------
// Config bypass
// ---------------------------------------------------------------------------

/**
 * Reads .crumbs/config.json from the given project directory and returns
 * true if bypass_gates is set to a truthy value.
 *
 * Returns false on any failure (file absent, parse error, missing field).
 * This is intentionally conservative — a config read failure does NOT
 * bypass the gate.
 *
 * @param {string} projectDir  Absolute path to the project root.
 * @returns {boolean}
 */
function isBypassEnabled(projectDir) {
  const configPath = path.join(projectDir, '.crumbs', 'config.json');
  let raw;
  try {
    raw = fs.readFileSync(configPath, 'utf8');
  } catch (_err) {
    // Config file absent — bypass not enabled.
    return false;
  }

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (_err) {
    debugLog(HOOK_NAME, 'config.json parse error — bypass not enabled', configPath);
    return false;
  }

  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
    return false;
  }

  return Boolean(parsed.bypass_gates);
}

// ---------------------------------------------------------------------------
// Core handler
// ---------------------------------------------------------------------------

/**
 * Core handler: accepts the parsed JSON event object from Claude Code's
 * PreToolUse event, enforces gate ordering, and returns either an empty string
 * (silent allow) or a JSON block response string.
 *
 * Returns an empty string for any silent no-op condition.
 *
 * @param {object} input  Parsed JSON from Claude Code's PreToolUse stdin.
 * @returns {Promise<string>}
 */
async function handler(input) {
  try {
    // Determine tool name — TeamCreate and SendMessage bypass gate checks.
    const toolName =
      input && typeof input.tool_name === 'string' ? input.tool_name : '';

    if (BYPASS_TOOLS.has(toolName)) {
      debugLog(HOOK_NAME, `bypassing gate check for tool: ${toolName}`);
      return '';
    }

    // Resolve project directory from workspace (falls back to cwd).
    const projectDir =
      (input &&
        input.workspace &&
        typeof input.workspace.project_dir === 'string' &&
        input.workspace.project_dir) ||
      process.cwd();

    debugLog(HOOK_NAME, 'projectDir', projectDir);

    // Detect session directory — silent no-op if absent.
    const sessionDir = detectSessionDir(input);
    if (sessionDir === null) {
      debugLog(HOOK_NAME, 'no ant-farm session detected — silent no-op');
      return '';
    }

    debugLog(HOOK_NAME, 'sessionDir', sessionDir);

    // Check bypass_gates config — warn and allow if enabled.
    if (isBypassEnabled(projectDir)) {
      debugLog(HOOK_NAME, 'WARNING: bypass_gates=true in config.json — gate enforcement disabled for this spawn');
      return '';
    }

    // Check the predecessor gate.
    const gatePassed = isGatePassed(sessionDir, PREDECESSOR_GATE);
    debugLog(HOOK_NAME, `gate ${PREDECESSOR_GATE} passed: ${gatePassed}`, { sessionDir });

    if (!gatePassed) {
      const reason = `Gate blocked: ${PREDECESSOR_GATE} has not passed for session ${sessionDir}`;
      debugLog(HOOK_NAME, 'blocking Task spawn — gate not passed', { reason });
      return JSON.stringify({ continue: false, reason });
    }

    // Gate has passed — allow spawn silently.
    debugLog(HOOK_NAME, 'gate passed — allowing Task spawn');
    return '';
  } catch (err) {
    debugLog(HOOK_NAME, 'unexpected error', err && err.message);
    return '';
  }
}

// ---------------------------------------------------------------------------
// Main entrypoint
// ---------------------------------------------------------------------------

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

module.exports = {
  handler,
  detectSessionDir,
  extractSessionDirFromText,
  detectSessionFromEnv,
  isBypassEnabled,
  SESSION_PATH_MARKER,
  PREDECESSOR_GATE,
  BYPASS_TOOLS,
};
