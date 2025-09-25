# 🛠️ Setup Guide - AI-Powered Enterprise Automation Suite

> **Complete step-by-step setup instructions** for the revolutionary AI-collaborative automation system.

## 🎯 Quick Start (5 minutes)

```bash
# 1. Clone and setup environment
git clone https://github.com/arturdr-org/org-automation.git
cd org-automation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Test the system
python scripts/demo-ai-system.py

# 3. Configure API keys (see section below)
export CLAUDE_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."

# 4. Run first AI operation
python scripts/ai-manual-parser.py --command "Health Check" --dry-run
```

## 📋 Prerequisites

### 🔧 Required Tools
- **Git**: Version control system
- **Python 3.9+**: Main runtime environment
- **GitHub CLI** (optional): For advanced configuration
- **Docker** (optional): For containerized deployment

### 🔑 Required Permissions
- `admin:org` - Organization management
- `repo` - Full repository access
- `workflow` - GitHub Actions management
- `read:project` - Project access
- `write:project` - Project management

## 🏗️ Architecture Overview

Before setup, understand the enterprise-grade structure:

```
Enterprise Components:
├── 🧠 Core System        # Central automation engine
├── 🔧 Domain Modules     # CICD, Security, Quality, Notifications
├── 🤖 AI Integration     # Multi-AI coordination hub
├── 📚 Documentation      # Technical architecture docs
├── 🧪 Test Suites        # Comprehensive testing
└── ⚙️ GitHub Automation  # Workflows & templates
```

## 🚀 Installation Steps

### 1️⃣ Environment Setup

```bash
# Clone the enterprise repository
git clone https://github.com/arturdr-org/org-automation.git
cd org-automation

# Verify enterprise structure
ls -la  # Should see only 9 essential files in root

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import aiohttp, yaml; print('✅ Dependencies installed')"
```

### 2️⃣ AI Providers Configuration

#### 🧠 Claude (Anthropic)
```bash
# Get API key from: https://console.anthropic.com/
export CLAUDE_API_KEY="sk-ant-api03-..."

# Test connection
python scripts/ai-integration-hub.py list providers
```

#### 🤖 OpenAI GPT
```bash
# Get API key from: https://platform.openai.com/api-keys
export OPENAI_API_KEY="sk-..."

# Verify integration
python -c "import os; print('✅ OpenAI configured' if os.getenv('OPENAI_API_KEY') else '❌ Missing key')"
```

#### 🔍 Google Gemini
```bash
# Get API key from: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="..."

# Test all providers
python scripts/ai-integration-hub.py list providers
```

### 3️⃣ GitHub Integration

#### Option A: GitHub App (Recommended)

1. **Create GitHub App**:
   ```
   Settings → Developer settings → GitHub Apps → New GitHub App
   ```

2. **Configure App**:
   ```
   Name: ai-automation-arturdr-org
   Homepage: https://github.com/arturdr-org/org-automation
   Webhook: Disabled
   ```

3. **Set Permissions**:
   ```yaml
   Repository permissions:
     Contents: Read & Write
     Issues: Read & Write  
     Metadata: Read
     Pull requests: Read & Write
     Actions: Write
     
   Organization permissions:
     Members: Read
     Administration: Write
   ```

4. **Configure Secrets**:
   ```bash
   # In GitHub repository settings
   gh secret set ORG_APP_ID --body "123456"
   gh secret set ORG_APP_PRIVATE_KEY --body "$(cat private-key.pem)"
   ```

#### Option B: Personal Access Token

```bash
# Create token with required scopes
gh auth login --scopes "admin:org,repo,workflow"

# Set secret
gh secret set GITHUB_TOKEN --body "ghp_..."
```

### 4️⃣ Notification Systems

#### 📧 Slack Integration
```bash
# Create webhook: https://api.slack.com/messaging/webhooks
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# Set GitHub secret
gh secret set SLACK_WEBHOOK_URL --body "$SLACK_WEBHOOK_URL"
```

#### 🚨 PagerDuty Integration
```bash
# Get integration key from PagerDuty service
export PAGERDUTY_INTEGRATION_KEY="..."

# Configure for critical alerts
gh secret set PAGERDUTY_INTEGRATION_KEY --body "$PAGERDUTY_INTEGRATION_KEY"
```

### 5️⃣ Enterprise Configuration

#### 🏗️ Module Configuration

Each domain module has specific configuration:

```bash
# CICD Module
ls modules/cicd/
# Configure: workflows/, pipelines/, deployment/, testing/

# Security Module  
ls modules/security/
# Configure: scanning/, policies/, compliance/, monitoring/

# Quality Module
ls modules/quality/
# Configure: code_analysis/, metrics/, reporting/, standards/

# Notifications Module
ls modules/notifications/
# Configure: slack/, email/, pagerduty/, webhooks/
```

#### ⚙️ Shared Resources

```bash
# Global configurations
ls shared/config/
# Edit: ai-hub-config.example.json, branch_protection.yml, labels.yml

# Common utilities
ls shared/utils/
# Extend: Common functions and helpers

# Reusable templates
ls shared/templates/
# Customize: Issue templates, PR templates, etc.
```

## 🧪 Testing & Validation

### System Health Check
```bash
# Complete system demonstration
python scripts/demo-ai-system.py

# Individual component tests
python scripts/ai-manual-parser.py --list
python scripts/ai-integration-hub.py status

# Test suites
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/e2e/ -v
```

### AI Integration Tests
```bash
# Test multi-AI collaboration
python scripts/ai-integration-hub.py request warp_agent \
  "Health Check" --parameters '{"dry_run": true}' --priority 1

# Validate AI manual operations  
python scripts/ai-manual-parser.py --command "Verificar Status do Sistema" --dry-run

# Test knowledge base
ls docs/ # Verify comprehensive documentation
```

## ⚙️ GitHub Actions Configuration

### 🤖 AI-Powered Operations

The main workflow `.github/workflows/ai-powered-operations.yml` provides:

- **Scheduled Execution**: 2x daily (6:00 & 18:00 UTC)
- **Manual Execution**: Via GitHub Actions UI
- **21 Automated Jobs**: Validation, execution, monitoring, alerts
- **Multi-AI Coordination**: Collaborative decision making
- **Security Validation**: Pre-execution safety checks

#### Manual Execution
```
1. Go to Actions → AI-Powered Operations
2. Click "Run workflow"
3. Configure:
   - Operation Type: health_check, daily_routine, etc.
   - Dry Run: true (for safe testing)
   - AI Requester: system identifier
```

### 🔍 Additional Workflows

- **CI/CD Pipeline**: `.github/workflows/ci-build-test.yml`
- **Security Audit**: `.github/workflows/security-audit.yml` 
- **External Integrations**: `.github/workflows/external-integrations.yml`

## 🎯 Advanced Configuration

### 🔧 Custom AI Operations

Add custom operations to `docs/ai-operations-manual.md`:

```yaml
- name: "Custom Operation"
  category: "sistema"
  priority: "alta"
  prerequisites:
    - "Sistema operacional"
    - "Permissões adequadas"
  commands:
    - "your-custom-command"
  validation:
    - "check-system-status"
  output: "Status da operação customizada"
```

### 📊 Monitoring & Metrics

Configure custom KPIs in the AI manual:

```yaml
kpis:
  - name: "Custom Metric"
    description: "Your custom monitoring metric"
    target: "< 100ms response time"
    alert_threshold: "> 500ms"
```

### 🤖 AI Provider Extensions

Add new AI providers in `scripts/ai-integration-hub.py`:

```python
class CustomAIProvider(AIProvider):
    def __init__(self, config):
        super().__init__(config)
        # Your custom provider implementation
```

## 🔒 Security Considerations

### 🛡️ Environment Security
- Store all API keys in GitHub Secrets
- Use environment-specific configurations
- Enable 2FA for all accounts
- Regular security audits via automated workflows

### 🔐 AI Security
- Always test in dry-run mode first
- Validate AI responses before execution
- Implement rate limiting for AI calls
- Monitor AI decision logs for audit trails

### 🎯 Access Control
- Use GitHub Apps with minimal required permissions
- Implement role-based access in the organization
- Regular permission audits
- Emergency stop mechanisms for AI operations

## 📚 Documentation Structure

Navigate the comprehensive documentation:

```
docs/
├── architecture.md          # System architecture overview
├── mcp.md                   # Model Context Protocol integration  
├── onboarding.md            # Quick start guide (5 minutes)
├── ai-operations-manual.md  # Complete operations manual
├── architecture/            # Detailed architecture docs
│   ├── REPOSITORY_STRUCTURE.md
│   └── MODERNIZATION_PLAN.md
└── guides/                  # User & developer guides
    └── GITHUB_APP_SETUP.md
```

## 🚨 Troubleshooting

### Common Issues

#### ❌ API Key Issues
```bash
# Check if keys are set
echo $CLAUDE_API_KEY $OPENAI_API_KEY $GEMINI_API_KEY

# Test API connections
python scripts/ai-integration-hub.py list providers
```

#### ❌ Permission Errors
```bash
# Verify GitHub token permissions
gh auth status

# Check organization access
gh api orgs/arturdr-org/repos
```

#### ❌ AI Integration Problems
```bash
# Debug AI operations
python scripts/ai-manual-parser.py --command "Health Check" --dry-run -v

# Check logs
tail -f logs/ai_manual_parser.log
tail -f logs/ai_integration_hub.log
```

### 🆘 Getting Help

- 📖 **Documentation**: Complete docs in `docs/`
- 🐛 **Issues**: Open GitHub issue for bugs
- 💬 **Discussions**: Use GitHub Discussions for questions
- 📧 **Support**: Available in organization settings

## 🎉 Next Steps

After setup is complete:

1. ✅ **Test the system**: `python scripts/demo-ai-system.py`
2. ✅ **Configure AI providers**: Add your API keys
3. ✅ **Run first operation**: Health check in dry-run mode
4. ✅ **Enable automation**: Set up GitHub Actions
5. ✅ **Monitor operations**: Check dashboards and logs
6. ✅ **Customize**: Adapt to your specific needs

## 🏆 Success Criteria

Your setup is complete when:

- ✅ All AI providers show "ready" status
- ✅ Demo system runs successfully  
- ✅ GitHub Actions execute without errors
- ✅ Health checks pass in dry-run mode
- ✅ Notifications are delivered correctly
- ✅ Documentation is accessible and clear

---

**🚀 Welcome to the future of AI-powered automation!**

*You now have access to the most advanced collaborative AI automation system available.*