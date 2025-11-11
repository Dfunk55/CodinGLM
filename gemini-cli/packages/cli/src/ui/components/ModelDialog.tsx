/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import type React from 'react';
import { useCallback, useContext, useMemo } from 'react';
import { Box, Text } from 'ink';
import {
  DEFAULT_GLM_MODEL_AUTO,
  DEFAULT_GLM_MODEL,
  DEFAULT_GLM_FLASH_MODEL,
  DEFAULT_GLM_FLASH_LITE_MODEL,
  ModelSlashCommandEvent,
  logModelSlashCommand,
} from '@codinglm/core';
import { useKeypress } from '../hooks/useKeypress.js';
import { theme } from '../semantic-colors.js';
import { DescriptiveRadioButtonSelect } from './shared/DescriptiveRadioButtonSelect.js';
import { ConfigContext } from '../contexts/ConfigContext.js';

interface ModelDialogProps {
  onClose: () => void;
}

// Z.AI GLM model options shown in the selector.
// Model IDs follow Z.AI API naming (lowercase, dashed).
const MODEL_OPTIONS = [
  {
    value: DEFAULT_GLM_MODEL_AUTO, // 'auto'
    title: 'Auto (recommended)',
    description:
      'Let CodinGLM choose between GLM‑4.6, 4.5‑Air, and 4‑Flash',
    key: DEFAULT_GLM_MODEL_AUTO,
  },
  {
    value: DEFAULT_GLM_MODEL,
    title: 'GLM‑4.6',
    description:
      'Best for complex reasoning, debugging, and multi‑file refactors',
    key: DEFAULT_GLM_MODEL,
  },
  {
    value: DEFAULT_GLM_FLASH_LITE_MODEL,
    title: 'GLM‑4.5‑Air',
    description: 'Fast and balanced; great for everyday coding tasks',
    key: DEFAULT_GLM_FLASH_LITE_MODEL,
  },
  {
    value: DEFAULT_GLM_FLASH_MODEL,
    title: 'GLM‑4‑Flash',
    description: 'Lowest latency for simple edits and quick queries',
    key: DEFAULT_GLM_FLASH_MODEL,
  },
];

export function ModelDialog({ onClose }: ModelDialogProps): React.JSX.Element {
  const config = useContext(ConfigContext);

  // Determine the Preferred Model (read once when the dialog opens).
  const preferredModel = config?.getModel() || DEFAULT_GLM_MODEL_AUTO;

  useKeypress(
    (key) => {
      if (key.name === 'escape') {
        onClose();
      }
    },
    { isActive: true },
  );

  // Calculate the initial index based on the preferred model.
  const initialIndex = useMemo(
    () => MODEL_OPTIONS.findIndex((option) => option.value === preferredModel),
    [preferredModel],
  );

  // Handle selection internally (Autonomous Dialog).
  const handleSelect = useCallback(
    (model: string) => {
      if (config) {
        config.setModel(model);
        const event = new ModelSlashCommandEvent(model);
        logModelSlashCommand(config, event);
      }
      onClose();
    },
    [config, onClose],
  );

  return (
    <Box
      borderStyle="round"
      borderColor={theme.border.default}
      flexDirection="column"
      padding={1}
      width="100%"
    >
      <Text bold>Select GLM Model</Text>
      <Box marginTop={1}>
        <DescriptiveRadioButtonSelect
          items={MODEL_OPTIONS}
          onSelect={handleSelect}
          initialIndex={initialIndex}
          showNumbers={true}
        />
      </Box>
      <Box flexDirection="column">
        <Text color={theme.text.secondary}>
          {
            '> To use a specific GLM model on startup, use the --model flag.'
          }
        </Text>
      </Box>
      <Box marginTop={1} flexDirection="column">
        <Text color={theme.text.secondary}>(Press Esc to close)</Text>
      </Box>
    </Box>
  );
}
