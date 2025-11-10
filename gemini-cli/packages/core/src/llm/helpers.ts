/**
 * Internal LLM helpers for CodinGLM.
 */

import type { Content, Part, PartListUnion } from './types.js';

export function createPartFromText(text: string): Part {
  return { text };
}

export function toParts(parts: PartListUnion): Part[] {
  if (Array.isArray(parts)) {
    return parts.map((p) => (typeof p === 'string' ? { text: p } : (p as Part)));
  }
  // If a raw string was provided, wrap it as a single text part
  if (typeof parts === 'string') {
    return [{ text: parts }];
  }
  return [];
}

export function createUserContent(input: PartListUnion | string): Content {
  const partsArray: Part[] = Array.isArray(input)
    ? toParts(input)
    : typeof input === 'string'
      ? [{ text: input }]
      : [input as Part];
  return { role: 'user', parts: partsArray };
}
