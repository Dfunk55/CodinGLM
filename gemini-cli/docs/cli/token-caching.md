# Token Caching and Cost Optimization

CodinGLM CLI automatically optimizes API costs through token caching when using
API key authentication (CodinGLM API key or Vertex AI). This feature reuses
previous system instructions and context to reduce the number of tokens
processed in subsequent requests.

**Token caching is available for:**

- API key users (CodinGLM API key)
- Vertex AI users (with project and location setup)

**Token caching is not available for:**

- OAuth users (legacy personal/enterprise accounts) - the Code Assist API does
  not support cached content creation at this time

You can view your token usage and cached token savings using the `/stats`
command. When cached tokens are available, they will be displayed in the stats
output.
