#!/usr/bin/env node

/**
 * JS Endpoint Scanner - CLI Interface
 * 
 * Command-line tool for scanning JavaScript applications
 * 
 * Usage:
 *   jscan scan --url https://example.com --mode static --output results.json --i-have-permission
 */

const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const fs = require('fs');
const path = require('path');

const { Orchestrator } = require('./src/index');
const { version } = require('./package.json');

// Create CLI program
const program = new Command();

program
  .name('jscan')
  .description('JS Endpoint Intelligence Scanner')
  .version(version);

// Scan command
program
  .command('scan')
  .description('Scan a JavaScript application for API endpoints')
  .requiredOption('--url <url>', 'Target application URL')
  .option('--mode <mode>', 'Scan mode: static, runtime, authenticated', 'static')
  .option('--output <path>', 'Output file path', 'results.json')
  .option('--format <format>', 'Output format: json, sarif', 'json')
  .requiredOption('--i-have-permission', 'Confirm you have authorization to scan this target')
  .option('--consent-ticket <ticket>', 'Consent tracking ticket/email')
  .option('--auth-cookie <cookie>', 'Authentication cookie for authenticated scans')
  .option('--auth-header <header>', 'Authorization header (e.g., "Bearer token123")')
  .option('--max-depth <number>', 'Max crawl depth', parseInt, 3)
  .option('--max-pages <number>', 'Max pages to crawl', parseInt, 10)
  .option('--timeout <seconds>', 'Timeout in seconds', parseInt, 300)
  .option('--headless', 'Run browser in headless mode', true)
  .option('--enable-ai', 'Enable LLM inference', true)
  .option('--ai-budget <number>', 'Max LLM calls per scan', parseInt, 100)
  .option('--respect-robots', 'Honor robots.txt', true)
  .option('--verbose', 'Verbose logging', false)
  .option('--files <files>', 'Comma-separated list of files to scan (for static mode)')
  .action(async (options) => {
    // Validate required consent
    if (!options.iHavePermission) {
      console.error(chalk.red('❌ Error: --i-have-permission flag is required'));
      console.error(chalk.yellow('   You must confirm you have authorization to scan this target.'));
      process.exit(1);
    }
    
    // Display warning banner
    console.log(chalk.yellow.bold('\n⚠️  LEGAL NOTICE ⚠️'));
    console.log(chalk.yellow('You must have explicit written authorization to scan this application.'));
    console.log(chalk.yellow('Unauthorized scanning may violate laws (CFAA, GDPR, etc.).\n'));
    
    // Create spinner for progress
    const spinner = ora('Initializing scanner...').start();
    
    try {
      // Parse auth options
      let authConfig = null;
      if (options.authCookie || options.authHeader) {
        authConfig = {
          cookies: options.authCookie ? parseCookies(options.authCookie) : null,
          header: options.authHeader || null
        };
      }
      
      // Parse file list
      let filesToScan = null;
      if (options.files) {
        filesToScan = options.files.split(',').map(f => f.trim());
      }
      
      // Configure scan
      const scanConfig = {
        targetUrl: options.url,
        mode: options.mode,
        authentication: authConfig,
        consentTicket: options.consentTicket,
        crawler: {
          maxDepth: options.maxDepth,
          maxPages: options.maxPages,
          timeoutMs: options.timeout * 1000,
          headless: options.headless
        },
        ai: {
          enabled: options.enableAi,
          maxCalls: options.aiBudget
        },
        files: filesToScan,
        respectRobotsTxt: options.respectRobots,
        verbose: options.verbose
      };
      
      // Initialize orchestrator
      const orchestrator = new Orchestrator(scanConfig);
      
      // Set up progress events
      orchestrator.on('progress', (event) => {
        spinner.text = event.message;
        if (options.verbose) {
          spinner.stopAndPersist({ symbol: '📌', text: event.message });
          spinner.start();
        }
      });
      
      orchestrator.on('warning', (warning) => {
        spinner.warn(chalk.yellow(warning.message));
        spinner.start();
      });
      
      orchestrator.on('error', (error) => {
        spinner.fail(chalk.red(error.message));
      });
      
      // Run scan
      spinner.text = 'Starting scan...';
      const results = await orchestrator.scan();
      
      // Format output
      let outputContent;
      if (options.format === 'sarif') {
        outputContent = convertToSARIF(results);
      } else {
        outputContent = JSON.stringify(results, null, 2);
      }
      
      // Write to file
      const outputPath = path.resolve(options.output);
      fs.writeFileSync(outputPath, outputContent);
      
      spinner.succeed(chalk.green(`✓ Scan completed successfully`));
      
      // Display summary
      console.log(chalk.bold('\n📊 Scan Summary:'));
      console.log(`  Scan ID: ${chalk.cyan(results.metadata.scan_id)}`);
      console.log(`  Duration: ${chalk.cyan(results.metadata.scan_duration_seconds + 's')}`);
      console.log(`  Endpoints Discovered: ${chalk.cyan(results.endpoints.length)}`);
      
      const riskCounts = countByRisk(results.endpoints);
      console.log(`  Risk Breakdown:`);
      console.log(`    ${chalk.red('Critical')}: ${riskCounts.critical || 0}`);
      console.log(`    ${chalk.red('High')}: ${riskCounts.high || 0}`);
      console.log(`    ${chalk.yellow('Medium')}: ${riskCounts.medium || 0}`);
      console.log(`    ${chalk.blue('Low')}: ${riskCounts.low || 0}`);
      console.log(`    ${chalk.gray('Info')}: ${riskCounts.info || 0}`);
      
      if (results.findings?.exploit_chains?.length > 0) {
        console.log(`  Exploit Chains: ${chalk.yellow(results.findings.exploit_chains.length)}`);
      }
      
      console.log(`\n  Full results saved to: ${chalk.green(outputPath)}`);
      
      // Exit with appropriate code
      if (riskCounts.critical > 0) {
        console.log(chalk.red('\n⚠️  Critical risks found - review immediately!'));
        process.exit(2);  // Critical findings
      } else if (riskCounts.high > 0) {
        console.log(chalk.yellow('\n⚠️  High-severity risks found - review recommended.'));
        process.exit(1);  // High findings (non-blocking by default)
      } else {
        console.log(chalk.green('\n✓ No critical or high-severity risks detected.'));
        process.exit(0);  // Success
      }
      
    } catch (error) {
      spinner.fail(chalk.red('✗ Scan failed'));
      console.error(chalk.red(`\nError: ${error.message}`));
      if (options.verbose) {
        console.error(error.stack);
      }
      process.exit(1);
    }
  });

// Helper: Parse cookie string
function parseCookies(cookieString) {
  // Format: "name1=value1; name2=value2"
  const cookies = [];
  cookieString.split(';').forEach(pair => {
    const [name, value] = pair.trim().split('=');
    if (name && value) {
      cookies.push({ name, value, domain: '', path: '/' });
    }
  });
  return cookies;
}

// Helper: Count endpoints by risk level
function countByRisk(endpoints) {
  const counts = {};
  endpoints.forEach(ep => {
    const risk = ep.risk_scores?.overall_risk || 'info';
    counts[risk] = (counts[risk] || 0) + 1;
  });
  return counts;
}

// Helper: Convert to SARIF format
function convertToSARIF(results) {
  // SARIF 2.1.0 format
  return JSON.stringify({
    version: '2.1.0',
    $schema: 'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json',
    runs: [{
      tool: {
        driver: {
          name: 'JS Endpoint Scanner',
          version: results.metadata.engine_version,
          informationUri: 'https://github.com/yourorg/js-endpoint-scanner'
        }
      },
      results: results.endpoints
        .filter(ep => ep.risk_scores?.overall_risk !== 'info')
        .map(ep => ({
          ruleId: `endpoint-risk-${ep.risk_scores.overall_risk}`,
          level: mapRiskToSARIFLevel(ep.risk_scores.overall_risk),
          message: {
            text: `${ep.method} ${ep.url_template} - Risk: ${ep.risk_scores.overall_risk}`
          },
          locations: [{
            physicalLocation: {
              artifactLocation: {
                uri: ep.source_code?.original_file || ep.source_code?.bundle_file
              },
              region: {
                startLine: ep.source_code?.line || 1
              }
            }
          }]
        }))
    }]
  }, null, 2);
}

function mapRiskToSARIFLevel(risk) {
  const mapping = {
    critical: 'error',
    high: 'error',
    medium: 'warning',
    low: 'note',
    info: 'note'
  };
  return mapping[risk] || 'note';
}

// Parse CLI arguments
program.parse();
