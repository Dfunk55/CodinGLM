/**
 * Lightweight shim for @codinglm/genai to support legacy compiled paths
 * during the CodinGLM refactor. This surfaces only the identifiers
 * referenced by historical JS outputs so bundling succeeds.
 */

export { FinishReason, GenerateContentResponse } from '../llm/types.js';
export type { Content, Part, FunctionDeclaration } from '../llm/types.js';
export { createUserContent } from '../llm/helpers.js';
export { Type } from '../llm/schema.js';

// Minimal stand-ins for SDK-specific exports used in legacy code
export class EmbedContentResponse {}
export class ApiError extends Error {
  status?: number;
  override cause?: unknown;

  constructor(init?: { status?: number; message?: string; cause?: unknown }) {
    super(init?.message ?? 'ApiError');
    this.name = 'ApiError';
    this.status = init?.status;
    this.cause = init?.cause;
  }
}

// Minimal function calling config enum
export const FunctionCallingConfigMode = {
  AUTO: 'AUTO',
  ANY: 'ANY',
  NONE: 'NONE',
} as const;

// Minimal MCP conversion helper used by the CodinGLM CLI.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function mcpToTool(
  mcpClient: any,
  _options?: { timeout?: number },
): any {
  return {
    async tool(): Promise<{ functionDeclarations?: any[] }> {
      try {
        const resp = await mcpClient.request(
          { method: 'tools/list', params: {} },
          undefined,
        );
        const tools = Array.isArray(resp?.tools) ? resp.tools : [];
        return {
          functionDeclarations: tools.map((tool: any) => ({
            name: tool?.name,
            description: tool?.description,
            parametersJsonSchema: tool?.inputSchema ?? {
              type: 'object',
              properties: {},
            },
          })),
        };
      } catch {
        return { functionDeclarations: [] };
      }
    },
    async callTool(functionCalls: any[]) {
      const call = functionCalls?.[0];
      try {
        const response = await mcpClient.request(
          {
            method: 'tools/call',
            params: { name: call?.name, arguments: call?.args },
          },
          undefined,
        );
        return [
          {
            functionResponse: {
              name: call?.name,
              response: response ?? {},
            },
          },
        ];
      } catch (error) {
        return [
          {
            functionResponse: {
              name: call?.name,
              response: {
                error: { isError: true, message: String(error) },
              },
            },
          },
        ];
      }
    },
  };
}
