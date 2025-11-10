/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
export declare const DEFAULT_GEMINI_MODEL = "glm-4.6";
export declare const DEFAULT_GEMINI_FLASH_MODEL = "glm-4-flash";
export declare const DEFAULT_GEMINI_FLASH_LITE_MODEL = "glm-4.5-air";
export declare const DEFAULT_GEMINI_MODEL_AUTO = "auto";
export declare const DEFAULT_GEMINI_EMBEDDING_MODEL = "glm-embedding-001";
export declare const DEFAULT_THINKING_MODE = 8192;
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
export declare function getEffectiveModel(isInFallbackMode: boolean, requestedModel: string): string;
