/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import type { Config } from '../../config/config.js';
import type { BaseLlmClient } from '../../core/baseLlmClient.js';
import type {
  RoutingContext,
  RoutingDecision,
  TerminalStrategy,
} from '../routingStrategy.js';

export class DefaultStrategy implements TerminalStrategy {
  readonly name = 'default';

  async route(
    _context: RoutingContext,
    config: Config,
    _baseLlmClient: BaseLlmClient,
  ): Promise<RoutingDecision> {
    const model = config.getModel();
    return {
      model,
      metadata: {
        source: this.name,
        latencyMs: 0,
        reasoning: `Routing to configured model: ${model}`,
      },
    };
  }
}
