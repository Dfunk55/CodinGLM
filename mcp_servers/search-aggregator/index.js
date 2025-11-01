#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { fetch } from 'undici';

const server = new Server({
  name: 'search-aggregator-mcp',
  version: '0.1.0',
  description: 'Unified multi-provider search'
}, { capabilities: { tools: {} } });

const providers = {
  tavily: {
    enabled: !!process.env.TAVILY_API_KEY,
    search: async (query, opts) => {
      const body = {
        api_key: process.env.TAVILY_API_KEY,
        query,
        include_answer: false,
        max_results: opts.limit || 10,
        search_depth: 'advanced',
        ...(opts.timeRange ? { days: opts.timeRange } : {}),
        ...(opts.site ? { query: `${query} site:${opts.site}` } : {})
      };
      const res = await fetch('https://api.tavily.com/search', {
        method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error(`tavily HTTP ${res.status}`);
      const data = await res.json();
      return (data.results || []).map(r => ({
        provider: 'tavily', title: r.title, url: r.url, snippet: r.content || r.snippet || '',
        score: r.score || undefined
      }));
    }
  },
  exa: {
    enabled: !!process.env.EXA_API_KEY,
    search: async (query, opts) => {
      const res = await fetch('https://api.exa.ai/search', {
        method: 'POST',
        headers: { 'content-type': 'application/json', 'authorization': `Bearer ${process.env.EXA_API_KEY}` },
        body: JSON.stringify({ query, numResults: opts.limit || 10 })
      });
      if (!res.ok) throw new Error(`exa HTTP ${res.status}`);
      const data = await res.json();
      return (data.results || []).map(r => ({ provider: 'exa', title: r.title, url: r.url, snippet: r.text || r.snippet || '' }));
    }
  },
  brave: {
    enabled: !!process.env.BRAVE_API_KEY,
    search: async (query, opts) => {
      const u = new URL('https://api.search.brave.com/res/v1/web/search');
      u.searchParams.set('q', query);
      u.searchParams.set('count', String(opts.limit || 10));
      if (opts.safe) u.searchParams.set('safesearch', 'strict');
      const res = await fetch(u, { headers: { 'X-Subscription-Token': process.env.BRAVE_API_KEY } });
      if (!res.ok) throw new Error(`brave HTTP ${res.status}`);
      const data = await res.json();
      const web = data.web?.results || [];
      return web.map(r => ({ provider: 'brave', title: r.title, url: r.url, snippet: r.description || '' }));
    }
  },
  bing: {
    enabled: !!process.env.BING_API_KEY,
    search: async (query, opts) => {
      const u = new URL('https://api.bing.microsoft.com/v7.0/search');
      u.searchParams.set('q', query);
      u.searchParams.set('count', String(opts.limit || 10));
      const res = await fetch(u, { headers: { 'Ocp-Apim-Subscription-Key': process.env.BING_API_KEY } });
      if (!res.ok) throw new Error(`bing HTTP ${res.status}`);
      const data = await res.json();
      const web = data.webPages?.value || [];
      return web.map(r => ({ provider: 'bing', title: r.name, url: r.url, snippet: r.snippet || '' }));
    }
  },
  serpapi: {
    enabled: !!process.env.SERPAPI_KEY,
    search: async (query, opts) => {
      const u = new URL('https://serpapi.com/search.json');
      u.searchParams.set('engine', 'google');
      u.searchParams.set('q', query);
      u.searchParams.set('api_key', process.env.SERPAPI_KEY);
      const res = await fetch(u);
      if (!res.ok) throw new Error(`serpapi HTTP ${res.status}`);
      const data = await res.json();
      const results = data.organic_results || [];
      return results.slice(0, opts.limit || 10).map(r => ({ provider: 'serpapi', title: r.title, url: r.link, snippet: r.snippet || '' }));
    }
  }
};

function dedup(results) {
  const seen = new Map();
  for (const r of results) {
    const key = (r.url || '').replace(/[#?].*$/, '').toLowerCase();
    if (!seen.has(key)) seen.set(key, r); else {
      const prev = seen.get(key);
      seen.set(key, { ...prev, provider: `${prev.provider},${r.provider}` });
    }
  }
  return Array.from(seen.values());
}

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'search',
      description: 'Aggregate web search across multiple providers',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string' },
          providers: { type: 'array', items: { type: 'string' } },
          limit: { type: 'number' },
          timeRange: { type: 'number', description: 'days' },
          site: { type: 'string' },
          safe: { type: 'boolean' },
          rerank: { type: 'boolean' }
        }, required: ['query']
      }
    },
    { name: 'providers_info', description: 'List configured providers and whether they are enabled', inputSchema: { type: 'object', properties: {} } }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;
  if (name === 'providers_info') {
    const info = Object.fromEntries(Object.entries(providers).map(([k, v]) => [k, { enabled: v.enabled }]))
    return { content: [{ type: 'json', json: info }] };
  }
  if (name === 'search') {
    const query = args?.query?.toString?.() || '';
    if (!query) throw new Error('query is required');
    const limit = Number(args?.limit || 10);
    const selected = (Array.isArray(args?.providers) && args.providers.length) ? args.providers : Object.keys(providers);
    const active = selected.filter(p => providers[p]?.enabled);
    if (active.length === 0) {
      return { content: [{ type: 'text', text: 'No providers enabled. Set API keys in environment (e.g., TAVILY_API_KEY, EXA_API_KEY, BRAVE_API_KEY, BING_API_KEY, SERPAPI_KEY).' }] };
    }
    const opts = { limit, timeRange: args?.timeRange, site: args?.site, safe: !!args?.safe };
    const results = (await Promise.allSettled(active.map(p => providers[p].search(query, opts))))
      .flatMap(r => r.status === 'fulfilled' ? r.value : []);
    let aggregated = dedup(results).slice(0, limit * 3);
    if (args?.rerank && process.env.COHERE_API_KEY && aggregated.length > 1) {
      try {
        const { CohereClient } = await import('cohere-ai');
        const co = new CohereClient({ token: process.env.COHERE_API_KEY });
        const rer = await co.rerank({ model: 'rerank-english-v3.0', query, documents: aggregated.map(r => r.title + '\n' + r.snippet) });
        aggregated = rer.results.map((r, i) => ({ ...aggregated[r.index], _rerankScore: r.relevance_score ?? (aggregated.length - i) }));
      } catch (e) { /* ignore rerank failure */ }
    }
    return { content: [{ type: 'json', json: aggregated.slice(0, limit) }] };
  }
  throw new Error(`Unknown tool: ${name}`);
});

async function main() { const transport = new StdioServerTransport(); await server.connect(transport); }
main().catch(err => { console.error(err); process.exit(1); });
