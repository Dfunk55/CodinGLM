#!/usr/bin/env node
/**
 * Testing Toolbox MCP Server
 * Provides unified testing tools: test runners, coverage, fuzzing, mutation testing
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { promisify } from 'util';
import { exec } from 'child_process';

const execAsync = promisify(exec);

const server = new Server(
  {
    name: 'testing-toolbox',
    version: '1.0.0'
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

const TOOLBOX_PATH = '/Users/dustinpainter/Dev-Projects/toolbox/rust-workspace';

async function executeToolboxCommand(command, args = []) {
  try {
    // Use the toolbox binary from PATH or full path, but execute in current working directory
    const toolboxBinary = `${TOOLBOX_PATH}/target/debug/toolbox`;
    const fullCommand = `${toolboxBinary} ${command} ${args.join(' ')}`;
    
    const { stdout, stderr } = await execAsync(fullCommand);
    
    return {
      success: true,
      stdout: stdout.trim(),
      stderr: stderr.trim(),
      command: fullCommand,
      cwd: process.cwd()
    };
  } catch (error) {
    return {
      success: false,
      stdout: error.stdout || '',
      stderr: error.stderr || error.message,
      command: `toolbox ${command} ${args.join(' ')}`,
      cwd: process.cwd(),
      error: error.message
    };
  }
}

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'testing_run_all',
        description: 'Run all tests across all supported languages and frameworks in the project.',
        inputSchema: {
          type: 'object',
          properties: {
            parallel: {
              type: 'boolean',
              description: 'Run tests in parallel',
              default: true
            },
            coverage: {
              type: 'boolean',
              description: 'Generate coverage reports',
              default: true
            }
          }
        }
      },
      {
        name: 'testing_coverage_report',
        description: 'Generate unified coverage report combining all language coverage data.',
        inputSchema: {
          type: 'object',
          properties: {
            format: {
              type: 'string',
              enum: ['html', 'json', 'lcov', 'cobertura'],
              description: 'Coverage report format',
              default: 'html'
            },
            threshold: {
              type: 'number',
              description: 'Minimum coverage threshold',
              default: 80
            }
          }
        }
      },
      {
        name: 'testing_fuzz',
        description: 'Run fuzzing tests to find edge cases and security issues.',
        inputSchema: {
          type: 'object',
          properties: {
            language: {
              type: 'string',
              enum: ['auto', 'rust', 'go', 'python'],
              description: 'Language-specific fuzzing',
              default: 'auto'
            },
            duration: {
              type: 'string',
              description: 'Fuzzing duration (e.g., 30s, 5m, 1h)',
              default: '5m'
            }
          }
        }
      },
      {
        name: 'testing_mutation',
        description: 'Run mutation testing to evaluate test quality by introducing code mutations.',
        inputSchema: {
          type: 'object',
          properties: {
            language: {
              type: 'string',
              enum: ['auto', 'python', 'typescript', 'rust'],
              description: 'Language for mutation testing',
              default: 'auto'
            },
            threshold: {
              type: 'number',
              description: 'Minimum mutation score',
              default: 70
            }
          }
        }
      },
      {
        name: 'testing_performance',
        description: 'Run performance and benchmark tests to measure code efficiency.',
        inputSchema: {
          type: 'object',
          properties: {
            language: {
              type: 'string',
              enum: ['auto', 'rust', 'go', 'python', 'typescript'],
              description: 'Language for performance testing',
              default: 'auto'
            },
            compare_baseline: {
              type: 'boolean',
              description: 'Compare against performance baseline',
              default: false
            }
          }
        }
      },
      {
        name: 'testing_integration',
        description: 'Run integration tests including API tests, database tests, and service interactions.',
        inputSchema: {
          type: 'object',
          properties: {
            environment: {
              type: 'string',
              enum: ['local', 'docker', 'kubernetes'],
              description: 'Test environment',
              default: 'local'
            },
            services: {
              type: 'array',
              items: { type: 'string' },
              description: 'Services to test against',
              default: []
            }
          }
        }
      },
      {
        name: 'testing_e2e',
        description: 'Run end-to-end tests simulating real user scenarios.',
        inputSchema: {
          type: 'object',
          properties: {
            browser: {
              type: 'string',
              enum: ['chrome', 'firefox', 'safari', 'edge'],
              description: 'Browser for web tests',
              default: 'chrome'
            },
            headless: {
              type: 'boolean',
              description: 'Run browser in headless mode',
              default: true
            }
          }
        }
      },
      {
        name: 'testing_load',
        description: 'Run load testing to evaluate system performance under stress.',
        inputSchema: {
          type: 'object',
          properties: {
            target_url: {
              type: 'string',
              description: 'Target URL for load testing'
            },
            concurrent_users: {
              type: 'number',
              description: 'Number of concurrent users',
              default: 10
            },
            duration: {
              type: 'string',
              description: 'Test duration',
              default: '5m'
            }
          },
          required: ['target_url']
        }
      },
      {
        name: 'testing_security',
        description: 'Run security-focused tests including penetration testing and vulnerability scanning.',
        inputSchema: {
          type: 'object',
          properties: {
            target: {
              type: 'string',
              description: 'Target for security testing (URL or local path)',
              default: 'local'
            },
            scan_type: {
              type: 'string',
              enum: ['web', 'api', 'infrastructure'],
              description: 'Type of security scan',
              default: 'web'
            }
          }
        }
      },
      {
        name: 'testing_report_generate',
        description: 'Generate comprehensive testing report with all test results and metrics.',
        inputSchema: {
          type: 'object',
          properties: {
            format: {
              type: 'string',
              enum: ['html', 'pdf', 'json', 'junit'],
              description: 'Report format',
              default: 'html'
            },
            include_trends: {
              type: 'boolean',
              description: 'Include historical trend data',
              default: true
            }
          }
        }
      }
    ]
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result;
    
    switch (name) {
      case 'testing_run_all':
        const runArgs = ['run-all'];
        if (args.parallel) runArgs.push('--parallel');
        if (args.coverage) runArgs.push('--coverage');
        result = await executeToolboxCommand('testing', runArgs);
        break;
        
      case 'testing_coverage_report':
        const coverageArgs = ['coverage-report'];
        if (args.format) coverageArgs.push('--format', args.format);
        if (args.threshold) coverageArgs.push('--threshold', args.threshold.toString());
        result = await executeToolboxCommand('testing', coverageArgs);
        break;
        
      case 'testing_fuzz':
        const fuzzArgs = ['fuzz'];
        if (args.language) fuzzArgs.push('--language', args.language);
        if (args.duration) fuzzArgs.push('--duration', args.duration);
        result = await executeToolboxCommand('testing', fuzzArgs);
        break;
        
      case 'testing_mutation':
        const mutationArgs = ['mutation'];
        if (args.language) mutationArgs.push('--language', args.language);
        if (args.threshold) mutationArgs.push('--threshold', args.threshold.toString());
        result = await executeToolboxCommand('testing', mutationArgs);
        break;
        
      case 'testing_performance':
        const perfArgs = ['performance'];
        if (args.language) perfArgs.push('--language', args.language);
        if (args.compare_baseline) perfArgs.push('--compare-baseline');
        result = await executeToolboxCommand('testing', perfArgs);
        break;
        
      case 'testing_integration':
        const integrationArgs = ['integration'];
        if (args.environment) integrationArgs.push('--environment', args.environment);
        if (args.services && args.services.length > 0) {
          integrationArgs.push('--services', args.services.join(','));
        }
        result = await executeToolboxCommand('testing', integrationArgs);
        break;
        
      case 'testing_e2e':
        const e2eArgs = ['e2e'];
        if (args.browser) e2eArgs.push('--browser', args.browser);
        if (args.headless) e2eArgs.push('--headless');
        result = await executeToolboxCommand('testing', e2eArgs);
        break;
        
      case 'testing_load':
        const loadArgs = ['load', '--target-url', args.target_url];
        if (args.concurrent_users) loadArgs.push('--concurrent-users', args.concurrent_users.toString());
        if (args.duration) loadArgs.push('--duration', args.duration);
        result = await executeToolboxCommand('testing', loadArgs);
        break;
        
      case 'testing_security':
        const securityArgs = ['security'];
        if (args.target) securityArgs.push('--target', args.target);
        if (args.scan_type) securityArgs.push('--scan-type', args.scan_type);
        result = await executeToolboxCommand('testing', securityArgs);
        break;
        
      case 'testing_report_generate':
        const reportArgs = ['report-generate'];
        if (args.format) reportArgs.push('--format', args.format);
        if (args.include_trends) reportArgs.push('--include-trends');
        result = await executeToolboxCommand('testing', reportArgs);
        break;
        
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
    
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing ${name}: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(error => {
  console.error('Server error:', error);
  process.exit(1);
});