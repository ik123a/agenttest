# Contributing to AgentTest

Thank you for your interest in contributing to AgentTest!

## Getting Started

1. Fork the repository
2. Clone your fork
3. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

## Development Setup

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=agenttest

# Build package
poetry build
```

## Code Style

- Use type hints
- Follow PEP 8
- Add docstrings to all public functions
- Keep functions focused and small

## Pull Requests

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Reporting Issues

Use GitHub Issues to report bugs or request features.

## Good First Issues

- Add more built-in mock tools
- Improve adapter for specific LangChain patterns
- Add more example scenarios
- Documentation improvements

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
