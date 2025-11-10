/**
 * Lightweight shim for @google/genai to support legacy compiled paths
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
  constructor(public status?: number) {
    super('ApiError');
    this.name = 'ApiError';
  }
}

// Minimal function calling config enum
export const FunctionCallingConfigMode = {
  AUTO: 'AUTO',
  ANY: 'ANY',
  NONE: 'NONE',
} as const;

// No-op MCP conversion placeholder (legacy import path)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function mcpToTool(_tool: any): any {
  return _tool;
}

