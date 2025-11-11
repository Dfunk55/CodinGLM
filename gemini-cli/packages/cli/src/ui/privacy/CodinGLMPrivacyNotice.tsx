/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { Box, Newline, Text } from 'ink';
import { theme } from '../semantic-colors.js';
import { useKeypress } from '../hooks/useKeypress.js';

interface CodinGLMPrivacyNoticeProps {
  onExit: () => void;
}

export const CodinGLMPrivacyNotice = ({ onExit }: CodinGLMPrivacyNoticeProps) => {
  useKeypress(
    (key) => {
      if (key.name === 'escape') {
        onExit();
      }
    },
    { isActive: true },
  );

  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text bold color={theme.text.accent}>
        CodinGLM API Key Notice
      </Text>
      <Newline />
      <Text color={theme.text.primary}>
        By using the Zhipu AI (Z.AI) CodinGLM API
        <Text color={theme.text.link}>[1]</Text>, you agree to the Zhipu AI API
        Service Terms<Text color={theme.status.success}>[2]</Text> and Privacy
        Notice<Text color={theme.text.accent}>[3]</Text>. Keep your API key
        confidential and only use it with trusted tooling.
      </Text>
      <Newline />
      <Text color={theme.text.primary}>
        <Text color={theme.text.link}>[1]</Text>{' '}
        https://open.bigmodel.cn/usercenter/apikey
      </Text>
      <Text color={theme.text.primary}>
        <Text color={theme.status.success}>[2]</Text>{' '}
        https://open.bigmodel.cn/usercenter/protocol
      </Text>
      <Text color={theme.text.primary}>
        <Text color={theme.text.accent}>[3]</Text>{' '}
        https://open.bigmodel.cn/usercenter/privacy
      </Text>
      <Newline />
      <Text color={theme.text.secondary}>Press Esc to exit.</Text>
    </Box>
  );
};
