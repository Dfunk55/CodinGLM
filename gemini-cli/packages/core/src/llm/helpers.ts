/**
 * Internal LLM helpers for CodinGLM.
 */

import type { Content, Part, PartListUnion, PartUnion } from './types.js';

export function createPartFromText(text: string): Part {
  return { text };
}

export function toParts(parts: PartListUnion): Part[] {
  return parts.map((p) => (typeof p === 'string' ? { text: p } : p));
}

export function createUserContent(input: PartListUnion | string): Content {
  const partsArray: Part[] = Array.isArray(input)
    ? toParts(input)
    : typeof input === 'string'
      ? [{ text: input }]
      : [input as Part];
  return { role: 'user', parts: partsArray };
}

