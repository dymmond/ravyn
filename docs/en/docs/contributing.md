# Contributing to Ravyn

Thank you for your interest in contributing to Ravyn! We welcome contributions from the community and appreciate your help in making Ravyn better.

## What You'll Learn

- How to set up your development environment with hatch
- Contribution workflow and guidelines
- Code style and testing requirements
- How to submit pull requests
- Where to get help

## Quick Start

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/ravyn.git
cd ravyn

# 2. Install hatch
pip install hatch

# 3. Create development environments (optional, hatch does this automatically)
hatch env create
hatch env create test
hatch env create docs

# 4. Run tests to verify setup
hatch run test:test

# 5. Create a branch for your changes
git checkout -b feature/my-awesome-feature

# 6. Make your changes and test
hatch run test:test
hatch run lint

# 7. Commit and push
git add .
git commit -m "Add awesome feature"
git push origin feature/my-awesome-feature

# 8. Open a pull request on GitHub
```

---

## Ways to Contribute

### 🐛 Report Bugs

Found a bug? Please start with a [discussion](https://github.com/dymmond/ravyn/discussions) as "Potential Issue":

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, Ravyn version)
- Code snippets and tracebacks

### Suggest Features

Have an idea? [Open a discussion](https://github.com/dymmond/ravyn/discussions) as "Ideas":

- Clear description of the feature
- Use cases and benefits
- Proposed implementation (if you have ideas)

### 📝 Improve Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add examples
- Improve existing guides
- Write tutorials

### 🔧 Submit Code

Code contributions should:

- Fix bugs
- Add new features
- Improve performance
- Enhance existing functionality

---

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account

### Installation

```bash
# Fork the repository on GitHub first, then:

# Clone your fork
git clone https://github.com/YOUR_USERNAME/ravyn.git
cd ravyn

# Add upstream remote
git remote add upstream https://github.com/dymmond/ravyn.git

# Install hatch
pip install hatch
```

> [!INFO]
> Ravyn uses [hatch](https://hatch.pypa.io/latest/) for development, testing, and release cycles.

### Initialize Environments (Optional)

Hatch automatically creates environments when needed, but you can pre-initialize them:

```bash
# Create all environments
hatch env create
hatch env create test
hatch env create docs
```

!!! tip
    If you prefer your own virtual environment with all packages installed, you can run `scripts/install`.

### Verify Installation

```bash
# Run tests
hatch run test:test

# Run linting
hatch run lint

# Check formatting
hatch run format
```

---

## Contribution Workflow

### 1. Create a Discussion

Before starting work, create a [discussion](https://github.com/dymmond/ravyn/discussions) to talk about your changes.

### 2. Fork and Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/my-feature
# or
git checkout -b fix/bug-description
```

### 3. Make Changes

- Write clean, readable code
- Follow the code style guidelines
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run all tests
hatch run test:test

# Run specific test file
hatch run test:test tests/test_routing.py

# Run linting
hatch run lint

# Format code
hatch run format
```

### 5. Enable Pre-commit (Optional)

```bash
# Install pre-commit hooks
pre-commit install
```

### 6. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: description of what you did"
```

**Commit Message Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issue numbers when applicable

Examples:
```
Add support for WebSocket connections (#123)
Fix validation error in request handling (#456)
Update documentation for caching system
```

### 7. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/my-feature
```

Then open a pull request on GitHub with:

- Clear title describing the change
- Description of what changed and why
- Reference to related discussions/issues
- Screenshots (if UI changes)

---

## Testing

### Running Tests

```bash
# All tests
hatch run test:test

# Specific file
hatch run test:test tests/test_routing.py

# With coverage
hatch run test:test --cov=ravyn --cov-report=html

# Verbose output
hatch run test:test -v
```

> [!INFO]
> Ravyn uses pytest. Any additional arguments are passed directly to pytest.

### Writing Tests

```python
import pytest
from ravyn import Ravyn, get

def test_simple_route():
    """Test basic route functionality."""
    app = Ravyn()
    
    @get("/hello")
    def hello() -> dict:
        return {"message": "Hello, World!"}
    
    app.add_route(hello)
    
    from ravyn import RavynTestClient
    
    with RavynTestClient(app) as client:
        response = client.get("/hello")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, World!"}
```

---

## Documentation

### Building Documentation

```bash
# Build all documentation
hatch run docs:build

# Build specific language
hatch run docs:build_lang en
```

### Serving Documentation Locally

```bash
# Serve docs with live reload
hatch run docs:serve

# Serve on specific port
hatch run docs:serve -p 8080

# Serve specific language
hatch run docs:serve_lang es
```

The documentation will be available at `http://localhost:8000`.

!!! tip
    You can also manually run `mkdocs serve` in the `docs/en/` directory.

### Documentation Structure

- Documentation uses [MkDocs](https://www.mkdocs.org/)
- All docs are in Markdown format in `./docs/en/`
- Code examples are in `./docs_src/` directory
- Code blocks are included/injected when generating the site

---

## Code Style

### Linting and Formatting

```bash
# Run linting
hatch run lint

# Format code
hatch run format
```

### Python Style

We follow PEP 8 with some modifications:

```python
# Good
class UserController:
    """Handle user-related operations."""
    
    async def get_user(self, user_id: int) -> dict:
        """
        Get user by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            User data dictionary
        """
        user = await self.db.fetch_one("SELECT * FROM users WHERE id = ?", user_id)
        return user
```

### Type Hints

Always use type hints:

```python
# Good
async def create_user(name: str, email: str) -> dict:
    pass

# Bad - no type hints
async def create_user(name, email):
    pass
```

---

## Building Ravyn

### Local Build

```bash
# Build package locally
hatch build

# Or create a shell with installed package
hatch shell
```

---

## TaskFile (Alternative)

Ravyn also supports [TaskFile](https://taskfile.dev/installation/) as an alternative to hatch commands:

```bash
# List all available tasks
task

# Run tests manually
task test_man ARGS=tests/msgspec/
```

!!! warning
    TaskFile support may be discontinued in the future for a better alternative.

---

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Related Discussions/Issues
Relates to #123

## Testing
Describe how you tested your changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
```

---

## Translations

Help with translations is very much appreciated!

### Tips and Guidelines

- Check [existing pull requests](https://github.com/dymmond/ravyn/pulls) for your language
- Review PRs and request changes or approve them
- Check [GitHub Discussions](https://github.com/dymmond/ravyn/discussions/categories/translations) for translation coordination
- Add one pull request per page translated
- Use [ISO 639-1 codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) for language codes

### Translating Existing Language

```bash
# Serve docs for specific language (e.g., Spanish)
hatch run docs:serve_lang es
```

Then copy files from `docs/en/docs/` to `docs/es/docs/` and translate.

### Adding New Language

```bash
# Create new language directory (e.g., Creole with code 'ht')
hatch run docs:new_lang ht
```

This creates `docs/ht/mkdocs.yml` and `docs/ht/index.md` to get started.

---

## Getting Help

### Community

- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: Report bugs and request features
- **Pull Requests**: Review and contribute code

### Resources

- [Documentation](https://ravyn.dev)
- [GitHub Repository](https://github.com/dymmond/ravyn)
- [Examples](https://github.com/dymmond/ravyn/tree/main/examples)

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

**Do:**
- Be respectful and constructive
- Welcome newcomers
- Give credit where due
- Focus on what's best for the community

**Don't:**
- Use offensive language
- Make personal attacks
- Harass others
- Share private information

---

## Releasing

*This section is for the maintainers of `Ravyn`*.

### Building the Ravyn for release

Before releasing a new package into production some considerations need to be taken into account.

* **Changelog**
    * Like many projects, we follow the format from [keepchangelog](https://keepachangelog.com/en/1.0.0/).
    * [Compare](https://github.com/dymmond/ravyn/compare/) `main` with the release tag and list of the entries
that are of interest to the users of the framework.
        * What **must** go in the changelog? added, changed, removed or deprecated features and the bug fixes.
        * What is **should not go** in the changelog? Documentation changes, tests or anything not specified in the
point above.
        * Make sure the order of the entries are sorted by importance.
        * Keep it simple.

* *Version bump*
    * The version should be in `__init__.py` of the main package.

#### Releasing

Once the `release` PR is merged, create a new [release](https://github.com/dymmond/ravyn/releases/new)
that includes:

Example:

There will be a release of the version `0.2.3`, this is what it should include.

* Release title: `Version 0.2.3`.
* Tag: `0.2.3`.
* The description should be copied from the changelog.

Once the release is created, it should automatically upload the new version to PyPI. If something
does not work with PyPI the release can be done by running `scripts/release`.

---

## Thank You!

Your contributions make Ravyn better for everyone. We appreciate your time and effort! ---

## Next Steps

- [View Discussions](https://github.com/dymmond/ravyn/discussions)
- [View Open Issues](https://github.com/dymmond/ravyn/issues)
- [Read the Documentation](https://ravyn.dev)
