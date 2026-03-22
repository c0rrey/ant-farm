'use strict';

/**
 * claude-md.js — CLAUDE.md sentinel block injection and removal.
 *
 * Replicates the logic from scripts/setup.sh sync_claude_block and
 * remove_claude_block functions using the EXACT same sentinel markers.
 *
 * Sentinel markers (must match setup.sh L102-103 exactly):
 *   <!-- ant-farm:start -->
 *   <!-- ant-farm:end -->
 *
 * Rules:
 *  - If the destination CLAUDE.md does not exist: create it with only the block.
 *  - If the file exists but has no sentinel: back it up, append the block
 *    (with a leading newline to avoid joining onto the last line).
 *  - If the file has both sentinels and the block is identical: do nothing.
 *  - If the file has both sentinels and the block differs: back it up, replace
 *    only the content between (inclusive of) the sentinel lines.
 *  - If only the start sentinel is found but not the end: error, refuse to touch.
 *
 * In dry-run mode (dryRun === true) no files are written; instead the planned
 * operation is recorded on the provided DryRunCollector.
 */

const fs = require('fs/promises');
const path = require('path');
const { backupFile, pathExists } = require('./file-ops');

const ANTFARM_START = '<!-- ant-farm:start -->';
const ANTFARM_END = '<!-- ant-farm:end -->';

/**
 * Builds the sentinel-wrapped block string from the given content string.
 * The result is:
 *   <!-- ant-farm:start -->
 *   <content>
 *   <!-- ant-farm:end -->
 *
 * @param {string} content  The raw block content (without sentinel lines).
 * @returns {string}  The wrapped block (ends with a newline).
 */
function buildBlock(content) {
  // Normalise content: ensure it ends with exactly one newline
  const body = content.endsWith('\n') ? content : content + '\n';
  return `${ANTFARM_START}\n${body}${ANTFARM_END}\n`;
}

/**
 * Extracts the ant-farm block (inclusive of sentinel lines) from text.
 * Returns null if no block is present.
 *
 * @param {string} text  File content as a string.
 * @returns {string|null}
 */
function extractBlock(text) {
  const lines = text.split('\n');
  let inside = false;
  const result = [];

  for (const line of lines) {
    if (line === ANTFARM_START) {
      inside = true;
      result.push(line);
      continue;
    }
    if (inside) {
      result.push(line);
      if (line === ANTFARM_END) break;
    }
  }

  return result.length > 0 ? result.join('\n') : null;
}

/**
 * Replaces the ant-farm block in text with newBlock.
 * Lines outside the sentinels are preserved verbatim.
 * The old sentinel lines (and everything between them) are removed and newBlock
 * is inserted in their place.
 *
 * @param {string} text      Original file content.
 * @param {string} newBlock  Replacement block string (including sentinel lines).
 * @returns {string}  Updated file content.
 */
function replaceBlock(text, newBlock) {
  const lines = text.split('\n');
  const result = [];
  let skip = false;

  for (const line of lines) {
    if (line === ANTFARM_START) {
      skip = true;
      // Insert the replacement block here (split into lines)
      const blockLines = newBlock.split('\n');
      // Remove the trailing empty element caused by trailing newline in newBlock
      if (blockLines[blockLines.length - 1] === '') blockLines.pop();
      for (const bl of blockLines) result.push(bl);
      continue;
    }
    if (skip && line === ANTFARM_END) {
      skip = false;
      continue;
    }
    if (!skip) {
      result.push(line);
    }
  }

  return result.join('\n');
}

/**
 * Removes the ant-farm block (inclusive of sentinel lines) from text.
 * Lines outside the sentinels are preserved verbatim.
 *
 * @param {string} text  Original file content.
 * @returns {string}  Updated file content with the block removed.
 */
function removeBlockFromText(text) {
  const lines = text.split('\n');
  const result = [];
  let skip = false;

  for (const line of lines) {
    if (line === ANTFARM_START) {
      skip = true;
      continue;
    }
    if (skip && line === ANTFARM_END) {
      skip = false;
      continue;
    }
    if (!skip) {
      result.push(line);
    }
  }

  return result.join('\n');
}

/**
 * Injects or replaces the ant-farm block in the destination CLAUDE.md file.
 *
 * @param {string} blockContent  Raw content to place inside the sentinel block
 *   (the sentinel lines themselves are added by this function).
 * @param {string} dst   Absolute path to the target CLAUDE.md.
 * @param {object} [options]
 * @param {boolean} [options.dryRun=false]  If true, no files are written.
 * @param {object|null} [options.collector]  DryRunCollector instance (required
 *   when dryRun is true).
 * @returns {Promise<void>}
 */
async function syncClaudeMdBlock(blockContent, dst, { dryRun = false, collector = null } = {}) {
  const block = buildBlock(blockContent);

  const dstExists = await pathExists(dst);

  if (!dstExists) {
    if (dryRun) {
      collector.add('claude-md-create', null, dst);
      return;
    }
    // Create the file with just the block
    await fs.mkdir(path.dirname(dst), { recursive: true });
    await fs.writeFile(dst, block, 'utf8');
    console.log(`  created: ${dst} (with ant-farm block)`);
    return;
  }

  const existing = await fs.readFile(dst, 'utf8');
  const hasStart = existing.includes(ANTFARM_START);
  const hasEnd = existing.includes(ANTFARM_END);

  if (!hasStart && !hasEnd) {
    // File exists, no sentinel block — append
    if (dryRun) {
      collector.add('claude-md-append', null, dst);
      return;
    }
    const bakPath = await backupFile(dst);
    console.log(`  backed up: ${dst} → ${bakPath}`);
    // Ensure trailing newline before appending
    const needsNewline = existing.length > 0 && !existing.endsWith('\n');
    const prefix = needsNewline ? '\n' : '';
    await fs.writeFile(dst, existing + prefix + '\n' + block, 'utf8');
    console.log(`  appended ant-farm block to: ${dst}`);
    return;
  }

  // Guard: start without end
  if (hasStart && !hasEnd) {
    throw new Error(
      `Found start sentinel but not end sentinel in ${dst} — refusing to modify. Fix the file manually.`
    );
  }

  // Guard: end without start (unusual but possible)
  if (!hasStart && hasEnd) {
    throw new Error(
      `Found end sentinel but not start sentinel in ${dst} — refusing to modify. Fix the file manually.`
    );
  }

  // Both sentinels present — compare content
  const existingBlock = extractBlock(existing);
  if (!existingBlock) {
    throw new Error(
      `Sentinel markers found in ${dst} but could not extract block — ` +
        `markers may not be on their own lines. Fix the file manually.`
    );
  }
  if (existingBlock.trimEnd() === block.trimEnd()) {
    if (dryRun) {
      collector.add('claude-md-unchanged', null, dst);
    } else {
      console.log(`  unchanged: ${dst} (ant-farm block)`);
    }
    return;
  }

  // Block differs — replace
  if (dryRun) {
    collector.add('claude-md-update', null, dst);
    return;
  }
  const bakPath = await backupFile(dst);
  console.log(`  backed up: ${dst} → ${bakPath}`);
  const updated = replaceBlock(existing, block);
  await fs.writeFile(dst, updated, 'utf8');
  console.log(`  updated ant-farm block in: ${dst}`);
}

/**
 * Removes the ant-farm block from the destination CLAUDE.md file.
 * If the file does not exist or has no block, does nothing.
 * Backs up the file before modifying.
 *
 * @param {string} dst  Absolute path to the target CLAUDE.md.
 * @param {object} [options]
 * @param {boolean} [options.dryRun=false]  If true, no files are written.
 * @param {object|null} [options.collector]  DryRunCollector instance.
 * @returns {Promise<void>}
 */
async function removeClaudeMdBlock(dst, { dryRun = false, collector = null } = {}) {
  const dstExists = await pathExists(dst);
  if (!dstExists) {
    if (dryRun) {
      console.log(`  [dry-run] no CLAUDE.md found at ${dst} — nothing to remove`);
    }
    return;
  }

  const existing = await fs.readFile(dst, 'utf8');
  const hasStart = existing.includes(ANTFARM_START);
  const hasEnd = existing.includes(ANTFARM_END);

  if (!hasStart) {
    if (dryRun) {
      console.log(`  [dry-run] no ant-farm block found in ${dst} — nothing to remove`);
    } else {
      console.log(`  no ant-farm block found in ${dst} — nothing to remove`);
    }
    return;
  }

  // Guard: start without end
  if (hasStart && !hasEnd) {
    throw new Error(
      `Found start sentinel but not end sentinel in ${dst} — refusing to modify. Fix the file manually.`
    );
  }

  if (dryRun) {
    collector.add('claude-md-remove', null, dst);
    return;
  }

  const bakPath = await backupFile(dst);
  console.log(`  backed up: ${dst} → ${bakPath}`);
  const updated = removeBlockFromText(existing);
  await fs.writeFile(dst, updated, 'utf8');
  console.log(`  removed ant-farm block from: ${dst}`);
}

module.exports = {
  ANTFARM_START,
  ANTFARM_END,
  buildBlock,
  extractBlock,
  replaceBlock,
  removeBlockFromText,
  syncClaudeMdBlock,
  removeClaudeMdBlock,
};
