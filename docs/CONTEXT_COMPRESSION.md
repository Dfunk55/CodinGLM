# Context Compression System

## Overview

The context compression system in CodinGLM automatically manages conversation history to stay within token limits while preserving important context. When the conversation grows too large, older messages are summarized into compact representations, allowing you to have longer coding sessions without losing continuity.

## How It Works

### Compression Process

1. **Monitoring**: After each turn (user message, assistant response, or tool execution), the system checks if the total token count exceeds `maxContextTokens`

2. **Selection**: If compression is needed, the system:
   - Preserves the system prompt (never compressed)
   - Preserves the most recent `preserveRecentMessages` messages
   - Selects older messages for summarization

3. **Summarization**: Selected messages are sent to the AI model (or a cheaper `summaryModel` if configured) to generate a concise summary

4. **Replacement**: The summary replaces the original messages, reducing token usage while retaining key information

5. **Iteration**: If still above `targetContextTokens`, the process repeats (up to `maxCompressionPasses` times)

### Convergence Protection

The system includes a convergence check that stops compression if insufficient progress is made (< 10% token reduction per pass). This prevents wasteful API calls when compression isn't effective.

## Configuration

### Default Settings

Default values maximize GLM-4.6's 200K context window for subscription users:

```json
{
  "context": {
    "compression": {
      "enabled": true,
      "maxContextTokens": 185000,
      "targetContextTokens": 165000,
      "preserveRecentMessages": 15,
      "summaryMaxTokens": 2000,
      "summaryModel": null,
      "maxCompressionPasses": 3,
      "verbose": false
    }
  }
}
```

These aggressive defaults use 92.5% of GLM-4.6's context window, optimized for:
- **Longest possible coding sessions** before compression triggers
- **Maximum context retention** with 15 preserved recent messages
- **Detailed summaries** (2K tokens) when compression is needed
- **Subscription plans** where API costs aren't a concern

Leaves 15K tokens for output generation and safety margin.

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable automatic compression |
| `maxContextTokens` | integer | `185000` | Token limit that triggers compression |
| `targetContextTokens` | integer | `165000` | Target token count after compression |
| `preserveRecentMessages` | integer | `15` | Number of recent messages to keep intact (min: 1) |
| `summaryMaxTokens` | integer | `2000` | Maximum tokens for each summary |
| `summaryModel` | string | `null` | Optional cheaper model for summaries (e.g., `"glm-4-flash"`) |
| `maxCompressionPasses` | integer | `3` | Maximum compression iterations per trigger |
| `verbose` | boolean | `false` | Show detailed compression logs |

### Configuration File

Example custom settings in `.codinglm.json`:

```json
{
  "context": {
    "compression": {
      "maxContextTokens": 195000,
      "targetContextTokens": 180000,
      "preserveRecentMessages": 20,
      "summaryMaxTokens": 3000,
      "verbose": true
    }
  }
}
```

For pay-per-token users who want to reduce costs, override with lower values:

```json
{
  "context": {
    "compression": {
      "maxContextTokens": 50000,
      "targetContextTokens": 40000,
      "preserveRecentMessages": 8,
      "summaryMaxTokens": 800,
      "summaryModel": "glm-4-flash"
    }
  }
}
```

## Tuning Guidelines

### For Absolute Maximum Context (Subscription Users)

If you want to push GLM-4.6 to its absolute limit:

```json
{
  "maxContextTokens": 195000,
  "targetContextTokens": 180000,
  "preserveRecentMessages": 20,
  "summaryMaxTokens": 3000
}
```

**Benefits:**
- ✅ Use 97.5% of GLM-4.6's 200K context
- ✅ Extremely long coding sessions
- ✅ Maximum recent context retention
- ✅ Highly detailed summaries
- ⚠️ May occasionally hit context limits with very long outputs

### For Pay-Per-Token Users (Cost Optimization)

If you're on pay-per-token pricing and want to reduce costs:

```json
{
  "maxContextTokens": 50000,
  "targetContextTokens": 40000,
  "summaryModel": "glm-4-flash",
  "preserveRecentMessages": 8,
  "summaryMaxTokens": 800
}
```

**Benefits:**
- ✅ Significantly lower API costs
- ✅ Faster responses
- ✅ Still 4x larger than legacy models
- ⚠️ More frequent compressions
- ⚠️ Less preserved recent context

### For Ultra-Long Sessions (Multi-Day Projects)

To preserve maximum continuity across extended coding sessions:

```json
{
  "preserveRecentMessages": 25,
  "maxContextTokens": 190000,
  "targetContextTokens": 175000,
  "summaryMaxTokens": 3500,
  "maxCompressionPasses": 5
}
```

**Benefits:**
- ✅ Preserve up to 25 recent message pairs verbatim
- ✅ Very detailed summaries for better context
- ✅ Multiple compression passes for large backlogs
- ✅ Best continuity for complex, multi-day projects

## Token Counting

### Accurate Counting (Recommended, Optional)

The system can use `tiktoken` for accurate token counting when available. **Note**: tiktoken is optional and the system works perfectly fine without it.

```bash
# Install with:
poetry add tiktoken

# Or with pip:
pip install tiktoken
```

**⚠️ Compatibility Note**: tiktoken may have issues with Python 3.14+ due to PyO3 version constraints. If installation fails, the system will automatically use the heuristic fallback.

With tiktoken installed, you get:
- ✅ Exact token counts matching the API
- ✅ Better compression decisions
- ✅ Fewer surprises with token limits

### Fallback Heuristic (Default)

Without tiktoken, the system uses a simple heuristic (characters ÷ 4):
- ⚠️ Less accurate for code and special characters
- ⚠️ May trigger compression too early or too late
- ✅ No additional dependencies required
- ✅ Fast computation
- ✅ Works on all Python versions

The fallback is used automatically when:
- tiktoken is not installed
- tiktoken import fails
- tiktoken encounters an encoding error

## Monitoring Compression

### Viewing Compression Events

Enable verbose mode to see when compression occurs:

```json
{
  "context": {
    "compression": {
      "verbose": true
    }
  }
}
```

You'll see messages like:
```
Context compressed (removed 12 messages ≈4,523 tokens; trigger: tool_execution).
```

### Manual Compression

Use the `/compact` command to manually trigger compression at any time:

```
> /compact
✓ Context compressed
Removed: 8 messages
Tokens: 52,340 → 18,120 (saved 34,220, 65.4%)
```

This is useful for:
- Preparing for a new phase of work
- Freeing up context before starting a complex task
- Testing compression settings
- Managing context proactively on subscription plans

### Programmatic Access to Metrics

In the API, you can access compression metrics:

```python
from codinglm.conversation import ConversationManager

manager = ConversationManager(client, registry, console)
# ... run some conversations ...

metrics = manager.compressor.get_metrics()
print(metrics)
# Output: Compressions: 3 | Messages compressed: 42 | Tokens saved: 8,234 (72.3%) | API: 3 | Fallback: 0
```

### Available Metrics

- `total_compressions`: Number of compression events
- `total_messages_compressed`: Total messages replaced with summaries
- `total_tokens_before`: Total tokens before all compressions
- `total_tokens_after`: Total tokens after all compressions
- `api_calls_successful`: Number of API-based summaries
- `fallback_summaries_used`: Number of fallback summaries

## Troubleshooting

### Problem: Compression Happening Too Frequently

**Symptoms**: You see compression messages after every few turns

**Solutions**:
1. Increase `maxContextTokens`:
   ```json
   {"maxContextTokens": 16000}
   ```
2. Decrease `preserveRecentMessages`:
   ```json
   {"preserveRecentMessages": 5}
   ```
3. Use a cheaper summary model to reduce impact:
   ```json
   {"summaryModel": "glm-4-flash"}
   ```

### Problem: Running Out of Context Despite Compression

**Symptoms**: "Context compression skipped: only N messages"

**Solutions**:
1. Reduce `preserveRecentMessages`:
   ```json
   {"preserveRecentMessages": 4}
   ```
2. Increase `maxCompressionPasses`:
   ```json
   {"maxCompressionPasses": 5}
   ```
3. Clear history manually: `/clear` command

### Problem: Losing Important Context

**Symptoms**: The assistant forgets recent details

**Solutions**:
1. Increase `preserveRecentMessages`:
   ```json
   {"preserveRecentMessages": 12}
   ```
2. Increase `summaryMaxTokens` for more detailed summaries:
   ```json
   {"summaryMaxTokens": 800}
   ```
3. Increase both token limits:
   ```json
   {
     "maxContextTokens": 15000,
     "targetContextTokens": 12000
   }
   ```

### Problem: Summaries Not Helpful

**Symptoms**: Assistant asks you to repeat information

**Solutions**:
1. Use a more capable summary model:
   ```json
   {"summaryModel": "glm-4.6"}
   ```
2. Increase `summaryMaxTokens`:
   ```json
   {"summaryMaxTokens": 1000}
   ```
3. Reduce compression frequency by increasing `maxContextTokens`

### Problem: High API Costs from Summarization

**Symptoms**: Many compression events, high bills

**Solutions**:
1. Use cheaper model for summaries:
   ```json
   {"summaryModel": "glm-4-flash"}
   ```
2. Reduce compression passes:
   ```json
   {"maxCompressionPasses": 1}
   ```
3. Accept larger contexts to compress less often:
   ```json
   {"maxContextTokens": 18000}
   ```

## Advanced Topics

### Summary Protection

Summaries are tagged with a unique marker to prevent:
- Infinite compression loops
- Accidental compression of summaries
- Name collision attacks

Each compression session uses a unique marker (e.g., `context_summary:a7b3c9d2`) that persists for the session lifetime.

### Fallback Mechanism

If the API is unavailable or fails, the system generates a local fallback summary:
- Extracts first 160 characters from each message
- Includes up to 10 message snippets
- Preserves role labels (user, assistant, tool)

This ensures compression continues even with network issues.

### Validation

Configuration values are validated on load:
- `maxContextTokens` > `targetContextTokens`
- `preserveRecentMessages` ≥ 1
- All token/pass counts > 0

Invalid configurations raise clear error messages.

## Best Practices

1. **Consider installing tiktoken** (optional): Get accurate token counts if compatible
   ```bash
   poetry add tiktoken  # Skip if Python 3.14+ or installation fails
   ```

2. **Enable verbose mode during tuning**: See what's happening
   ```json
   {"verbose": true}
   ```

3. **Start with defaults**: Only tune if you have specific needs

4. **Use flash model for summaries**: Save costs without sacrificing much quality
   ```json
   {"summaryModel": "glm-4-flash"}
   ```

5. **Monitor metrics**: Track compression effectiveness
   ```python
   metrics = manager.compressor.get_metrics()
   print(f"Saved {metrics.get_tokens_saved()} tokens ({metrics.get_compression_ratio():.1%})")
   ```

6. **Clear history for new tasks**: Start fresh with `/clear`

7. **Preserve more messages for complex tasks**: Increase `preserveRecentMessages` when working on intricate problems

## Implementation Details

### File Locations

- **Core logic**: `codinglm/conversation/compression.py`
- **Configuration**: `codinglm/config.py` (`ContextCompressionConfig`)
- **Integration**: `codinglm/conversation/manager.py`
- **Token counting**: `codinglm/utils/token_counter.py`

### Constants

Compression behavior is controlled by constants in `compression.py`:

| Constant | Value | Description |
|----------|-------|-------------|
| `MIN_SUMMARY_CHARS` | 200 | Minimum summary length |
| `CHARS_PER_TOKEN_ESTIMATE` | 4 | Heuristic conversion ratio |
| `FALLBACK_MAX_SNIPPETS` | 10 | Max snippets in fallback |
| `FALLBACK_SNIPPET_LENGTH` | 160 | Characters per snippet |
| `MIN_COMPRESSION_REDUCTION_RATIO` | 0.10 | Minimum 10% reduction to continue |

### Compression Triggers

Compression is checked after:
- User sends a message (`trigger="user"`)
- Assistant responds (`trigger="assistant"`)
- Tool executes (`trigger=<tool_name>`)

## FAQ

**Q: Does compression affect response quality?**
A: The AI receives summaries instead of full messages, which may reduce context quality. However, summaries capture key points, and recent messages are preserved verbatim.

**Q: Can I disable compression?**
A: Yes, set `"enabled": false` in configuration. Not recommended for long sessions.

**Q: Do I need to install tiktoken?**
A: No, tiktoken is optional. The system works fine with the heuristic fallback. tiktoken provides 10-20% better accuracy but may not install on Python 3.14+.

**Q: How much does tiktoken improve accuracy?**
A: Typically 10-20% more accurate, especially for code-heavy conversations with mixed content types. However, the heuristic fallback is sufficient for most use cases.

**Q: What's the performance impact?**
A: Minimal - token counting is fast, and compression only runs when needed. Summarization adds one API call per compression event.

**Q: Can I see the summaries?**
A: Yes, they're stored in the message history with `name="context_summary:<unique_id>"`. Enable verbose mode to see compression details.

**Q: Does compression work offline?**
A: Yes, the fallback mechanism creates summaries locally if the API is unavailable.

## See Also

- [Configuration Guide](./CONFIGURATION.md)
- [Lessons Learned](./LESSONS.md)
- [API Documentation](./API.md)
