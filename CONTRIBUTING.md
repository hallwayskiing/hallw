# Contributing to HALLW

Thank you for your interest in contributing to HALLW! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check the [existing issues](https://github.com/hallwayskiing/hallw/issues) to see if the problem has already been reported.

When creating a bug report, please include:

- **Clear title**: A descriptive summary of the issue
- **Environment**: Python version, OS, browser version
- **Steps to reproduce**: Detailed steps to reproduce the behavior
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Logs**: Relevant log output (if applicable)
- **Screenshots**: If applicable, add screenshots to help explain the problem

### Suggesting Features

We welcome feature suggestions! Please open an issue with:

- **Clear description**: What feature would you like to see?
- **Use case**: Why is this feature useful?
- **Possible implementation**: If you have ideas, describe how it might work

### Pull Requests

1. **Fork the repository** and create your branch from `main`:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Set up development environment**:
   ```bash
   # Install in development mode
   pip install -e ".[dev]"

   # Install pre-commit hooks
   pre-commit install
   ```

3. **Make your changes**:
   - Write clean, documented code
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

4. **Test your changes**:
   ```bash
   # Run tests
   pytest

   # Run linting
   black --check .
   isort --check .
   mypy src/
   ```

5. **Commit your changes**:
   ```bash
   git commit -m "Add: description of your feature"
   ```

   Use clear commit messages following [Conventional Commits](https://www.conventionalcommits.org/):
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring
   - `Test:` for test additions/changes

6. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**:
   - Provide a clear description of changes
   - Reference any related issues
   - Ensure all CI checks pass

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Chrome/Chromium browser

### Setup Steps

1. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hallw.git
   cd hallw
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Playwright**:
   ```bash
   playwright install chromium
   ```

5. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing

### Running Code Quality Checks

```bash
# Format code
black .

# Sort imports
isort .

# Type check
mypy src/

# Run all checks
pre-commit run --all-files
```

## Adding New Tools

Tools are automatically discovered from the `src/hallw/tools/` directory. To add a new tool:

1. **Create a module** in `src/hallw/tools/` or a subdirectory:
   ```python
   from langchain_core.tools import tool
   from hallw.utils.logger import logger
   from hallw.tools.tool_response import build_tool_response

   @tool
   async def my_new_tool(param: str) -> str:
       """Brief description of what the tool does.

       Args:
           param: Description of param

       Returns:
           JSON string created via build_tool_response
       """
       try:
           # Your implementation
           result = "Tool result"
           # Always use build_tool_response to create tool responses
           return build_tool_response(True, "Success", {"result": result})
       except Exception as e:
           logger.error(f"my_new_tool error: {e}")
           # Return failure responses using build_tool_response
           return build_tool_response(False, f"Error: {e}")
   ```

   **Important**: All tools must return JSON strings created via `build_tool_response(success, message, data)`.
   This ensures consistent parsing and error handling across the agent framework.

2. **Add tests** in `tests/tools/test_my_new_tool.py`

3. **Update documentation** if needed

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=hallw --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_should_do_something_when_condition()`
- Test both success and failure cases
- Use fixtures for common setup
- Mock external dependencies

Example:
```python
import pytest
from hallw.tools.my_tool import my_tool

@pytest.mark.asyncio
async def test_my_tool_success():
    result = await my_tool("input")
    assert "success" in result.lower()

@pytest.mark.asyncio
async def test_my_tool_failure():
    result = await my_tool("")
    assert "error" in result.lower()
```

## Documentation

- Update `README.md` for user-facing changes
- Add docstrings to new functions/classes
- Update `CHANGELOG.md` for notable changes
- Include examples in docstrings when helpful

## Release Process

Releases are managed by maintainers. The process includes:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with new version
3. Create a git tag
4. Push to GitHub (CI/CD will publish to PyPI)

## Questions?

If you have questions about contributing, please:

- Open an issue with the `question` label
- Check existing issues and discussions
- Contact maintainers if needed

Thank you for contributing to HALLW! 🎉
