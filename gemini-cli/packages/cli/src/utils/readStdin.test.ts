/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { vi, describe, expect, it, beforeEach, afterEach } from 'vitest';
import { readStdin } from './readStdin.js';

// Mock process.stdin
const mockStdin = {
  setEncoding: vi.fn(),
  read: vi.fn(),
  on: vi.fn(),
  removeListener: vi.fn(),
  destroy: vi.fn(),
};

describe('readStdin', () => {
  let originalStdin: typeof process.stdin;
  let onReadableHandler: () => void;
  let onEndHandler: () => void;

  beforeEach(() => {
    vi.clearAllMocks();
    originalStdin = process.stdin;

    // Replace process.stdin with our mock
    Object.defineProperty(process, 'stdin', {
      value: mockStdin,
      writable: true,
      configurable: true,
    });

    // Capture event handlers
    mockStdin.on.mockImplementation((event: string, handler: () => void) => {
      if (event === 'readable') onReadableHandler = handler;
      if (event === 'end') onEndHandler = handler;
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    Object.defineProperty(process, 'stdin', {
      value: originalStdin,
      writable: true,
      configurable: true,
    });
  });

  it('should read and accumulate data from stdin', async () => {
    mockStdin.read
      .mockReturnValueOnce('I love ')
      .mockReturnValueOnce('CodinGLM!')
      .mockReturnValueOnce(null);

    const promise = readStdin();

    // Trigger readable event
    onReadableHandler();

    // Trigger end to resolve
    onEndHandler();

    await expect(promise).resolves.toBe('I love CodinGLM!');
  });

  it('should handle empty stdin input', async () => {
    mockStdin.read.mockReturnValue(null);

    const promise = readStdin();

    // Trigger end immediately
    onEndHandler();

    await expect(promise).resolves.toBe('');
  });

  // Emulate terminals where stdin is not TTY (eg: git bash)
  it('should timeout and resolve with empty string when no input is available', async () => {
    vi.useFakeTimers();

    const promise = readStdin();

    // Fast-forward past the timeout (to run test faster)
    vi.advanceTimersByTime(500);

    await expect(promise).resolves.toBe('');

    vi.useRealTimers();
  });

  it('should clear timeout once when data is received and resolve with data', async () => {
    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');
    mockStdin.read
      .mockReturnValueOnce('chunk1')
      .mockReturnValueOnce('chunk2')
      .mockReturnValueOnce(null);

    const promise = readStdin();

    // Trigger readable event
    onReadableHandler();

    expect(clearTimeoutSpy).toHaveBeenCalledOnce();

    // Trigger end to resolve
    onEndHandler();

    await expect(promise).resolves.toBe('chunk1chunk2');
  });

  it('should truncate and resolve when input exceeds MAX_STDIN_SIZE', async () => {
    const MAX_STDIN_SIZE = 8 * 1024 * 1024; // 8MB
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Create a large chunk that exceeds the limit
    const largeChunk = 'x'.repeat(MAX_STDIN_SIZE + 1000);

    mockStdin.read
      .mockReturnValueOnce(largeChunk)
      .mockReturnValueOnce(null);

    const promise = readStdin();

    // Trigger readable event
    onReadableHandler();

    // Promise should resolve with truncated data
    const result = await promise;

    // Verify truncation
    expect(result.length).toBe(MAX_STDIN_SIZE);
    expect(result).toBe('x'.repeat(MAX_STDIN_SIZE));

    // Verify stream was destroyed
    expect(mockStdin.destroy).toHaveBeenCalledOnce();

    // Verify user warning was shown
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining('⚠️  Warning: Input too large'),
    );

    consoleErrorSpy.mockRestore();
  });

  it('should handle size limit with multiple chunks', async () => {
    const MAX_STDIN_SIZE = 8 * 1024 * 1024; // 8MB
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Create chunks that together exceed the limit
    const chunk1 = 'a'.repeat(MAX_STDIN_SIZE - 100); // Just under limit
    const chunk2 = 'b'.repeat(200); // This pushes over the limit

    mockStdin.read
      .mockReturnValueOnce(chunk1)
      .mockReturnValueOnce(chunk2)
      .mockReturnValueOnce(null);

    const promise = readStdin();

    // Trigger readable event (processes both chunks)
    onReadableHandler();

    const result = await promise;

    // Should have exactly MAX_STDIN_SIZE bytes
    expect(result.length).toBe(MAX_STDIN_SIZE);
    // Should be chunk1 + 100 bytes of chunk2
    expect(result).toBe(chunk1 + 'b'.repeat(100));

    // Verify stream was destroyed
    expect(mockStdin.destroy).toHaveBeenCalledOnce();

    // Verify user warning was shown
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining('⚠️  Warning: Input too large'),
    );

    consoleErrorSpy.mockRestore();
  });
});
