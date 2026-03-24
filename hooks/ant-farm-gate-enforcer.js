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
 *   - Checks wave failure rate when spawning wave N > 1: blocks if wave N-1 failure rate
 *     exceeds wave_failure_threshold (default 0.5, configurable via config.json).
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
 *   handler(input)                      — async hook entry point; accepts parsed JSON input,
 *                                         returns JSON response string (or '' for silent pass).
 *   detectSessionDir(input)             — extract session directory from parsed JSON input object.
 *   extractSessionDirFromText(text)     — low-level regex helper used by detectSessionDir.
 *   detectSessionFromEnv()              — locate session dir from SESSION_DIR env var.
 *   isBypassEnabled(projectDir)         — return true when bypass flag is active in config.
 *   extractTaskIdFromPrompt(prompt)     — parse the active crumb/task ID out of a prompt string.
 *   extractWaveNumberFromPrompt(prompt) — parse the current wave number out of a prompt string.
 *   getWaveFailureThreshold(projectDir) — return the configured wave failure threshold (number, 0–1).
 *   getStuckAgentThresholds(projectDir) — return { timeoutMinutes, escalationMinutes } thresholds.
 *   checkStuckAgents(sessionDir, projectDir) — scan agent spawn log and return stuck-agent report.
 *   SESSION_PATH_MARKER                 — string sentinel written to session files.
 *   PREDECESSOR_GATE                    — gate-type constant for predecessor checks.
 *   POSITION_CHECK_GATE                 — gate-type constant for position/step checks.
 *   RETRY_FAILURE_TYPE                  — failure-type constant used in retry verdicts.
 *   AGENT_SPAWN_GATE                    — gate-type constant for agent spawn limits.
 *   BYPASS_TOOLS                        — Set of tool names exempt from gate enforcement.
 *   DEFAULT_WAVE_FAILURE_THRESHOLD      — default threshold for wave failures (0.5).
 *   DEFAULT_STUCK_AGENT_TIMEOUT_MINUTES — default minutes before an agent is considered stuck.
 *   DEFAULT_STUCK_AGENT_ESCALATION_MINUTES — default minutes before stuck agent is escalated.
 */

const fs = require('fs');
const path = require('path');
const { debugLog } = require('./lib/debug-log');
const { isGatePassed, writeGateVerdict, appendAgentSpawn, readAgentSpawns } = require('./lib/gate-manager');
const { getExpectedNextStep } = require('./lib/progress-reader');
const { canRetry } = require('./lib/retry-tracker');
const { getWaveStatus } = require('./lib/wave-tracker');

const HOOK_NAME = 'ant-farm-gate-enforcer';

/** Marker string used to identify ant-farm session paths within a Task prompt. */
const SESSION_PATH_MARKER = '.crumbs/sessions/_session-';

/** Gate that must have passed before any Task-based agent spawn is allowed. */
const PREDECESSOR_GATE = 'startup-check';

/** Gate name used when recording the position check verdict in gate-status.json. */
const POSITION_CHECK_GATE = 'position-check';

/** Tools that bypass gate checks entirely (review team coordination). */
const BYPASS_TOOLS = new Set(['TeamCreate', 'SendMessage']);

/**
 * Failure type passed to canRetry() for gate-enforcer-level retry checks.
 * Gate-enforced re-spawns are checkpoint retries.
 */
const RETRY_FAILURE_TYPE = 'checkpoint';

/**
 * Gate name used when recording agent spawn timestamps in gate-status.json.
 * Written with a PASS verdict each time a spawn is allowed through.
 */
const AGENT_SPAWN_GATE = 'agent-spawn';

/**
 * Default wave failure threshold. Spawning is blocked when the previous wave's
 * failureRate exceeds this value. Configurable via config.json wave_failure_threshold.
 */
const DEFAULT_WAVE_FAILURE_THRESHOLD = 0.5;

/**
 * Default stuck-agent timeout in minutes. An advisory WARNING is injected when
 * an agent has been running longer than this without producing a commit.
 * Configurable via config.json stuck_agent_timeout_minutes.
 */
const DEFAULT_STUCK_AGENT_TIMEOUT_MINUTES = 10;

/**
 * Default stuck-agent escalation threshold in minutes. The advisory escalates
 * to CRITICAL when an agent has been running longer than this.
 * Configurable via config.json stuck_agent_escalation_minutes.
 */
const DEFAULT_STUCK_AGENT_ESCALATION_MINUTES = 15;

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
// Wave number extraction and threshold config
// ---------------------------------------------------------------------------

/**
 * Reads wave_failure_threshold from .crumbs/config.json.
 *
 * Returns DEFAULT_WAVE_FAILURE_THRESHOLD (0.5) on any failure (file absent,
 * parse error, missing field, non-numeric value). Conservative fallback —
 * a config read failure does NOT disable wave checks.
 *
 * @param {string} projectDir  Absolute path to the project root.
 * @returns {number}  Threshold value in range [0, 1].
 */
function getWaveFailureThreshold(projectDir) {
  const configPath = path.join(projectDir, '.crumbs', 'config.json');
  let raw;
  try {
    raw = fs.readFileSync(configPath, 'utf8');
  } catch (_err) {
    return DEFAULT_WAVE_FAILURE_THRESHOLD;
  }

  let parsed;
  try {
    parsed = JSON.parse(raw);
  } catch (_err) {
    debugLog(HOOK_NAME, 'config.json parse error — using default wave_failure_threshold');
    return DEFAULT_WAVE_FAILURE_THRESHOLD;
  }

  if (
    parsed === null ||
    typeof parsed !== 'object' ||
    Array.isArray(parsed) ||
    typeof parsed.wave_failure_threshold !== 'number'
  ) {
    return DEFAULT_WAVE_FAILURE_THRESHOLD;
  }

  const val = parsed.wave_failure_threshold;
  return Math.max(0, Math.min(1, val));
}

/**
 * Scans a prompt string for a wave number indicator.
 *
 * Recognized patterns (case-insensitive):
 *   - "Wave 2", "wave 3", "WAVE 1"
 *   - "wave=2" (progress.log style key=value)
 *
 * Returns the parsed wave number, or null if no wave indicator is found.
 * Returns null for wave numbers <= 0 (invalid).
 *
 * @param {string} prompt  The Task tool prompt string.
 * @returns {number|null}  Parsed wave number, or null.
 */
function extractWaveNumberFromPrompt(prompt) {
  if (typeof prompt !== 'string') {
    return null;
  }

  // Match "Wave N" (case-insensitive) or "wave=N".
  const match = prompt.match(/\bwave[= ](\d+)\b/i);
  if (!match) {
    return null;
  }

  const waveNum = parseInt(match[1], 10);
  if (isNaN(waveNum) || waveNum <= 0) {
    return null;
  }

  return waveNum;
}

/**
 * Reads stuck-agent timeout and escalation thresholds from .crumbs/config.json.
 *
 * Returns defaults when the file is absent, unparseable, or the fields are missing.
 * Conservative fallback — a config read failure does NOT disable stuck-agent checks.
 *
 * @param {string} projectDir  Absolute path to the project root.
 * @returns {{ timeoutMinutes: number, escalationMinutes: number }}
 */
function getStuckAgentThresholds(projectDir) {
  const configPath = path.join(projectDir, '.crumbs', 'config.json');
  let parsed;
  try {
    const raw = fs.readFileSync(configPath, 'utf8');
    parsed = JSON.parse(raw);
  } catch (_err) {
    return {
      timeoutMinutes: DEFAULT_STUCK_AGENT_TIMEOUT_MINUTES,
      escalationMinutes: DEFAULT_STUCK_AGENT_ESCALATION_MINUTES,
    };
  }

  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
    return {
      timeoutMinutes: DEFAULT_STUCK_AGENT_TIMEOUT_MINUTES,
      escalationMinutes: DEFAULT_STUCK_AGENT_ESCALATION_MINUTES,
    };
  }

  return {
    timeoutMinutes: typeof parsed.stuck_agent_timeout_minutes === 'number'
      ? parsed.stuck_agent_timeout_minutes
      : DEFAULT_STUCK_AGENT_TIMEOUT_MINUTES,
    escalationMinutes: typeof parsed.stuck_agent_escalation_minutes === 'number'
      ? parsed.stuck_agent_escalation_minutes
      : DEFAULT_STUCK_AGENT_ESCALATION_MINUTES,
  };
}

/**
 * Checks whether any spawned agents in the session are stuck.
 *
 * Reads agent spawn records from agents.json and computes elapsed time for each
 * agent since its spawned_at timestamp. Returns an advisory string when any agent
 * exceeds the configured timeout, or null when all agents are within limits.
 *
 * Advisory levels:
 *   - WARNING  : elapsed >= stuck_agent_timeout_minutes (default 10)
 *   - CRITICAL : elapsed >= stuck_agent_escalation_minutes (default 15)
 *
 * Returns the highest severity advisory found. Returns null when no agents are
 * spawned or all agents are within the timeout window.
 *
 * @param {string} sessionDir  Absolute path to the session directory.
 * @param {string} projectDir  Absolute path to the project root.
 * @returns {string|null}  Advisory message string, or null.
 */
function checkStuckAgents(sessionDir, projectDir) {
  const spawns = readAgentSpawns(sessionDir);
  if (spawns.length === 0) {
    return null;
  }

  const { timeoutMinutes, escalationMinutes } = getStuckAgentThresholds(projectDir);
  const now = Date.now();

  let maxElapsedMinutes = 0;
  let stuckTaskId = null;

  for (const spawn of spawns) {
    if (!spawn.spawned_at) {
      continue;
    }
    const spawnedAt = new Date(spawn.spawned_at).getTime();
    if (isNaN(spawnedAt)) {
      continue;
    }
    const elapsedMs = now - spawnedAt;
    const elapsedMinutes = elapsedMs / (60 * 1000);
    if (elapsedMinutes > maxElapsedMinutes) {
      maxElapsedMinutes = elapsedMinutes;
      stuckTaskId = spawn.task_id;
    }
  }

  if (maxElapsedMinutes >= escalationMinutes) {
    return `CRITICAL: Agent ${stuckTaskId} has been active for ${Math.floor(maxElapsedMinutes)} minutes without a commit (escalation threshold: ${escalationMinutes} min)`;
  }

  if (maxElapsedMinutes >= timeoutMinutes) {
    return `WARNING: Agent ${stuckTaskId} has been active for ${Math.floor(maxElapsedMinutes)} minutes without a commit (timeout threshold: ${timeoutMinutes} min)`;
  }

  return null;
}

// ---------------------------------------------------------------------------
// Task ID extraction
// ---------------------------------------------------------------------------

/**
 * Scans a prompt string for the first occurrence of a crumb task ID
 * (format: two or more uppercase letters followed by a hyphen and digits,
 * e.g. "AF-123", "TSK-42").
 *
 * Returns the matched task ID, or 'unknown' if no match is found.
 * Used to supply a taskId to canRetry() for per-task retry accounting.
 *
 * @param {string} prompt  The Task tool prompt string.
 * @returns {string}  Matched task ID or 'unknown'.
 */
function extractTaskIdFromPrompt(prompt) {
  if (typeof prompt !== 'string') {
    return 'unknown';
  }
  const match = prompt.match(/\b([A-Z]{2,}-\d+)\b/);
  return match ? match[1] : 'unknown';
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

    // Retry check: extract task ID from the prompt and verify the retry limit
    // has not been exceeded for this task. Blocks re-spawns when canRetry()
    // returns false (per-type or global cap reached).
    const prompt =
      input &&
      input.tool_input &&
      typeof input.tool_input.prompt === 'string'
        ? input.tool_input.prompt
        : '';

    const taskId = extractTaskIdFromPrompt(prompt);
    const retryAllowed = canRetry(sessionDir, RETRY_FAILURE_TYPE, taskId);
    debugLog(HOOK_NAME, 'retry check', { taskId, retryAllowed });

    if (!retryAllowed) {
      const reason = `Retry limit exceeded: ${RETRY_FAILURE_TYPE} retries for task ${taskId} have reached the maximum`;
      debugLog(HOOK_NAME, 'blocking Task spawn — retry limit exceeded', { reason });
      return JSON.stringify({ continue: false, reason });
    }

    // Wave failure check: if this spawn is for wave N (N > 1), verify that the
    // previous wave (N-1) did not exceed the failure threshold. Blocks next-wave
    // spawning when the prior wave's failure rate is too high.
    const currentWave = extractWaveNumberFromPrompt(prompt);
    debugLog(HOOK_NAME, 'wave number extracted from prompt', { currentWave });

    if (currentWave !== null && currentWave > 1) {
      const prevWave = currentWave - 1;
      const waveFailureThreshold = getWaveFailureThreshold(projectDir);
      const prevWaveStatus = getWaveStatus(sessionDir, prevWave);
      debugLog(HOOK_NAME, 'previous wave status', { prevWave, prevWaveStatus, threshold: waveFailureThreshold });

      if (prevWaveStatus.total > 0 && prevWaveStatus.failureRate > waveFailureThreshold) {
        const reason =
          `Wave failure threshold exceeded: wave ${prevWave} had ` +
          `${prevWaveStatus.failed}/${prevWaveStatus.total} failures ` +
          `(rate ${prevWaveStatus.failureRate.toFixed(2)} > threshold ${waveFailureThreshold})`;
        debugLog(HOOK_NAME, 'blocking Task spawn — wave failure threshold exceeded', { reason });
        return JSON.stringify({ continue: false, reason });
      }
    }

    // Position check: verify the spawn matches the expected next step from progress.log.
    const expectedNextStep = getExpectedNextStep(sessionDir);
    debugLog(HOOK_NAME, 'expected next step from progress.log', { expectedNextStep });

    if (expectedNextStep !== null) {
      // Determine the step being attempted from the prompt text.
      // `prompt` was already extracted above for the retry check.
      const stepMatched = prompt.includes(expectedNextStep);
      debugLog(HOOK_NAME, `position check: expected="${expectedNextStep}" matched=${stepMatched}`);

      if (!stepMatched) {
        // Extract the attempting step label from the prompt for the error message.
        // Best-effort: scan for any known step name in the prompt, or fall back to 'unknown'.
        const KNOWN_STEPS = [
          'startup-check',
          'pre-spawn-check',
          'scope-verify',
          'claims-vs-code',
          'review-integrity',
          'session-complete',
          'position-check',
        ];
        const attemptingStep = KNOWN_STEPS.find((s) => prompt.includes(s)) || 'unknown';

        const reason = `Position check failed: expected ${expectedNextStep}, attempting ${attemptingStep}`;
        debugLog(HOOK_NAME, 'blocking Task spawn — position mismatch', { reason });

        // Write the position-check FAIL verdict to gate-status.json with next_step meta.
        try {
          writeGateVerdict(sessionDir, POSITION_CHECK_GATE, 'FAIL', { next_step: expectedNextStep });
        } catch (writeErr) {
          debugLog(HOOK_NAME, 'failed to write position-check FAIL verdict', writeErr && writeErr.message);
        }

        return JSON.stringify({ continue: false, reason });
      }

      // Position matches — write PASS verdict with next_step meta.
      try {
        writeGateVerdict(sessionDir, POSITION_CHECK_GATE, 'PASS', { next_step: expectedNextStep });
      } catch (writeErr) {
        debugLog(HOOK_NAME, 'failed to write position-check PASS verdict', writeErr && writeErr.message);
      }
    }

    // Record spawn timestamp in gate-status.json so the session log reflects
    // when agents were dispatched. Written as an agent-spawn PASS verdict;
    // the timestamp field is automatically included by writeGateVerdict().
    try {
      writeGateVerdict(sessionDir, AGENT_SPAWN_GATE, 'PASS', { task_id: taskId });
    } catch (spawnWriteErr) {
      debugLog(HOOK_NAME, 'failed to write agent-spawn verdict', spawnWriteErr && spawnWriteErr.message);
    }

    // Append agent spawn record to agents.json for stuck-agent detection and
    // crumb session-agents reporting. This accumulates across all spawns;
    // unlike gate-status.json's single-entry-per-gate, agents.json is an array.
    try {
      appendAgentSpawn(sessionDir, {
        task_id: taskId,
        spawned_at: new Date().toISOString(),
        status: 'spawned',
      });
    } catch (appendErr) {
      debugLog(HOOK_NAME, 'failed to append agent spawn record', appendErr && appendErr.message);
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
  extractTaskIdFromPrompt,
  extractWaveNumberFromPrompt,
  getWaveFailureThreshold,
  getStuckAgentThresholds,
  checkStuckAgents,
  SESSION_PATH_MARKER,
  PREDECESSOR_GATE,
  POSITION_CHECK_GATE,
  RETRY_FAILURE_TYPE,
  AGENT_SPAWN_GATE,
  BYPASS_TOOLS,
  DEFAULT_WAVE_FAILURE_THRESHOLD,
  DEFAULT_STUCK_AGENT_TIMEOUT_MINUTES,
  DEFAULT_STUCK_AGENT_ESCALATION_MINUTES,
};
