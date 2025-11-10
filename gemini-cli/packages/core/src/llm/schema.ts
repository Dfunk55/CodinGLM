/**
 * Minimal JSON schema Type constants used across the codebase.
 */

export const Type = {
  OBJECT: 'object',
  STRING: 'string',
  NUMBER: 'number',
  BOOLEAN: 'boolean',
  ARRAY: 'array',
} as const;

export type Schema = Record<string, unknown>;

