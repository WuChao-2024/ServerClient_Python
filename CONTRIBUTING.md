# Contributing to Fast Inference Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## Getting Started

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/Server_OpenSource.git
   cd Server_OpenSource
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/original/Server_OpenSource.git
   ```

### Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy
```

## Development Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write clear, concise code
- Add comments for complex logic
- Update documentation if needed
- Add tests for new features

### 3. Test Your Changes

```bash
# Run tests
python -m pytest tests/

# Check code style
black --check .
flake8 .

# Type checking
mypy *.py
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve bug in inference"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specifics:

- **Line length**: 100 characters max
- **Indentation**: 4 spaces
- **Quotes**: Use single quotes for strings
- **Imports**: Group in order: standard library, third-party, local

### Code Formatting

Use `black` for automatic formatting:

```bash
black .
```

### Type Hints

Add type hints to function signatures:

```python
def process_data(data: np.ndarray, scale: float = 1.0) -> torch.Tensor:
    """Process input data."""
    pass
```

### Documentation

Use Google-style docstrings:

```python
def send_request(url: str, data: dict, timeout: int = 10) -> dict:
    """
    Send inference request to server.

    Args:
        url: Server URL
        data: Input data dictionary
        timeout: Request timeout in seconds

    Returns:
        dict: Response from server

    Raises:
        RuntimeError: If request fails
    """
    pass
```

## Testing

### Writing Tests

Create test files in `tests/` directory:

```python
# tests/test_feature.py
import unittest
from your_module import your_function


class TestFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass

    def test_basic_functionality(self):
        """Test basic functionality."""
        result = your_function(input_data)
        self.assertEqual(result, expected_output)

    def test_edge_cases(self):
        """Test edge cases."""
        with self.assertRaises(ValueError):
            your_function(invalid_input)
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_feature.py

# Run with coverage
python -m pytest --cov=. tests/
```

## Submitting Changes

### 1. Update Your Branch

```bash
git fetch upstream
git rebase upstream/main
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to GitHub and create a Pull Request
2. Fill in the PR template:
   - Description of changes
   - Related issues
   - Testing done
   - Screenshots (if applicable)

### 4. Code Review

- Address reviewer feedback
- Make requested changes
- Push updates to your branch

### 5. Merge

Once approved, your PR will be merged by a maintainer.

## Areas for Contribution

### High Priority

- [ ] Add more comprehensive tests
- [ ] Improve error handling
- [ ] Add performance benchmarks
- [ ] Improve documentation

### Features

- [ ] Add support for gRPC protocol
- [ ] Implement request batching
- [ ] Add model versioning
- [ ] Add A/B testing support
- [ ] Add request caching

### Documentation

- [ ] Add more usage examples
- [ ] Create video tutorials
- [ ] Translate documentation to more languages
- [ ] Add API reference

### Performance

- [ ] Optimize serialization
- [ ] Add GPU memory pooling
- [ ] Implement request queuing
- [ ] Add load balancing

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

Thank you for contributing! 🎉
