/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import type { Mock } from 'vitest';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { memoryCommand } from './memoryCommand.js';
import type { SlashCommand, CommandContext } from './types.js';
import { createMockCommandContext } from '../../test-utils/mockCommandContext.js';
import { MessageType } from '../types.js';
import type { LoadedSettings } from '../../config/settings.js';
import {
  getErrorMessage,
  SimpleExtensionLoader,
  type FileDiscoveryService,
} from '@codinglm/core';
import type { LoadServerHierarchicalMemoryResponse } from '@codinglm/core/index.js';
import { loadHierarchicalContextMemory } from '../../config/config.js';

vi.mock('@codinglm/core', async (importOriginal) => {
  const original =
    await importOriginal<typeof import('@codinglm/core')>();
  return {
    ...original,
    getErrorMessage: vi.fn((error: unknown) => {
      if (error instanceof Error) return error.message;
      return String(error);
    }),
  };
});

vi.mock('../../config/config.js', async (importOriginal) => {
  const original =
    await importOriginal<typeof import('../../config/config.js')>();
  return {
    ...original,
    loadHierarchicalContextMemory: vi.fn(),
  };
});

const mockLoadHierarchicalContextMemory = loadHierarchicalContextMemory as Mock;

describe('memoryCommand', () => {
  let mockContext: CommandContext;

  const getSubCommand = (
    name: 'show' | 'add' | 'refresh' | 'list',
  ): SlashCommand => {
    const subCommand = memoryCommand.subCommands?.find(
      (cmd) => cmd.name === name,
    );
    if (!subCommand) {
      throw new Error(`/memory ${name} command not found.`);
    }
    return subCommand;
  };

  describe('/memory show', () => {
    let showCommand: SlashCommand;
    let mockGetUserMemory: Mock;
    let mockGetContextFileCount: Mock;

    beforeEach(() => {
      showCommand = getSubCommand('show');

      mockGetUserMemory = vi.fn();
      mockGetContextFileCount = vi.fn();

      mockContext = createMockCommandContext({
        services: {
          config: {
            getUserMemory: mockGetUserMemory,
            getContextFileCount: mockGetContextFileCount,
            getExtensionLoader: () => new SimpleExtensionLoader([]),
          },
        },
      });
    });

    it('should display a message if memory is empty', async () => {
      if (!showCommand.action) throw new Error('Command has no action');

      mockGetUserMemory.mockReturnValue('');
      mockGetContextFileCount.mockReturnValue(0);

      await showCommand.action(mockContext, '');

      expect(mockContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.INFO,
          text: 'Memory is currently empty.',
        },
        expect.any(Number),
      );
    });

    it('should display the memory content and file count if it exists', async () => {
      if (!showCommand.action) throw new Error('Command has no action');

      const memoryContent = 'This is a test memory.';

      mockGetUserMemory.mockReturnValue(memoryContent);
      mockGetContextFileCount.mockReturnValue(1);

      await showCommand.action(mockContext, '');

      expect(mockContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.INFO,
          text: `Current memory content from 1 file(s):\n\n---\n${memoryContent}\n---`,
        },
        expect.any(Number),
      );
    });
  });

  describe('/memory add', () => {
    let addCommand: SlashCommand;

    beforeEach(() => {
      addCommand = getSubCommand('add');
      mockContext = createMockCommandContext();
    });

    it('should return an error message if no arguments are provided', () => {
      if (!addCommand.action) throw new Error('Command has no action');

      const result = addCommand.action(mockContext, '  ');
      expect(result).toEqual({
        type: 'message',
        messageType: 'error',
        content: 'Usage: /memory add <text to remember>',
      });

      expect(mockContext.ui.addItem).not.toHaveBeenCalled();
    });

    it('should return a tool action and add an info message when arguments are provided', () => {
      if (!addCommand.action) throw new Error('Command has no action');

      const fact = 'remember this';
      const result = addCommand.action(mockContext, `  ${fact}  `);

      expect(mockContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.INFO,
          text: `Attempting to save to memory: "${fact}"`,
        },
        expect.any(Number),
      );

      expect(result).toEqual({
        type: 'tool',
        toolName: 'save_memory',
        toolArgs: { fact },
      });
    });
  });

  describe('/memory refresh', () => {
    let refreshCommand: SlashCommand;
    let mockSetUserMemory: Mock;
    let mockSetContextFileCount: Mock;
    let mockSetContextFilePaths: Mock;

    beforeEach(() => {
      refreshCommand = getSubCommand('refresh');
      mockSetUserMemory = vi.fn();
      mockSetContextFileCount = vi.fn();
      mockSetContextFilePaths = vi.fn();

      const mockConfig = {
        setUserMemory: mockSetUserMemory,
        setContextFileCount: mockSetContextFileCount,
        setContextFilePaths: mockSetContextFilePaths,
        getWorkingDir: () => '/test/dir',
        getDebugMode: () => false,
        getFileService: () => ({}) as FileDiscoveryService,
        getExtensionLoader: () => new SimpleExtensionLoader([]),
        getExtensions: () => [],
        shouldLoadMemoryFromIncludeDirectories: () => false,
        getWorkspaceContext: () => ({
          getDirectories: () => [],
        }),
        getFileFilteringOptions: () => ({
          ignore: [],
          include: [],
        }),
        isTrustedFolder: () => false,
      };

      mockContext = createMockCommandContext({
        services: {
          config: mockConfig,
          settings: {
            merged: {
              memoryDiscoveryMaxDirs: 1000,
              context: {
                importFormat: 'tree',
              },
            },
          } as unknown as LoadedSettings,
        },
        ui: {
          setContextFileCount: vi.fn(),
        },
      });
      mockLoadHierarchicalContextMemory.mockClear();
    });

    it('should display success message when memory is refreshed with content', async () => {
      if (!refreshCommand.action) throw new Error('Command has no action');

      const refreshResult: LoadServerHierarchicalMemoryResponse = {
        memoryContent: 'new memory content',
        fileCount: 2,
        filePaths: ['/path/one/CODINGLM.md', '/path/two/CODINGLM.md'],
      };
      mockLoadHierarchicalContextMemory.mockResolvedValue(refreshResult);

      await refreshCommand.action(mockContext, '');

      expect(mockContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.INFO,
          text: 'Refreshing memory from source files...',
        },
        expect.any(Number),
      );

      expect(mockLoadHierarchicalContextMemory).toHaveBeenCalledOnce();
      expect(mockSetUserMemory).toHaveBeenCalledWith(
        refreshResult.memoryContent,
      );
      expect(mockSetContextFileCount).toHaveBeenCalledWith(
        refreshResult.fileCount,
      );
      expect(mockSetContextFilePaths).toHaveBeenCalledWith(
        refreshResult.filePaths,
      );
      expect(mockContext.ui.setContextFileCount).toHaveBeenCalledWith(
        refreshResult.fileCount,
      );

      expect(mockContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.INFO,
          text: 'Memory refreshed successfully. Loaded 18 characters from 2 file(s).',
        },
        expect.any(Number),
      );
    });

    it('should display success message when memory is refreshed with no content', async () => {
      if (!refreshCommand.action) throw new Error('Command has no action');

      const refreshResult = { memoryContent: '', fileCount: 0, filePaths: [] };
      mockLoadHierarchicalContextMemory.mockResolvedValue(refreshResult);

      await refreshCommand.action(mockContext, '');

      expect(mockLoadHierarchicalContextMemory).toHaveBeenCalledOnce();
      expect(mockSetUserMemory).toHaveBeenCalledWith('');
      expect(mockSetContextFileCount).toHaveBeenCalledWith(0);
      expect(mockSetContextFilePaths).toHaveBeenCalledWith([]);

      expect(mockContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.INFO,
          text: 'Memory refreshed successfully. No memory content found.',
        },
        expect.any(Number),
      );
    });

    it('should display an error message if refreshing fails', async () => {
      if (!refreshCommand.action) throw new Error('Command has no action');

      const error = new Error('Failed to read memory files.');
      mockLoadHierarchicalContextMemory.mockRejectedValue(error);

      await refreshCommand.action(mockContext, '');

      expect(mockLoadHierarchicalContextMemory).toHaveBeenCalledOnce();
      expect(mockSetUserMemory).not.toHaveBeenCalled();
      expect(mockSetContextFileCount).not.toHaveBeenCalled();
      expect(mockSetContextFilePaths).not.toHaveBeenCalled();

      expect(mockContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.ERROR,
          text: `Error refreshing memory: ${error.message}`,
        },
        expect.any(Number),
      );

      expect(getErrorMessage).toHaveBeenCalledWith(error);
    });

    it('should not throw if config service is unavailable', async () => {
      if (!refreshCommand.action) throw new Error('Command has no action');

      const nullConfigContext = createMockCommandContext({
        services: { config: null },
      });

      await expect(
        refreshCommand.action(nullConfigContext, ''),
      ).resolves.toBeUndefined();

      expect(nullConfigContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.INFO,
          text: 'Refreshing memory from source files...',
        },
        expect.any(Number),
      );

      expect(mockLoadHierarchicalContextMemory).not.toHaveBeenCalled();
    });
  });

  describe('/memory list', () => {
    let listCommand: SlashCommand;
    let mockGetcontextFilePaths: Mock;

    beforeEach(() => {
      listCommand = getSubCommand('list');
      mockGetcontextFilePaths = vi.fn();
      mockContext = createMockCommandContext({
        services: {
          config: {
            getContextFilePaths: mockGetcontextFilePaths,
          },
        },
      });
    });

    it('should display a message if no CODINGLM.md files are found', async () => {
      if (!listCommand.action) throw new Error('Command has no action');

      mockGetcontextFilePaths.mockReturnValue([]);

      await listCommand.action(mockContext, '');

      expect(mockContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.INFO,
          text: 'No CODINGLM.md files in use.',
        },
        expect.any(Number),
      );
    });

    it('should display the file count and paths if they exist', async () => {
      if (!listCommand.action) throw new Error('Command has no action');

      const filePaths = ['/path/one/CODINGLM.md', '/path/two/CODINGLM.md'];
      mockGetcontextFilePaths.mockReturnValue(filePaths);

      await listCommand.action(mockContext, '');

      expect(mockContext.ui.addItem).toHaveBeenCalledWith(
        {
          type: MessageType.INFO,
          text: `There are 2 CODINGLM.md file(s) in use:\n\n${filePaths.join('\n')}`,
        },
        expect.any(Number),
      );
    });
  });
});
