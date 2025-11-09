/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { describe, expect, it, beforeEach, afterEach, vi } from 'vitest';
import type {
  GenerateContentParameters,
  GenerateContentResponse,
} from '@google/genai';
import { ZaiContentGenerator } from './zaiContentGenerator.js';

function createRequest(): GenerateContentParameters {
  return {
    model: 'glm-4.6',
    contents: [
      {
        role: 'user',
        parts: [{ text: 'Say hello.' }],
      },
    ],
  };
}

function createSseStream(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream<Uint8Array>({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk));
      }
      controller.close();
    },
  });
}

function expectDefined<T>(value: T | null | undefined): asserts value is T {
  expect(value).toBeDefined();
}

describe('ZaiContentGenerator', () => {
  const promptId = 'test-prompt';
  let originalFetch: typeof fetch;

  beforeEach(() => {
    originalFetch = globalThis.fetch;
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.resetAllMocks();
  });

  it('sends non-streaming requests and converts responses', async () => {
    const responsePayload = {
      id: 'resp_123',
      model: 'glm-4.6',
      choices: [
        {
          index: 0,
          message: {
            content: [{ type: 'text', text: 'Hello from GLM-4.6!' }],
          },
          finish_reason: 'stop',
        },
      ],
      usage: {
        prompt_tokens: 5,
        completion_tokens: 3,
        total_tokens: 8,
      },
    };

    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(responsePayload), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    globalThis.fetch = fetchMock as unknown as typeof fetch;

    const generator = new ZaiContentGenerator({ apiKey: 'fake-key' });
    const request = createRequest();
    const response = await generator.generateContent(request, promptId);

    expect(fetchMock).toHaveBeenCalledWith(
      'https://api.z.ai/api/paas/v4/chat/completions',
      expect.objectContaining({
        method: 'POST',
      }),
    );
    const candidate = response.candidates?.[0];
    expectDefined(candidate);
    const candidateContent = candidate.content;
    expectDefined(candidateContent);
    const firstPart = candidateContent.parts?.[0];
    expectDefined(firstPart);
    expect(firstPart.text).toBe('Hello from GLM-4.6!');
    expect(response.usageMetadata?.totalTokenCount).toBe(8);
  });

  it('streams reasoning and content updates', async () => {
    const events = [
      'data: {"id":"resp_stream","model":"glm-4.6","choices":[{"index":0,"delta":{"role":"assistant","reasoning_content":[{"type":"text","text":"Analyzing task"}]}}]}\n\n',
      'data: {"id":"resp_stream","choices":[{"index":0,"delta":{"content":[{"type":"text","text":"Final answer."}]}}]}\n\n',
      'data: {"id":"resp_stream","choices":[{"index":0,"finish_reason":"stop"}],"usage":{"prompt_tokens":12,"completion_tokens":5,"total_tokens":17,"thoughts_tokens":1}}\n\n',
      'data: [DONE]\n\n',
    ];
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(createSseStream(events), {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
      }),
    );
    globalThis.fetch = fetchMock as unknown as typeof fetch;

    const generator = new ZaiContentGenerator({ apiKey: 'fake-key' });
    const request = createRequest();

    const streamedResponses: GenerateContentResponse[] = [];
    const iterator = await generator.generateContentStream(request, promptId);
    for await (const chunk of iterator) {
      streamedResponses.push(chunk);
    }

    expect(streamedResponses).toHaveLength(3);

    const [maybeFirstChunk, maybeSecondChunk, maybeThirdChunk] =
      streamedResponses;
    expectDefined(maybeFirstChunk);
    expectDefined(maybeSecondChunk);
    expectDefined(maybeThirdChunk);

    const firstCandidate = maybeFirstChunk.candidates?.[0];
    expectDefined(firstCandidate);
    const firstContent = firstCandidate.content;
    expectDefined(firstContent);
    const reasoningParts = firstContent.parts ?? [];
    expect(
      reasoningParts.some(
        (part) => part.thought === true && part.text === 'Analyzing task',
      ),
    ).toBe(true);

    const secondCandidate = maybeSecondChunk.candidates?.[0];
    expectDefined(secondCandidate);
    const secondContent = secondCandidate.content;
    expectDefined(secondContent);
    const answerParts = secondContent.parts ?? [];
    expect(answerParts.find((part) => !part.thought)?.text).toBe(
      'Final answer.',
    );

    const thirdCandidate = maybeThirdChunk.candidates?.[0];
    expectDefined(thirdCandidate);
    expect(thirdCandidate.finishReason).toBe('STOP');
    expect(maybeThirdChunk.usageMetadata?.totalTokenCount).toBe(17);
    expect(maybeThirdChunk.usageMetadata?.thoughtsTokenCount).toBe(1);
  });

  it('streams tool call metadata', async () => {
    const events = [
      'data: {"id":"resp_tool","model":"glm-4.6","choices":[{"index":0,"delta":{"role":"assistant","tool_calls":[{"id":"call_1","type":"function","function":{"name":"write_file","arguments":"{\\"path\\":\\"/tmp/file\\",\\"content\\":\\"Hello\\"}"}}]}}]}\n\n',
      'data: {"id":"resp_tool","choices":[{"index":0,"delta":{"content":[{"type":"text","text":"Tool executed."}]}}]}\n\n',
      'data: {"id":"resp_tool","choices":[{"index":0,"finish_reason":"stop"}]}\n\n',
      'data: [DONE]\n\n',
    ];
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(createSseStream(events), {
        status: 200,
        headers: { 'Content-Type': 'text/event-stream' },
      }),
    );
    globalThis.fetch = fetchMock as unknown as typeof fetch;

    const generator = new ZaiContentGenerator({ apiKey: 'fake-key' });
    const request = createRequest();

    const iterator = await generator.generateContentStream(request, promptId);
    let lastChunk: GenerateContentResponse | null = null;
    for await (const chunk of iterator) {
      lastChunk = chunk;
    }

    expectDefined(lastChunk);
    const finalCandidate = lastChunk.candidates?.[0];
    expectDefined(finalCandidate);
    const finalContent = finalCandidate.content;
    expectDefined(finalContent);
    const parts = finalContent.parts ?? [];
    const functionCallPart = parts.find(
      (part) => part.functionCall !== undefined,
    );
    expect(functionCallPart?.functionCall?.name).toBe('write_file');
    expect(functionCallPart?.functionCall?.args).toEqual({
      path: '/tmp/file',
      content: 'Hello',
    });
  });
});
