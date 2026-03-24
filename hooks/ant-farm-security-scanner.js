#!/usr/bin/env node
'use strict';

/**
 * ant-farm-security-scanner.js — Claude Code PreToolUse hook for security scanning.
 *
 * Claude Code invokes this script for every PreToolUse event on the Write, Edit,
 * and Bash tools. It receives a JSON blob on stdin describing the tool call, then
 * writes a JSON response object to stdout.
 *
 * Behavior:
 *   Write tool:   scans input.tool_input.content for security patterns.
 *   Edit tool:    scans input.tool_input.new_string for security patterns.
 *   Bash tool:    scans input.tool_input.command for dangerous shell operations.
 *
 *   enforcing mode (default): detected patterns return { continue: false, reason: 'SECURITY: ...' }
 *   advisory mode:            detected patterns return { continue: true,  reason: 'SECURITY WARNING: ...' }
 *
 *   Files listed in security_exceptions in .ant-farm-scope.json bypass scanning.
 *   The hook is a silent no-op when no ant-farm session is detected (.ant-farm-scope.json absent).
 *
 * Response format:
 *   Silent (no output)                                       — no session, no violation, or exception
 *   {"continue": false, "reason": "SECURITY: pattern at N"} — enforcing mode violation
 *   {"continue": true,  "reason": "SECURITY WARNING: ..."}  — advisory mode violation
 *
 * Debug logging:
 *   Set ANT_FARM_DEBUG=1 to write trace events to ~/.claude/.ant-farm-hook-debug.log.
 *
 * Usage (Claude Code settings.json):
 *   "PreToolUse": [{
 *     "matcher": "Write|Edit|Bash",
 *     "type": "command",
 *     "command": "node /path/to/ant-farm-security-scanner.js"
 *   }]
 *
 * Exports:
 *   handler(input)  — async function accepting parsed JSON input, returning response string.
 *   BASH_PATTERNS   — array of dangerous shell operation patterns (exposed for testing).
 */

const fs = require('fs');
const path = require('path');
const { debugLog } = require('./lib/debug-log');
const { readScopeSidecar } = require('./lib/scope-reader');
const { scanContent } = require('./lib/security-scanner');

const HOOK_NAME = 'ant-farm-security-scanner';

/**
 * Bash-specific dangerous operation patterns.
 * These are checked against the shell command string directly (not file content).
 *
 * @type {Array<{name: string, regex: string, category: string, severity: string}>}
 */
const BASH_PATTERNS = [
  {
    name: 'curl_pipe_to_shell',
    regex: 'curl\\b[^|]*\\|\\s*(sh|bash|zsh|fish|ksh|dash)',
    category: 'dangerous_shell',
    severity: 'critical',
  },
  {
    name: 'wget_pipe_to_shell',
    regex: 'wget\\b[^|]*\\|\\s*(sh|bash|zsh|fish|ksh|dash)',
    category: 'dangerous_shell',
    severity: 'critical',
  },
  {
    name: 'eval_usage',
    regex: '\\beval\\s+[^#\\n]',
    category: 'dangerous_shell',
    severity: 'high',
  },
  {
    name: 'credential_exfiltration',
    regex:
      '(?:curl|wget|nc|netcat|ncat)\\b[^#\\n]*(?:AWS_SECRET|AWS_ACCESS_KEY|GITHUB_TOKEN|ANTHROPIC_API_KEY|DATABASE_URL|SECRET_KEY|PRIVATE_KEY)',
    category: 'dangerous_shell',
    severity: 'critical',
  },
  {
    name: 'destructive_filesystem_root',
    regex: '\\brm\\s+(?:-[rRf]*\\s+)?[/~][^#\\n]*',
    category: 'dangerous_shell',
    severity: 'high',
  },
  {
    name: 'destructive_format',
    regex: '\\b(?:mkfs|dd\\b[^#\\n]*of=/dev/(?:sd|hd|nvme|xvd|vd))',
    category: 'dangerous_shell',
    severity: 'critical',
  },
  {
    name: 'env_var_exfiltration',
    regex: '(?:curl|wget|nc|netcat)\\b[^#\\n]*\\$(?:HOME|PATH|ENV|SHELL|USER)[^#\\n]*',
    category: 'dangerous_shell',
    severity: 'high',
  },
];

/**
 * Reads the raw security_exceptions array from the scope sidecar.
 * These are pattern *names* (not file paths) to skip during scanning.
 *
 * This is separate from the scope-reader utility because security_exceptions
 * is a security-scanner-specific field that scope-reader doesn't extract.
 *
 * Returns an empty array when the sidecar is absent, malformed, or has no field.
 *
 * @param {string} projectDir  Absolute path to the project root.
 * @returns {string[]}
 */
function readSecurityExceptions(projectDir) {
  const sidecarPath = path.join(projectDir, '.ant-farm-scope.json');
  try {
    const raw = fs.readFileSync(sidecarPath, 'utf8');
    const parsed = JSON.parse(raw);
    if (parsed && Array.isArray(parsed.security_exceptions)) {
      return parsed.security_exceptions.filter((e) => typeof e === 'string');
    }
  } catch (_err) {
    // Absent or malformed — return empty.
  }
  return [];
}

/**
 * Loads security patterns from the sibling security-patterns.json file.
 * Returns an empty array if the file is absent or malformed.
 *
 * @returns {Array<{name: string, regex: string, category: string, severity: string}>}
 */
function loadFilePatterns() {
  try {
    const jsonPath = path.join(__dirname, 'lib', 'security-patterns.json');
    const raw = fs.readFileSync(jsonPath, 'utf8');
    const parsed = JSON.parse(raw);
    if (parsed && Array.isArray(parsed.patterns)) {
      return parsed.patterns;
    }
  } catch (err) {
    debugLog(HOOK_NAME, 'failed to load security-patterns.json', err && err.message);
  }
  return [];
}

/**
 * Extracts the content to scan from a Write or Edit tool_input.
 * Write → tool_input.content
 * Edit  → tool_input.new_string
 *
 * Returns null when no scannable content is present.
 *
 * @param {string} toolName
 * @param {object} toolInput
 * @returns {string|null}
 */
function extractFileContent(toolName, toolInput) {
  if (!toolInput) {
    return null;
  }
  if (toolName === 'Write' && typeof toolInput.content === 'string') {
    return toolInput.content;
  }
  if (toolName === 'Edit' && typeof toolInput.new_string === 'string') {
    return toolInput.new_string;
  }
  return null;
}

/**
 * Extracts the target file path from a Write or Edit tool_input.
 *
 * @param {object} toolInput
 * @returns {string|null}
 */
function extractTargetPath(toolInput) {
  if (toolInput && typeof toolInput.path === 'string' && toolInput.path.trim() !== '') {
    return toolInput.path.trim();
  }
  return null;
}

/**
 * Builds a human-readable violation reason string.
 *
 * @param {import('./lib/security-scanner').ScanMatch} match
 * @param {boolean} enforcing
 * @returns {string}
 */
function buildReason(match, enforcing) {
  const prefix = enforcing ? 'SECURITY' : 'SECURITY WARNING';
  return `${prefix}: ${match.name} at line ${match.line}`;
}

/**
 * Core handler: accepts the parsed JSON event object from Claude Code's
 * PreToolUse event, scans content for security issues, and returns either
 * an empty string (silent) or a JSON response string.
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

    // Silent no-op when no ant-farm session is active (sidecar absent).
    const scopeData = readScopeSidecar(projectDir);
    if (!scopeData) {
      debugLog(HOOK_NAME, 'sidecar absent — silent no-op');
      return '';
    }

    debugLog(HOOK_NAME, 'scopeData', scopeData);

    const toolName = (input && typeof input.tool_name === 'string' && input.tool_name) || '';
    const toolInput = (input && input.tool_input) || {};

    debugLog(HOOK_NAME, 'toolName', toolName);

    // Determine enforcement mode — default to 'enforcing' per spec (AC-3).
    // The scope sidecar mode field controls file-scope advisory vs enforcing.
    // We reuse the same mode for security scanning.
    const mode = scopeData.mode === 'advisory' ? 'advisory' : 'enforcing';
    const enforcing = mode === 'enforcing';

    // Read security_exceptions from sidecar (array of pattern names to skip).
    const securityExceptions = readSecurityExceptions(projectDir);

    debugLog(HOOK_NAME, 'securityExceptions', securityExceptions);

    // -----------------------------------------------------------------------
    // Bash tool: scan command for dangerous operations
    // -----------------------------------------------------------------------
    if (toolName === 'Bash') {
      const command =
        toolInput && typeof toolInput.command === 'string' ? toolInput.command : null;
      if (!command) {
        debugLog(HOOK_NAME, 'Bash: no command field — silent no-op');
        return '';
      }

      debugLog(HOOK_NAME, 'scanning Bash command');
      const matches = scanContent(command, BASH_PATTERNS, securityExceptions);

      if (matches.length === 0) {
        debugLog(HOOK_NAME, 'Bash: no violations found');
        return '';
      }

      const first = matches[0];
      debugLog(HOOK_NAME, 'Bash: violation found', first);

      const reason = buildReason(first, enforcing);
      return JSON.stringify({ continue: !enforcing, reason });
    }

    // -----------------------------------------------------------------------
    // Write / Edit tools: scan file content
    // -----------------------------------------------------------------------
    if (toolName !== 'Write' && toolName !== 'Edit') {
      debugLog(HOOK_NAME, 'tool not handled — silent no-op', toolName);
      return '';
    }

    // Check whether the target file is in the security_exceptions file list.
    const targetPath = extractTargetPath(toolInput);
    if (targetPath) {
      // security_exceptions in sidecar may contain file paths to bypass scanning.
      // Check if this file's basename or full path is in the exceptions list.
      const targetBasename = path.basename(targetPath);
      const securityFileExceptions = Array.isArray(scopeData.security_file_exceptions)
        ? scopeData.security_file_exceptions.filter((e) => typeof e === 'string')
        : [];

      if (securityFileExceptions.length > 0) {
        const resolvedTarget = path.resolve(projectDir, targetPath);
        for (const exc of securityFileExceptions) {
          const filePart = exc.replace(/:[0-9]+-[0-9]+$/, '');
          const resolvedExc = path.resolve(projectDir, filePart);
          if (resolvedTarget === resolvedExc || targetBasename === filePart) {
            debugLog(HOOK_NAME, 'file in security_file_exceptions — silent no-op', targetPath);
            return '';
          }
        }
      }
    }

    const content = extractFileContent(toolName, toolInput);
    if (content === null) {
      debugLog(HOOK_NAME, 'no scannable content in tool_input — silent no-op');
      return '';
    }

    const filePatterns = loadFilePatterns();
    debugLog(HOOK_NAME, 'scanning content', { toolName, patterns: filePatterns.length });

    const matches = scanContent(content, filePatterns, securityExceptions);

    if (matches.length === 0) {
      debugLog(HOOK_NAME, 'no security violations found');
      return '';
    }

    const first = matches[0];
    debugLog(HOOK_NAME, 'security violation found', first);

    const reason = buildReason(first, enforcing);
    return JSON.stringify({ continue: !enforcing, reason });
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

module.exports = {
  handler,
  extractFileContent,
  extractTargetPath,
  buildReason,
  BASH_PATTERNS,
  loadFilePatterns,
  readSecurityExceptions,
};
