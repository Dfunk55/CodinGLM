/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { useIsScreenReaderEnabled } from 'ink';
import { useUIState } from './contexts/UIStateContext.js';
import { StreamingContext } from './contexts/StreamingContext.js';
import { QuittingDisplay } from './components/QuittingDisplay.js';
import { ScreenReaderAppLayout } from './layouts/ScreenReaderAppLayout.js';
import { DefaultAppLayout } from './layouts/DefaultAppLayout.js';
import { ErrorBoundary } from './components/ErrorBoundary.js';
import { debugLogger } from '@codinglm/core';

export const App = () => {
  const uiState = useUIState();
  const isScreenReaderEnabled = useIsScreenReaderEnabled();

  if (uiState.quittingMessages) {
    return <QuittingDisplay />;
  }

  return (
    <ErrorBoundary
      onError={(error, errorInfo) => {
        debugLogger.error('Fatal UI error:', {
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
        });
      }}
    >
      <StreamingContext.Provider value={uiState.streamingState}>
        {isScreenReaderEnabled ? <ScreenReaderAppLayout /> : <DefaultAppLayout />}
      </StreamingContext.Provider>
    </ErrorBoundary>
  );
};
