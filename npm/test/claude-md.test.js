'use strict';

/**
 * claude-md.test.js — Tests for CLAUDE.md sentinel preservation.
 *
 * Tests cover:
 *  - syncClaudeMdBlock creates CLAUDE.md when it does not exist
 *  - syncClaudeMdBlock appends to existing CLAUDE.md without sentinel
 *  - syncClaudeMdBlock is idempotent when block is unchanged
 *  - syncClaudeMdBlock replaces block when content differs
 *  - syncClaudeMdBlock errors on malformed sentinels (start without end)
 *  - removeClaudeMdBlock removes the block from a file
 *  - removeClaudeMdBlock is a no-op when the file has no block
 *  - removeClaudeMdBlock is a no-op when the file does not exist
 *  - Dry-run: correct operation recorded, no files written
 *  - User content outside the sentinel block is preserved
 */

const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs/promises');
const os = require('os');
const path = require('path');

const {
  ANTFARM_START,
  ANTFARM_END,
  buildBlock,
  extractBlock,
  replaceBlock,
  removeBlockFromText,
  syncClaudeMdBlock,
  removeClaudeMdBlock,
} = require('../lib/claude-md');
const { DryRunCollector } = require('../lib/dry-run');
const { pathExists } = require('../lib/file-ops');

const SAMPLE_BLOCK_CONTENT = '# ant-farm orchestration block\nRun /ant-farm-init to install.\n';

// ---------------------------------------------------------------------------
// Helper: create a temporary directory and clean it up after the test.
// ---------------------------------------------------------------------------
async function withTmpDir(fn) {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'ant-farm-claude-md-test-'));
  try {
    await fn(dir);
  } finally {
    await fs.rm(dir, { recursive: true, force: true });
  }
}

// ===========================================================================
// Unit tests for pure text-manipulation functions
// ===========================================================================

test('buildBlock: wraps content between sentinel markers', () => {
  const result = buildBlock('Hello\n');
  assert.ok(result.startsWith(ANTFARM_START + '\n'), 'Block should start with start sentinel');
  assert.ok(result.endsWith(ANTFARM_END + '\n'), 'Block should end with end sentinel');
  assert.ok(result.includes('Hello\n'), 'Block should contain the supplied content');
});

test('buildBlock: normalizes content without trailing newline', () => {
  const result = buildBlock('Hello');
  assert.ok(result.includes('Hello\n'), 'buildBlock should add trailing newline if absent');
});

test('extractBlock: returns null when no sentinel markers present', () => {
  const text = '# My file\nSome content\n';
  assert.equal(extractBlock(text), null);
});

test('extractBlock: returns the block including sentinel lines', () => {
  const block = buildBlock(SAMPLE_BLOCK_CONTENT);
  const document = `# Preamble\n\n${block}\n# After\n`;
  const extracted = extractBlock(document);
  assert.ok(extracted !== null, 'Should find and return the block');
  assert.ok(extracted.includes(ANTFARM_START), 'Extracted block should include start sentinel');
  assert.ok(extracted.includes(ANTFARM_END), 'Extracted block should include end sentinel');
});

test('replaceBlock: replaces old block with new block', () => {
  const oldContent = 'old content\n';
  const newContent = 'new content\n';
  const document = `# Header\n\n${buildBlock(oldContent)}\n# Footer\n`;
  const newBlock = buildBlock(newContent);
  const result = replaceBlock(document, newBlock);
  assert.ok(!result.includes('old content'), 'Old content should be replaced');
  assert.ok(result.includes('new content'), 'New content should appear in result');
  assert.ok(result.includes('# Header'), 'Content before block should be preserved');
  assert.ok(result.includes('# Footer'), 'Content after block should be preserved');
});

test('removeBlockFromText: removes the block, preserving surrounding content', () => {
  const document = `# Header\n\n${buildBlock(SAMPLE_BLOCK_CONTENT)}\n# Footer\n`;
  const result = removeBlockFromText(document);
  assert.ok(!result.includes(ANTFARM_START), 'Start sentinel should be removed');
  assert.ok(!result.includes(ANTFARM_END), 'End sentinel should be removed');
  assert.ok(!result.includes(SAMPLE_BLOCK_CONTENT.trim()), 'Block content should be removed');
  assert.ok(result.includes('# Header'), 'Content before block should be preserved');
  assert.ok(result.includes('# Footer'), 'Content after block should be preserved');
});

test('removeBlockFromText: returns text unchanged when no block present', () => {
  const original = '# Just a header\nSome notes.\n';
  const result = removeBlockFromText(original);
  assert.equal(result, original, 'Text without sentinel should be returned unchanged');
});

// ===========================================================================
// Integration tests for syncClaudeMdBlock (filesystem)
// ===========================================================================

test('syncClaudeMdBlock: creates CLAUDE.md when file does not exist', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');

    await syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath);

    const exists = await pathExists(claudeMdPath);
    assert.ok(exists, 'CLAUDE.md should be created when it does not exist');

    const content = await fs.readFile(claudeMdPath, 'utf8');
    assert.ok(content.includes(ANTFARM_START), 'Created file should contain start sentinel');
    assert.ok(content.includes(ANTFARM_END), 'Created file should contain end sentinel');
    assert.ok(content.includes('ant-farm orchestration block'), 'Created file should contain the block content');
  });
});

test('syncClaudeMdBlock: appends block to existing CLAUDE.md without sentinel', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');
    const userContent = '# My custom instructions\nThese are mine.\n';
    await fs.writeFile(claudeMdPath, userContent, 'utf8');

    await syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath);

    const result = await fs.readFile(claudeMdPath, 'utf8');

    // User content must be preserved
    assert.ok(result.includes('My custom instructions'), 'User content before sentinel should be preserved');
    assert.ok(result.includes('These are mine.'), 'User content lines should be preserved');

    // Block should have been appended
    assert.ok(result.includes(ANTFARM_START), 'Start sentinel should be present after append');
    assert.ok(result.includes(ANTFARM_END), 'End sentinel should be present after append');

    // A backup should have been created
    const entries = await fs.readdir(tmpDir);
    const bakFiles = entries.filter(e => e.startsWith('CLAUDE.md.bak.'));
    assert.ok(bakFiles.length > 0, 'A backup should be created before appending to existing CLAUDE.md');
  });
});

test('syncClaudeMdBlock: is idempotent when block content is unchanged', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');

    // First sync — creates the file
    await syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath);
    const afterFirst = await fs.readFile(claudeMdPath, 'utf8');

    // Second sync with identical content
    await syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath);
    const afterSecond = await fs.readFile(claudeMdPath, 'utf8');

    assert.equal(afterFirst, afterSecond, 'File should not change on idempotent re-sync');

    // No backup file should be created on an unchanged sync
    const entries = await fs.readdir(tmpDir);
    const bakFiles = entries.filter(e => e.startsWith('CLAUDE.md.bak.'));
    assert.equal(bakFiles.length, 0, 'No backup should be created when content is unchanged');
  });
});

test('syncClaudeMdBlock: replaces block when content changes', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');
    const userContent = '# User header\n';
    await fs.writeFile(claudeMdPath, userContent + '\n' + buildBlock('old block content\n'), 'utf8');

    await syncClaudeMdBlock('new block content\n', claudeMdPath);

    const result = await fs.readFile(claudeMdPath, 'utf8');
    assert.ok(!result.includes('old block content'), 'Old block content should be replaced');
    assert.ok(result.includes('new block content'), 'New block content should be in file');
    assert.ok(result.includes('# User header'), 'User header outside block should be preserved');

    // Backup created
    const entries = await fs.readdir(tmpDir);
    const bakFiles = entries.filter(e => e.startsWith('CLAUDE.md.bak.'));
    assert.ok(bakFiles.length > 0, 'A backup should be created before updating the block');
  });
});

test('syncClaudeMdBlock: throws when start sentinel exists but end is missing', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');
    const malformed = `# Header\n${ANTFARM_START}\nsome content without end sentinel\n`;
    await fs.writeFile(claudeMdPath, malformed, 'utf8');

    await assert.rejects(
      () => syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath),
      /start sentinel.*not end sentinel|refusing to modify/i,
      'Should throw when start sentinel is present but end sentinel is missing'
    );
  });
});

test('syncClaudeMdBlock: user content after the block is preserved', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');

    const before = '# Before block\n';
    const after = '\n# After block\nUser notes here.\n';
    const initial = before + '\n' + buildBlock('initial content\n') + after;
    await fs.writeFile(claudeMdPath, initial, 'utf8');

    await syncClaudeMdBlock('updated content\n', claudeMdPath);

    const result = await fs.readFile(claudeMdPath, 'utf8');
    assert.ok(result.includes('# Before block'), 'Content before block should be preserved after update');
    assert.ok(result.includes('# After block'), 'Content after block should be preserved after update');
    assert.ok(result.includes('User notes here'), 'User notes after block should be preserved after update');
  });
});

// ===========================================================================
// Integration tests for removeClaudeMdBlock (filesystem)
// ===========================================================================

test('removeClaudeMdBlock: removes the block, preserves surrounding content', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');
    const userContent = '# User notes\nKeep this.\n';
    await fs.writeFile(claudeMdPath, userContent + '\n' + buildBlock(SAMPLE_BLOCK_CONTENT), 'utf8');

    await removeClaudeMdBlock(claudeMdPath);

    const result = await fs.readFile(claudeMdPath, 'utf8');
    assert.ok(!result.includes(ANTFARM_START), 'Start sentinel should be removed');
    assert.ok(!result.includes(ANTFARM_END), 'End sentinel should be removed');
    assert.ok(result.includes('# User notes'), 'User notes should be preserved after block removal');
    assert.ok(result.includes('Keep this.'), 'User content should be preserved after block removal');

    // A backup should have been created
    const entries = await fs.readdir(tmpDir);
    const bakFiles = entries.filter(e => e.startsWith('CLAUDE.md.bak.'));
    assert.ok(bakFiles.length > 0, 'A backup should be created before removing the block');
  });
});

test('removeClaudeMdBlock: is a no-op when file has no block', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');
    const original = '# No sentinel here\nJust user content.\n';
    await fs.writeFile(claudeMdPath, original, 'utf8');

    await removeClaudeMdBlock(claudeMdPath);

    const result = await fs.readFile(claudeMdPath, 'utf8');
    assert.equal(result, original, 'File should be unchanged when it has no sentinel block');

    // No backup should be created since nothing changed
    const entries = await fs.readdir(tmpDir);
    const bakFiles = entries.filter(e => e.startsWith('CLAUDE.md.bak.'));
    assert.equal(bakFiles.length, 0, 'No backup should be created when there is nothing to remove');
  });
});

test('removeClaudeMdBlock: is a no-op when file does not exist', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');

    // Should not throw
    await assert.doesNotReject(
      () => removeClaudeMdBlock(claudeMdPath),
      'removeClaudeMdBlock should not throw when file does not exist'
    );
  });
});

test('removeClaudeMdBlock: throws when start sentinel exists but end is missing', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');
    const malformed = `# Header\n${ANTFARM_START}\nsome content without end\n`;
    await fs.writeFile(claudeMdPath, malformed, 'utf8');

    await assert.rejects(
      () => removeClaudeMdBlock(claudeMdPath),
      /start sentinel.*not end sentinel|refusing to modify/i,
      'Should throw when start sentinel is present but end sentinel is missing'
    );
  });
});

// ===========================================================================
// Dry-run tests for syncClaudeMdBlock and removeClaudeMdBlock
// ===========================================================================

test('syncClaudeMdBlock dry-run: records claude-md-create, does not create file', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');
    const collector = new DryRunCollector();

    await syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath, { dryRun: true, collector });

    const exists = await pathExists(claudeMdPath);
    assert.ok(!exists, 'CLAUDE.md should NOT be created in dry-run mode');

    const createOps = collector._ops.filter(o => o.op === 'claude-md-create');
    assert.equal(createOps.length, 1, 'Should record one claude-md-create op in dry-run');
  });
});

test('syncClaudeMdBlock dry-run: records claude-md-append, does not write file', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');
    await fs.writeFile(claudeMdPath, '# Existing content\n', 'utf8');

    const originalContent = await fs.readFile(claudeMdPath, 'utf8');
    const collector = new DryRunCollector();

    await syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath, { dryRun: true, collector });

    const afterContent = await fs.readFile(claudeMdPath, 'utf8');
    assert.equal(afterContent, originalContent, 'File should not be modified in dry-run append mode');

    const appendOps = collector._ops.filter(o => o.op === 'claude-md-append');
    assert.equal(appendOps.length, 1, 'Should record one claude-md-append op in dry-run');
  });
});

test('syncClaudeMdBlock dry-run: records claude-md-unchanged when block matches', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');

    // Set up file with current block
    await syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath);
    const collector = new DryRunCollector();

    // Dry-run with identical content
    await syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath, { dryRun: true, collector });

    const unchangedOps = collector._ops.filter(o => o.op === 'claude-md-unchanged');
    assert.equal(unchangedOps.length, 1, 'Should record one claude-md-unchanged op in dry-run');
  });
});

test('syncClaudeMdBlock dry-run: records claude-md-update when block differs', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');

    // Install initial block
    await syncClaudeMdBlock('original content\n', claudeMdPath);
    const collector = new DryRunCollector();

    // Dry-run with different content
    await syncClaudeMdBlock('changed content\n', claudeMdPath, { dryRun: true, collector });

    const updateOps = collector._ops.filter(o => o.op === 'claude-md-update');
    assert.equal(updateOps.length, 1, 'Should record one claude-md-update op in dry-run');

    // File should be unchanged
    const content = await fs.readFile(claudeMdPath, 'utf8');
    assert.ok(content.includes('original content'), 'Original content should remain in dry-run update mode');
  });
});

test('removeClaudeMdBlock dry-run: records claude-md-remove, does not modify file', async () => {
  await withTmpDir(async (tmpDir) => {
    const claudeMdPath = path.join(tmpDir, 'CLAUDE.md');
    await syncClaudeMdBlock(SAMPLE_BLOCK_CONTENT, claudeMdPath);
    const originalContent = await fs.readFile(claudeMdPath, 'utf8');

    const collector = new DryRunCollector();
    await removeClaudeMdBlock(claudeMdPath, { dryRun: true, collector });

    const afterContent = await fs.readFile(claudeMdPath, 'utf8');
    assert.equal(afterContent, originalContent, 'File should not be modified in dry-run remove mode');

    const removeOps = collector._ops.filter(o => o.op === 'claude-md-remove');
    assert.equal(removeOps.length, 1, 'Should record one claude-md-remove op in dry-run');
  });
});
