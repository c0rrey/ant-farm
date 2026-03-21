'use strict';

/**
 * dry-run.js — Dry-run mode support for the ant-farm-cc installer.
 *
 * In dry-run mode the installer must not write, delete, or modify any files.
 * Instead it collects a list of planned operations and prints a human-readable
 * preview at the end.
 *
 * Usage:
 *   const collector = new DryRunCollector();
 *   collector.add('install', src, dst);
 *   collector.add('update', src, dst);
 *   collector.add('backup', dst, bakPath);
 *   collector.add('skip-unchanged', null, dst);
 *   collector.add('remove', null, dst);
 *   collector.add('claude-md-create', null, dst);
 *   collector.add('claude-md-append', null, dst);
 *   collector.add('claude-md-update', null, dst);
 *   collector.add('claude-md-unchanged', null, dst);
 *   collector.add('claude-md-remove', null, dst);
 *   collector.printReport();
 */

const LABELS = {
  'install': '[would install]',
  'update': '[would update]',
  'backup': '[would backup]',
  'skip-unchanged': '[unchanged]',
  'remove': '[would remove]',
  'claude-md-create': '[would create CLAUDE.md with ant-farm block]',
  'claude-md-append': '[would append ant-farm block to CLAUDE.md]',
  'claude-md-update': '[would update ant-farm block in CLAUDE.md]',
  'claude-md-unchanged': '[unchanged CLAUDE.md ant-farm block]',
  'claude-md-remove': '[would remove ant-farm block from CLAUDE.md]',
};

class DryRunCollector {
  constructor() {
    /** @type {Array<{op: string, src: string|null, dst: string}>} */
    this._ops = [];
  }

  /**
   * Record a planned operation.
   *
   * @param {string} op   One of the operation keys defined in LABELS above.
   * @param {string|null} src  Source path (or null if not applicable).
   * @param {string} dst  Destination/target path.
   */
  add(op, src, dst) {
    this._ops.push({ op, src, dst });
  }

  /**
   * Returns the number of recorded operations.
   * @returns {number}
   */
  get count() {
    return this._ops.length;
  }

  /**
   * Prints a formatted dry-run report to stdout.
   * Called at the end of a dry-run pass.
   */
  printReport() {
    console.log('--- Dry-run preview (no files were written) ---');
    console.log('');

    if (this._ops.length === 0) {
      console.log('  (no operations planned)');
      console.log('');
      return;
    }

    for (const { op, src, dst } of this._ops) {
      const label = LABELS[op] || `[${op}]`;
      if (src) {
        console.log(`  ${label}  ${src}  →  ${dst}`);
      } else {
        console.log(`  ${label}  ${dst}`);
      }
    }
    console.log('');
    console.log(`Total: ${this._ops.length} operation(s) planned.`);
    console.log('Run without --dry-run to apply these changes.');
    console.log('');
  }
}

module.exports = { DryRunCollector };
