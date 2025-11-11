/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import type { GitIgnoreFilter } from '../utils/gitIgnoreParser.js';
import type { ContextIgnoreFilter } from '../utils/geminiIgnoreParser.js';
import { GitIgnoreParser } from '../utils/gitIgnoreParser.js';
import { ContextIgnoreParser } from '../utils/geminiIgnoreParser.js';
import { isGitRepository } from '../utils/gitUtils.js';
import * as path from 'node:path';

export interface FilterFilesOptions {
  respectGitIgnore?: boolean;
  respectContextIgnore?: boolean;
}

export interface FilterReport {
  filteredPaths: string[];
  ignoredCount: number;
}

export class FileDiscoveryService {
  private gitIgnoreFilter: GitIgnoreFilter | null = null;
  private geminiIgnoreFilter: ContextIgnoreFilter | null = null;
  private combinedIgnoreFilter: GitIgnoreFilter | null = null;
  private projectRoot: string;

  constructor(projectRoot: string) {
    this.projectRoot = path.resolve(projectRoot);
    if (isGitRepository(this.projectRoot)) {
      this.gitIgnoreFilter = new GitIgnoreParser(this.projectRoot);
    }
    this.geminiIgnoreFilter = new ContextIgnoreParser(this.projectRoot);

    if (this.gitIgnoreFilter) {
      const geminiPatterns = this.geminiIgnoreFilter.getPatterns();
      // Create combined parser: .gitignore + .geminiignore
      this.combinedIgnoreFilter = new GitIgnoreParser(
        this.projectRoot,
        geminiPatterns,
      );
    }
  }

  /**
   * Filters a list of file paths based on git ignore rules
   */
  filterFiles(filePaths: string[], options: FilterFilesOptions = {}): string[] {
    const { respectGitIgnore = true, respectContextIgnore = true } = options;
    return filePaths.filter((filePath) => {
      if (
        respectGitIgnore &&
        respectContextIgnore &&
        this.combinedIgnoreFilter
      ) {
        return !this.combinedIgnoreFilter.isIgnored(filePath);
      }

      if (respectGitIgnore && this.gitIgnoreFilter?.isIgnored(filePath)) {
        return false;
      }
      if (respectContextIgnore && this.geminiIgnoreFilter?.isIgnored(filePath)) {
        return false;
      }
      return true;
    });
  }

  /**
   * Filters a list of file paths based on git ignore rules and returns a report
   * with counts of ignored files.
   */
  filterFilesWithReport(
    filePaths: string[],
    opts: FilterFilesOptions = {
      respectGitIgnore: true,
      respectContextIgnore: true,
    },
  ): FilterReport {
    const filteredPaths = this.filterFiles(filePaths, opts);
    const ignoredCount = filePaths.length - filteredPaths.length;

    return {
      filteredPaths,
      ignoredCount,
    };
  }

  /**
   * Unified method to check if a file should be ignored based on filtering options
   */
  shouldIgnoreFile(
    filePath: string,
    options: FilterFilesOptions = {},
  ): boolean {
    return this.filterFiles([filePath], options).length === 0;
  }
}
