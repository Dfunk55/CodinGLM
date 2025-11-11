/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { Box, Newline, Text } from 'ink';
import { RadioButtonSelect } from '../components/shared/RadioButtonSelect.js';
import { usePrivacySettings } from '../hooks/usePrivacySettings.js';

import type { Config } from '@codinglm/core';
import { theme } from '../semantic-colors.js';
import { useKeypress } from '../hooks/useKeypress.js';

interface CloudFreePrivacyNoticeProps {
  config: Config;
  onExit: () => void;
}

export const CloudFreePrivacyNotice = ({
  config,
  onExit,
}: CloudFreePrivacyNoticeProps) => {
  const { privacyState, updateDataCollectionOptIn } =
    usePrivacySettings(config);

  useKeypress(
    (key) => {
      if (
        (privacyState.error || privacyState.isFreeTier === false) &&
        key.name === 'escape'
      ) {
        onExit();
      }
    },
    { isActive: true },
  );

  if (privacyState.isLoading) {
    return <Text color={theme.text.secondary}>Loading...</Text>;
  }

  if (privacyState.error) {
    return (
      <Box flexDirection="column" marginY={1}>
        <Text color={theme.status.error}>
          Error loading Opt-in settings: {privacyState.error}
        </Text>
        <Text color={theme.text.secondary}>Press Esc to exit.</Text>
      </Box>
    );
  }

  if (privacyState.isFreeTier === false) {
    return (
      <Box flexDirection="column" marginY={1}>
        <Text bold color={theme.text.accent}>
          CodinGLM Privacy Notice
        </Text>
        <Newline />
        <Text>https://open.bigmodel.cn/usercenter/privacy</Text>
        <Newline />
        <Text color={theme.text.secondary}>Press Esc to exit.</Text>
      </Box>
    );
  }

  const items = [
    { label: 'Yes', value: true, key: 'true' },
    { label: 'No', value: false, key: 'false' },
  ];

  return (
    <Box flexDirection="column" marginY={1}>
      <Text bold color={theme.text.accent}>
        CodinGLM Privacy & Data Collection Notice
      </Text>
      <Newline />
      <Text color={theme.text.primary}>
        This notice and the Zhipu AI Privacy Policy
        <Text color={theme.text.link}>[1]</Text> describe how CodinGLM (powered
        by Zhipu AI) handles your data. Please read them carefully.
      </Text>
      <Newline />
      <Text color={theme.text.primary}>
        When you use CodinGLM with Zhipu AI, Zhipu AI may collect your prompts,
        related code, generated output, code edits, feature usage information,
        and feedback to provide, improve, and develop its services and machine
        learning technologies.
      </Text>
      <Newline />
      <Text color={theme.text.primary}>
        To help with quality and improve CodinGLM experiences, reviewers within
        Zhipu AI may read, annotate, and process the data collected above. Data
        is handled according to the Zhipu AI Privacy Policy. Avoid submitting
        confidential information or anything you do not want a reviewer to see
        or Zhipu AI to use to improve its services.
      </Text>
      <Newline />
      <Box flexDirection="column">
        <Text color={theme.text.primary}>
          Allow Zhipu AI to use this data to develop and improve its products?
        </Text>
        <RadioButtonSelect
          items={items}
          initialIndex={privacyState.dataCollectionOptIn ? 0 : 1}
          onSelect={(value) => {
            updateDataCollectionOptIn(value);
            // Only exit if there was no error.
            if (!privacyState.error) {
              onExit();
            }
          }}
        />
      </Box>
      <Newline />
      <Text>
        <Text color={theme.text.link}>[1]</Text>{' '}
        https://open.bigmodel.cn/usercenter/privacy
      </Text>
      <Newline />
      <Text color={theme.text.secondary}>
        Press Enter to choose an option and exit.
      </Text>
    </Box>
  );
};
