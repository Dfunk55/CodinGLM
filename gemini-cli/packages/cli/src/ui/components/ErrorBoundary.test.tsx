/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from 'ink-testing-library';
import React from 'react';
import { Text } from 'ink';
import { ErrorBoundary } from './ErrorBoundary.js';

// Component that throws an error
function ThrowError({ shouldThrow }: { shouldThrow: boolean }): JSX.Element {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <Text>Success</Text>;
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    // Suppress console.error for these tests since we're intentionally throwing errors
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('should render children when no error occurs', () => {
    const { lastFrame } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>,
    );

    expect(lastFrame()).toContain('Success');
  });

  it('should render default fallback UI when error occurs', () => {
    const { lastFrame } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    const frame = lastFrame();
    expect(frame).toContain('An unexpected error occurred');
    expect(frame).toContain('Test error');
  });

  it('should call onError callback when error occurs', () => {
    const onError = vi.fn();

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(onError).toHaveBeenCalledTimes(1);
    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String),
      }),
    );

    const [error] = onError.mock.calls[0];
    expect(error.message).toBe('Test error');
  });

  it('should render custom fallback when provided', () => {
    const customFallback = (error: Error) => (
      <Text>Custom error: {error.message}</Text>
    );

    const { lastFrame } = render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(lastFrame()).toContain('Custom error: Test error');
  });

  it('should display stack trace in default fallback', () => {
    const { lastFrame } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    const frame = lastFrame();
    expect(frame).toContain('Stack trace:');
  });

  it('should handle errors with no stack trace', () => {
    function ThrowErrorNoStack(): JSX.Element {
      const error = new Error('Error without stack');
      error.stack = undefined;
      throw error;
    }

    const { lastFrame } = render(
      <ErrorBoundary>
        <ThrowErrorNoStack />
      </ErrorBoundary>,
    );

    const frame = lastFrame();
    expect(frame).toContain('An unexpected error occurred');
    expect(frame).toContain('Error without stack');
  });

  it('should continue to show error after re-render', () => {
    const { lastFrame, rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(lastFrame()).toContain('An unexpected error occurred');

    // Re-render should still show error
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    expect(lastFrame()).toContain('An unexpected error occurred');
  });

  it('should provide helpful error message in default fallback', () => {
    const { lastFrame } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>,
    );

    const frame = lastFrame();
    expect(frame).toContain('Press Ctrl+C to exit');
    expect(frame).toContain('Check the logs for more information');
  });
});
