# JS Endpoint Intelligence Scanner - Starter Repository

**Version:** 1.0.0-MVP  
**Status:** Development  
**License:** Proprietary (Enterprise)

---

## ⚠️ MANDATORY LEGAL NOTICE

**YOU MUST OBTAIN EXPLICIT WRITTEN AUTHORIZATION BEFORE SCANNING ANY APPLICATION.**

This tool performs deep analysis of JavaScript code and network traffic. Unauthorized use may violate:
- Computer Fraud and Abuse Act (CFAA) - USA
- Computer Misuse Act - UK
- GDPR Article 32 - EU
- Similar laws in other jurisdictions

**ALWAYS:**
- ✅ Get written consent from application owners
- ✅ Use `--i-have-permission` flag (explicit opt-in)
- ✅ Respect `robots.txt` disallow rules
- ✅ Never store sensitive tokens or PII

**NEVER:**
- ❌ Scan applications you don't own without authorization
- ❌ Use for malicious purposes
- ❌ Store credentials or auth tokens
- ❌ Perform active exploitation

---

## Quickstart (5 Minutes)

### Prerequisites

- **Node.js** 18+ (for AST parsing)
- **Python** 3.10+ (for runtime crawling)
- **Docker** 20+ (for containerized deployment)
- **PostgreSQL** 14+ (for metadata storage)
- **Neo4j** 4.4+ or Neo4j Aura account (for graph relationships)

### Installation

```powershell
# Clone repository
git clone https://github.com/yourorg/js-endpoint-scanner.git
cd js-endpoint-scanner

# Install Node.js dependencies
npm install

# Install Python dependencies
cd runtime
python -m pip install -r requirements.txt
cd ..

# Set up environment
cp .env.example .env
# Edit .env with your database credentials and API keys
```

### Minimal Scan (Static Only)

```powershell
# Scan a public SPA (static analysis only)
node cli.js scan `
  --url https://example-spa.com `
  --mode static `
  --output results.json `
  --i-have-permission

# View results
cat results.json | jq '.endpoints[] | {url: .url_template, method: .method}'
```

**Expected Output:**
```json
{
  "url": "/api/users/{id}",
  "method": "GET"
}
{
  "url": "/api/orders",
  "method": "POST"
}
```

### Full Scan (Static + Runtime)

```powershell
# Scan with headless browser
node cli.js scan `
  --url https://example-spa.com `
  --mode runtime `
  --output results.json `
  --i-have-permission `
  --headless true

# Includes network traffic interception
```

### Authenticated Scan (Enterprise Only)

```powershell
# Scan with authentication (requires explicit consent flag)
node cli.js scan `
  --url https://app.example.com `
  --mode authenticated `
  --auth-cookie "session=abc123; Path=/; Secure" `
  --output results.json `
  --consent-ticket "SEC-1234" `
  --i-have-permission

# Credential value is hashed in output, never stored plaintext
```

---

## Repository Structure

```
js-endpoint-scanner/
├── README.md                    # This file
├── ARCHITECTURE.md              # High-level system design
├── SPEC.md                      # Detailed engineering spec
├── SCHEMA.json                  # JSON Schema for results
├── PROMPTS.md                   # LLM prompt templates
├── TEST_PLAN.md                 # Testing & evaluation strategy
├── package.json                 # Node.js dependencies
├── Dockerfile                   # Container image
├── docker-compose.yml           # Local development stack
├── .env.example                 # Environment variables template
├── .github/
│   └── workflows/
│       └── scan-pr.yml          # GitHub Action for PR scanning
│
├── cli.js                       # Command-line interface
├── src/
│   ├── index.js                 # Main orchestrator
│   ├── config.js                # Configuration loader
│   ├── core/
│   │   ├── extract.js           # AST-based endpoint extraction ⭐
│   │   ├── parser.js            # SWC wrapper
│   │   └── bundle-fetcher.js    # HTTP client with caching
│   ├── runtime/
│   │   ├── crawl.py             # Playwright crawler ⭐
│   │   └── network-hook.py      # CDP network interception
│   ├── analysis/
│   │   ├── taint.js             # Taint/dataflow analyzer ⭐
│   │   ├── auth-inference.js    # Hybrid auth detection
│   │   ├── chain-builder.js     # Exploit chain generator
│   │   └── predictive.js        # ML-based endpoint guesser
│   ├── ai/
│   │   ├── llm-client.js        # OpenAI API wrapper
│   │   ├── prompts.js           # Prompt templates
│   │   └── function-calls.js    # Function calling schemas
│   ├── storage/
│   │   ├── postgres.js          # Metadata DB client
│   │   ├── neo4j.js             # Graph DB client
│   │   └── cache.js             # Redis client
│   ├── api/
│   │   ├── server.js            # Express API server
│   │   ├── routes/              # REST endpoints
│   │   └── graphql/             # GraphQL schema
│   └── ui/
│       ├── App.jsx              # React root component
│       ├── components/
│       │   ├── EndpointList.jsx # Endpoint table ⭐
│       │   ├── ChainGraph.jsx   # Visualization
│       │   └── AlertTimeline.jsx
│       └── index.html
│
├── tests/
│   ├── unit/                    # Jest unit tests
│   ├── integration/             # Playwright integration tests
│   └── fixtures/                # Sample bundles
│
├── scripts/
│   ├── setup-db.sql             # PostgreSQL schema
│   ├── seed-graph.cypher        # Neo4j sample data
│   └── migrate.js               # Database migrations
│
└── docs/
    ├── API.md                   # API documentation
    ├── DEPLOYMENT.md            # Production deployment guide
    └── CONTRIBUTING.md          # Development guidelines
```

**⭐ = Core files with code examples provided in this delivery**

---

## Project Configuration Files

### `package.json`

```json
{
  "name": "js-endpoint-scanner",
  "version": "1.0.0",
  "description": "Enterprise JavaScript endpoint discovery and security analysis",
  "main": "src/index.js",
  "bin": {
    "jscan": "./cli.js"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "scripts": {
    "start": "node src/api/server.js",
    "dev": "nodemon src/api/server.js",
    "scan": "node cli.js scan",
    "test": "jest --coverage",
    "test:integration": "playwright test",
    "lint": "eslint src/ --ext .js,.jsx",
    "format": "prettier --write \"src/**/*.{js,jsx,json}\"",
    "db:migrate": "node scripts/migrate.js",
    "docker:build": "docker build -t js-endpoint-scanner:latest .",
    "docker:dev": "docker-compose up -d"
  },
  "dependencies": {
    "@swc/core": "^1.3.100",
    "@swc/wasm": "^1.3.100",
    "axios": "^1.6.2",
    "dotenv": "^16.3.1",
    "express": "^4.18.2",
    "apollo-server-express": "^3.12.1",
    "graphql": "^16.8.1",
    "neo4j-driver": "^5.14.0",
    "pg": "^8.11.3",
    "redis": "^4.6.11",
    "openai": "^4.20.1",
    "commander": "^11.1.0",
    "chalk": "^5.3.0",
    "ora": "^7.0.1",
    "js-yaml": "^4.1.0",
    "jsonschema": "^1.4.1",
    "uuid": "^9.0.1",
    "winston": "^3.11.0",
    "compression": "^1.7.4",
    "helmet": "^7.1.0",
    "cors": "^2.8.5"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.1",
    "@types/node": "^20.10.4",
    "eslint": "^8.55.0",
    "eslint-config-airbnb-base": "^15.0.0",
    "jest": "^29.7.0",
    "nodemon": "^3.0.2",
    "prettier": "^3.1.0",
    "supertest": "^6.3.3"
  },
  "keywords": [
    "security",
    "api-discovery",
    "ast",
    "endpoint-scanner",
    "vulnerability-assessment",
    "spa-security"
  ],
  "author": "Your Security Team",
  "license": "UNLICENSED",
  "private": true
}
```

### `runtime/requirements.txt` (Python)

```txt
playwright==1.40.0
requests==2.31.0
beautifulsoup4==4.12.2
pydantic==2.5.2
python-dotenv==1.0.0
asyncio==3.4.3
aiohttp==3.9.1
redis==5.0.1
psycopg2-binary==2.9.9
structlog==23.2.0
```

### `.env.example`

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=scanner_metadata
POSTGRES_USER=scanner
POSTGRES_PASSWORD=changeme

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=changeme

REDIS_URL=redis://localhost:6379

# AI Configuration (OpenAI)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.1

# LLM Cost Controls
LLM_DAILY_BUDGET_USD=50
LLM_CACHE_TTL_SECONDS=604800  # 7 days

# Scanner Configuration
MAX_BUNDLE_SIZE_MB=50
MAX_CONCURRENT_CRAWLERS=3
CRAWLER_TIMEOUT_SECONDS=300
RESPECT_ROBOTS_TXT=true

# API Server
API_PORT=3000
API_HOST=0.0.0.0
API_RATE_LIMIT_WINDOW_MS=60000
API_RATE_LIMIT_MAX_REQUESTS=100

# Security
SESSION_SECRET=random-secret-change-me
ENABLE_AUTH=true
ALLOWED_ORIGINS=http://localhost:3000,https://app.example.com

# Monitoring
PROMETHEUS_PORT=9090
LOG_LEVEL=info
ENABLE_TRACING=false

# Storage
S3_BUCKET=scanner-bundles
S3_REGION=us-east-1
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key

# Feature Flags
ENABLE_PREDICTIVE_GENERATION=true
ENABLE_LLM_AUTH_INFERENCE=true
ENABLE_CHAIN_REASONING=true
```

### `Dockerfile`

```dockerfile
# Multi-stage build for minimal production image
FROM node:18-alpine AS node-builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY src/ ./src/
COPY cli.js ./

# Python runtime layer
FROM mcr.microsoft.com/playwright/python:v1.40.0-focal

# Install Node.js in Python image (unified runtime)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Node.js dependencies
COPY --from=node-builder /app/node_modules ./node_modules
COPY --from=node-builder /app/src ./src
COPY --from=node-builder /app/cli.js ./

# Install Python dependencies
COPY runtime/requirements.txt ./runtime/
RUN pip install --no-cache-dir -r runtime/requirements.txt

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Create non-root user
RUN groupadd -r scanner && useradd -r -g scanner scanner
RUN chown -R scanner:scanner /app
USER scanner

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

EXPOSE 3000

CMD ["node", "src/api/server.js"]
```

### `docker-compose.yml`

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: scanner_metadata
      POSTGRES_USER: scanner
      POSTGRES_PASSWORD: changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/setup-db.sql:/docker-entrypoint-initdb.d/setup.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U scanner"]
      interval: 10s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5.13-community
    environment:
      NEO4J_AUTH: neo4j/changeme
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_memory_heap_max__size: 2G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    healthcheck:
      test: ["CMD-SHELL", "cypher-shell -u neo4j -p changeme 'RETURN 1'"]
      interval: 15s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  scanner-api:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env
    ports:
      - "3000:3000"
    depends_on:
      postgres:
        condition: service_healthy
      neo4j:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./src:/app/src  # Hot reload in dev
      - bundle_cache:/app/cache
    environment:
      NODE_ENV: development

  scanner-worker:
    build:
      context: .
      dockerfile: Dockerfile
    command: node src/workers/job-processor.js
    env_file:
      - .env
    depends_on:
      - postgres
      - neo4j
      - redis
    deploy:
      replicas: 2  # Parallel workers
    environment:
      WORKER_MODE: "true"

volumes:
  postgres_data:
  neo4j_data:
  neo4j_logs:
  redis_data:
  bundle_cache:
```

---

## Development Workflow

### 1. Set Up Local Environment

```powershell
# Start infrastructure
docker-compose up -d postgres neo4j redis

# Wait for health checks
Start-Sleep -Seconds 15

# Run migrations
npm run db:migrate

# Seed graph with examples
docker exec -i js-endpoint-scanner-neo4j-1 cypher-shell -u neo4j -p changeme < scripts/seed-graph.cypher
```

### 2. Run Scanner Locally

```powershell
# Single scan (development)
node cli.js scan --url https://jsonplaceholder.typicode.com --mode static --i-have-permission

# Watch mode (for testing changes)
npm run dev  # Starts API server with nodemon
```

### 3. Run Tests

```powershell
# Unit tests (fast)
npm test

# Integration tests (requires browsers)
npm run test:integration

# Coverage report
npm test -- --coverage --coverageReporters=html
# Open coverage/index.html
```

### 4. Lint & Format

```powershell
# Auto-fix linting issues
npm run lint -- --fix

# Format code
npm run format
```

---

## Production Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed AWS/GCP/Azure guides.

**Quick Kubernetes Deployment:**

```powershell
# Build and push image
docker build -t gcr.io/yourproject/scanner:v1.0.0 .
docker push gcr.io/yourproject/scanner:v1.0.0

# Apply K8s manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -n scanner
```

---

## CI/CD Integration (GitHub Actions)

The repository includes a GitHub Action that scans JavaScript changes in PRs.

**File:** `.github/workflows/scan-pr.yml` (see full content in deliverables)

**Usage:**
1. Action triggers on `pull_request` events
2. Scans only changed `.js` files
3. Posts summary comment to PR
4. Fails if `critical` or `high` risk endpoints found (configurable)

**Example PR Comment:**
```markdown
## 🔍 JS Endpoint Scan Results

**Scan ID:** a1b2c3d4-...
**Changed Files:** 3 JavaScript files

### Summary
- **New Endpoints:** 2
- **High Risk:** 1 ⚠️
- **Medium Risk:** 1

### Top Findings
1. `/api/admin/users/{id}` - No authorization check detected (HIGH)
2. `/api/posts` - Tainted parameter in SQL-like query (MEDIUM)

[View Full Report](https://scanner.example.com/scans/a1b2c3d4)
```

---

## API Usage

### REST Endpoints

```powershell
# Start scan
curl -X POST http://localhost:3000/api/scans \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://example.com",
    "mode": "static",
    "consent_verified": true
  }'

# Get scan status
curl http://localhost:3000/api/scans/{scan_id}

# List endpoints for app
curl http://localhost:3000/api/apps/{app_id}/endpoints?risk_level=high

# Export to SARIF
curl http://localhost:3000/api/scans/{scan_id}/export?format=sarif > results.sarif
```

### GraphQL Queries

```graphql
query GetHighRiskEndpoints($appId: ID!) {
  app(id: $appId) {
    endpoints(filter: { riskLevel: HIGH }) {
      id
      urlTemplate
      method
      riskScores {
        overallRisk
        cvssBaseScore
      }
      chains {
        name
        likelihood
        steps {
          action
        }
      }
    }
  }
}
```

---

## Configuration Options

### Scan Modes

| Mode | Description | Use Case | Performance |
|------|-------------|----------|-------------|
| `static` | AST analysis only | Fast pre-commit checks, CI/CD | <30s for typical bundle |
| `runtime` | Headless browser + network capture | Comprehensive discovery | 2-5 min |
| `authenticated` | Runtime with credentials | Privileged endpoint discovery | 5-10 min |
| `predictive` | Include ML-generated guesses | Attack surface expansion | +1 min |

### CLI Flags

```
--url <string>              Target application URL (required)
--mode <static|runtime|...> Scan mode (default: static)
--output <path>             Output file path (default: results.json)
--format <json|sarif|html>  Output format (default: json)
--i-have-permission         Required flag confirming authorization (required)
--consent-ticket <string>   Tracking ticket/email for audit trail
--auth-cookie <string>      Cookie header for authenticated scans
--headless <bool>           Run browser in headless mode (default: true)
--max-depth <int>           Max crawl depth (default: 3)
--timeout <int>             Timeout in seconds (default: 300)
--enable-ai                 Enable LLM inference (default: true)
--ai-budget <int>           Max LLM calls per scan (default: 100)
--respect-robots            Honor robots.txt (default: true)
--verbose                   Verbose logging
```

---

## Troubleshooting

### Issue: "SWC parse error: Unexpected token"

**Cause:** Unsupported JS syntax (e.g., stage-0 proposals)  
**Fix:** Configure SWC parser in `src/config.js`:
```javascript
swcOptions: {
  jsc: {
    parser: {
      syntax: "ecmascript",
      jsx: true,
      decorators: true,  // Enable decorators
      dynamicImport: true
    }
  }
}
```

### Issue: "Playwright timeout after 30s"

**Cause:** Slow page load or heavy JS execution  
**Fix:** Increase timeout:
```powershell
node cli.js scan --url ... --timeout 600  # 10 minutes
```

### Issue: "Neo4j connection refused"

**Cause:** Neo4j not started or wrong credentials  
**Fix:**
```powershell
# Check Neo4j status
docker-compose ps neo4j

# View logs
docker-compose logs neo4j

# Restart
docker-compose restart neo4j
```

### Issue: "OpenAI API rate limit exceeded"

**Cause:** Too many LLM calls  
**Fix:** Enable caching and reduce calls:
```bash
# In .env
LLM_CACHE_TTL_SECONDS=604800  # 7 days
LLM_DAILY_BUDGET_USD=50

# Or disable AI temporarily
node cli.js scan --url ... --enable-ai false
```

---

## Performance Tuning

### For Large Bundles (>10MB)

```javascript
// src/config.js
module.exports = {
  parser: {
    maxWorkers: os.cpus().length - 1,  // Parallel parsing
    memoryLimitMb: 4096,  // Increase if OOM
    streamingMode: true   // Incremental AST building
  }
}
```

### For Slow Runtime Crawls

```python
# runtime/crawl.py
PLAYWRIGHT_CONFIG = {
    'max_concurrent_pages': 5,  # Parallel page crawling
    'browser_pool_size': 3,      # Reuse browser instances
    'navigation_timeout': 30000, # 30s timeout
    'wait_until': 'networkidle'  # Or 'domcontentloaded' for speed
}
```

---

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Rotate API keys monthly** - Set calendar reminder
3. **Use least-privilege DB credentials** - Read-only for query service
4. **Enable audit logging** - Track all scans to immutable log
5. **Encrypt data at rest** - PostgreSQL TDE, S3 SSE
6. **Rate limit API endpoints** - Prevent abuse (100 req/min default)
7. **Validate all user inputs** - Even internal tools
8. **Regular dependency updates** - `npm audit` in CI pipeline

---

## Getting Help

- **Documentation:** [docs/](docs/)
- **GitHub Issues:** https://github.com/yourorg/js-endpoint-scanner/issues
- **Slack Channel:** #security-scanner (internal)
- **Email Support:** security-tools@yourorg.com

---

## Roadmap

### MVP (Current)
- ✅ Static AST extraction
- ✅ Runtime Playwright crawling
- ✅ JSON output schema
- ✅ Basic auth inference (rules only)

### v1.0 (Next 4 weeks)
- ⏳ LLM-powered auth inference
- ⏳ Taint analysis
- ⏳ Exploit chain detection
- ⏳ GitHub Action CI integration

### v1.5 (8 weeks)
- 📅 Predictive endpoint generation
- 📅 Change detection / drift monitoring
- 📅 Web UI (React dashboard)
- 📅 SARIF export

### Enterprise (12+ weeks)
- 📅 Multi-tenant architecture
- 📅 RBAC and SSO
- 📅 SIEM integrations (Splunk, Datadog)
- 📅 Custom rule engine
- 📅 SLA guarantees (99.9% uptime)

---

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

**Quick Start:**
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`npm test`)
4. Commit with conventional commits (`feat: add new parser`)
5. Push and open PR

---

## License

**Proprietary - All Rights Reserved**

This software is confidential and proprietary. Unauthorized use, reproduction, or distribution is prohibited.

For licensing inquiries: legal@yourorg.com

---

## Acknowledgments

Built with:
- [SWC](https://swc.rs) - Rust-based JS/TS compiler
- [Playwright](https://playwright.dev) - Browser automation
- [Neo4j](https://neo4j.com) - Graph database
- [OpenAI](https://openai.com) - GPT-4 API

Inspired by research from:
- OWASP ZAP dynamic scanner
- Burp Suite active/passive scanning
- Semgrep static analysis patterns

---

**Last Updated:** 2025-12-06  
**Maintainers:** Security Engineering Team
