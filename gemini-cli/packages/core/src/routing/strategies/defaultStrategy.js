/**
 * @license
 * Copyright 2025 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
export class DefaultStrategy {
    name = 'default';
    async route(_context, config, _baseLlmClient) {
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
//# sourceMappingURL=defaultStrategy.js.map