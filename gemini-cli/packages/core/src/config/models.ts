/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

// In CodinGLM, all defaults point to Z.AI GLM models.
export const DEFAULT_GEMINI_MODEL = 'glm-4.6';
export const DEFAULT_GEMINI_FLASH_MODEL = 'glm-4-flash';
export const DEFAULT_GEMINI_FLASH_LITE_MODEL = 'glm-4.5-air';

export const DEFAULT_GEMINI_MODEL_AUTO = 'auto';

// Placeholder; embeddings not supported via ZaiContentGenerator.
export const DEFAULT_GEMINI_EMBEDDING_MODEL = 'glm-embedding-001';

// Cap the thinking at 8192 to prevent run-away thinking loops.
export const DEFAULT_THINKING_MODE = 8192;

/**
 * Determines the effective model to use, applying fallback logic if necessary.
 *
 * When fallback mode is active, this function enforces the use of the standard
 * fallback model. However, it makes an exception for "lite" models (any model
 * with "lite" in its name), allowing them to be used to preserve cost savings.
 * This ensures that "pro" models are always downgraded, while "lite" model
 * requests are honored.
 *
 * @param isInFallbackMode Whether the application is in fallback mode.
 * @param requestedModel The model that was originally requested.
 * @returns The effective model name.
 */
export function getEffectiveModel(
  isInFallbackMode: boolean,
  requestedModel: string,
): string {
  // If we are not in fallback mode, simply use the requested model.
  if (!isInFallbackMode) {
    return requestedModel;
  }

  // In CodinGLM fallback mode, honor faster/cheaper variants if requested.
  if (requestedModel.includes('flash') || requestedModel.includes('air')) {
    return requestedModel;
  }

  // Default fallback for CodinGLM is GLM-4-Flash.
  return DEFAULT_GEMINI_FLASH_MODEL;
}
