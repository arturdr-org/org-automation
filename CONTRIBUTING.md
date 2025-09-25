# 🤝 Contributing to org-automation-suite

Thank you for your interest in contributing to our AI-powered automation system! This guide will help you get started.

## 🌟 How to Contribute

### 🐛 Reporting Bugs
Use our [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.yml) and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Relevant logs

### ✨ Suggesting Features
Use our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.yml) and describe:
- The problem you're solving
- Your proposed solution
- Alternative approaches considered
- Impact on the system

### 🤖 AI Improvements
Use our [AI Enhancement Template](.github/ISSUE_TEMPLATE/ai_improvement.yml) for:
- AI behavior improvements
- New AI provider integrations
- Multi-AI collaboration enhancements
- Learning algorithm improvements

## 🚀 Development Workflow

### 1. Setup Development Environment
```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/org-automation.git
cd org-automation

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### 2. Understanding the Codebase
```
🧠 core/           # Core automation engine
🔧 modules/        # Domain-specific functionality
🤖 scripts/        # AI-powered tools
📚 docs/          # Technical documentation
🧪 tests/         # Test suites
```

Key files to understand:
- `scripts/ai-integration-hub.py` - Multi-AI coordination
- `scripts/ai-manual-parser.py` - Command execution engine
- `docs/ai-operations-manual.md` - Operation definitions
- `.github/workflows/ai-powered-operations.yml` - Automation workflows

### 3. Making Changes

#### Branch Naming Convention
```
feat/description       # New features
fix/description        # Bug fixes
docs/description       # Documentation
test/description       # Test improvements
refactor/description   # Code refactoring
ai/description         # AI-specific improvements
```

#### Code Standards
- **Python**: Follow PEP 8, use Black for formatting
- **Type Hints**: Required for all public functions
- **Docstrings**: Google-style docstrings
- **Testing**: Minimum 80% code coverage
- **AI Code**: Always include dry-run mode

#### Example Code Style
```python
async def execute_ai_operation(
    operation: str,
    parameters: Dict[str, Any],
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Execute an AI-powered operation with validation.
    
    Args:
        operation: The operation to execute
        parameters: Operation parameters
        dry_run: Whether to simulate execution only
        
    Returns:
        Operation result with metadata
        
    Raises:
        ValidationError: If parameters are invalid
        ExecutionError: If operation fails
    """
    # Implementation...
```

### 4. Testing Requirements

#### Test Categories
```bash
# Unit tests - Fast, isolated
python -m pytest tests/unit/ -v

# Integration tests - Components working together
python -m pytest tests/integration/ -v

# End-to-end tests - Full system workflows
python -m pytest tests/e2e/ -v

# AI tests - Specific AI functionality
python -m pytest tests/ai/ -v
```

#### AI Testing Guidelines
1. **Always test in dry-run mode first**
2. **Mock external AI API calls in unit tests**
3. **Test AI decision-making logic**
4. **Validate multi-AI collaboration scenarios**
5. **Test error handling and fallbacks**

Example AI test:
```python
@pytest.mark.asyncio
async def test_ai_collaboration_consensus():
    """Test that multiple AIs reach consensus on decisions."""
    hub = AIIntegrationHub()
    
    # Mock AI responses
    mock_responses = {
        "claude": {"decision": "approve", "confidence": 0.9},
        "gpt": {"decision": "approve", "confidence": 0.85},
        "gemini": {"decision": "approve", "confidence": 0.8}
    }
    
    consensus = await hub.get_ai_consensus(mock_responses)
    assert consensus["decision"] == "approve"
    assert consensus["confidence"] > 0.8
```

### 5. Documentation Requirements

#### Code Documentation
- All public functions must have docstrings
- Include type hints for parameters and return values
- Document complex algorithms and AI decision logic
- Add examples for AI operations

#### User Documentation
- Update relevant sections in `docs/`
- Add examples to the onboarding guide
- Update architecture documentation for significant changes
- Include troubleshooting information

### 6. Pull Request Process

#### Before Submitting
```bash
# Run the full test suite
python scripts/demo-ai-system.py  # End-to-end validation
pytest tests/ -v --cov=src --cov-report=html

# Check code quality
flake8 src/ tests/
black --check src/ tests/
mypy src/

# Validate AI functionality
python scripts/ai-integration-hub.py list providers
python scripts/ai-manual-parser.py --list
```

#### PR Checklist
- [ ] Tests pass locally and in CI
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] AI functionality tested in dry-run mode
- [ ] No breaking changes (or clearly documented)
- [ ] Commit messages follow conventional format

#### PR Review Process
1. **Automated Checks**: CI/CD pipeline runs automatically
2. **AI Safety Review**: For AI-related changes
3. **Code Review**: Focus on maintainability and performance
4. **Security Review**: For security-sensitive changes
5. **Integration Testing**: Full system testing

## 🏗️ Architecture Guidelines

### Core Principles
1. **Modularity**: Keep components loosely coupled
2. **Testability**: Design for easy testing
3. **AI Safety**: Always validate AI decisions
4. **Observability**: Comprehensive logging and metrics
5. **Scalability**: Design for growth

### AI Development Guidelines
1. **Multi-Provider Support**: Don't lock into single AI provider
2. **Graceful Degradation**: Handle AI service failures
3. **Consensus Mechanisms**: Use multiple AIs for critical decisions
4. **Learning Integration**: Improve AI performance over time
5. **Human Oversight**: Provide override mechanisms

### Performance Considerations
- Use async/await for I/O operations
- Implement caching for expensive AI calls
- Use connection pooling for external services
- Monitor memory usage for large operations
- Optimize for cold start scenarios

## 🛡️ Security Guidelines

### Code Security
- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all inputs from external sources
- Implement proper error handling
- Use secure communication protocols

### AI Security
- Validate AI responses before execution
- Implement rate limiting for AI calls
- Log all AI decisions for audit trails
- Use dry-run mode for testing
- Implement emergency stop mechanisms

## 🎯 Issue Triage and Labels

### Priority Labels
- `priority:critical` - System breaking, security issues
- `priority:high` - Important features, major bugs
- `priority:medium` - Standard features, minor bugs
- `priority:low` - Nice-to-have features, cosmetic issues

### Type Labels
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation related
- `ai-enhancement` - AI functionality improvements
- `security` - Security related
- `performance` - Performance improvements

### Status Labels
- `needs-triage` - Needs initial review
- `needs-reproduction` - Bug needs reproduction
- `needs-design` - Needs design discussion
- `ready-for-dev` - Ready for implementation
- `in-progress` - Currently being worked on

## 🚀 Release Process

### Version Numbering
We follow Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Release Checklist
1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Test AI functionality end-to-end
5. Create release PR
6. Tag release after merge
7. Deploy to production environment

## 🆘 Getting Help

### Where to Ask Questions
- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Code Comments**: Implementation questions in PRs
- **Documentation**: Check `docs/` directory first

### Maintainer Response Times
- **Critical Issues**: Within 4 hours
- **Bug Reports**: Within 2 business days
- **Feature Requests**: Within 1 week
- **PRs**: Within 1 week for initial review

## 🏆 Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Annual contributor reports
- Special recognition for AI improvements

Thank you for contributing to the future of intelligent automation! 🤖✨

