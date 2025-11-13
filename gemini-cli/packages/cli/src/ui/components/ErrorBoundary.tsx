/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { Component, ReactNode } from 'react';
import { Box, Text } from 'ink';
import { debugLogger } from '@codinglm/core';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: (error: Error, errorInfo: React.ErrorInfo) => ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * Error Boundary component that catches rendering errors and displays a fallback UI.
 *
 * This prevents the entire application from crashing when a component throws an error.
 * Errors are logged using the debug logger and can optionally be reported via onError callback.
 */
export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log the error
    debugLogger.error('UI Error caught by ErrorBoundary:', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });

    // Update state with error info
    this.setState({
      errorInfo,
    });

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  render(): ReactNode {
    if (this.state.hasError && this.state.error) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.state.errorInfo!);
      }

      // Default fallback UI
      return <DefaultErrorFallback error={this.state.error} />;
    }

    return this.props.children;
  }
}

interface DefaultErrorFallbackProps {
  error: Error;
}

/**
 * Default fallback UI displayed when an error occurs.
 */
function DefaultErrorFallback({ error }: DefaultErrorFallbackProps): JSX.Element {
  return (
    <Box flexDirection="column" paddingX={2} paddingY={1}>
      <Box marginBottom={1}>
        <Text bold color="red">
          ⚠️  An unexpected error occurred
        </Text>
      </Box>

      <Box marginBottom={1}>
        <Text color="gray">
          The application encountered an error and cannot continue. Please restart.
        </Text>
      </Box>

      <Box flexDirection="column" borderStyle="round" borderColor="red" paddingX={1}>
        <Text bold>Error Details:</Text>
        <Text color="red">{error.message}</Text>

        {error.stack && (
          <Box marginTop={1} flexDirection="column">
            <Text dimColor>Stack trace:</Text>
            <Text dimColor>
              {error.stack.split('\n').slice(0, 5).join('\n')}
            </Text>
          </Box>
        )}
      </Box>

      <Box marginTop={1}>
        <Text dimColor>
          Check the logs for more information. Press Ctrl+C to exit.
        </Text>
      </Box>
    </Box>
  );
}
