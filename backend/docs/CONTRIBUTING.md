# Contributing Guidelines

Terima kasih atas minat Anda untuk berkontribusi pada Food Recommendation Chatbot Backend!

---

## 🎯 Ways to Contribute

### 1. Report Bugs
- Use GitHub Issues (if applicable)
- Provide detailed description
- Include error messages
- Share reproduction steps

### 2. Suggest Features
- Check [IMPROVEMENTS.md](IMPROVEMENTS.md) first
- Explain use case
- Describe expected behavior
- Consider implementation complexity

### 3. Improve Documentation
- Fix typos
- Add examples
- Clarify explanations
- Update outdated info

### 4. Submit Code
- Fix bugs
- Add features
- Improve performance
- Refactor code

---

## 🚀 Getting Started

### 1. Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd food-chatbot-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials

# Run tests
python run_tests.py

# Ingest data
python ingest_data.py

# Start server
python main.py
```

### 2. Create a Branch

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or bugfix branch
git checkout -b fix/bug-description
```

### 3. Make Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation

### 4. Test Your Changes

```bash
# Run all tests
python run_tests.py

# Test specific component
python test_api.py

# Manual testing
curl http://localhost:8000/health
```

### 5. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add streaming response support"
```

### 6. Push and Create PR

```bash
# Push to your branch
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

---

## 📝 Code Style Guidelines

### Python Style

Follow PEP 8 with these specifics:

```python
# Good
def calculate_status(opening_time: str, closing_time: str) -> str:
    """
    Calculate operational status of restaurant.
    
    Args:
        opening_time: Opening time in HH:MM format
        closing_time: Closing time in HH:MM format
    
    Returns:
        Status string (e.g., "Buka Sekarang")
    """
    # Implementation
    pass

# Bad
def calc_stat(o,c):
    # no docstring, unclear names
    pass
```

### Naming Conventions

```python
# Classes: PascalCase
class RestaurantCard:
    pass

# Functions: snake_case
def get_current_time():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RESULTS = 10

# Private: _leading_underscore
def _internal_helper():
    pass
```

### Type Hints

Always use type hints:

```python
# Good
def search_restaurants(query: str, limit: int = 10) -> List[dict]:
    pass

# Bad
def search_restaurants(query, limit=10):
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int) -> dict:
    """
    Brief description of function.
    
    Longer description if needed. Explain what the function does,
    any important details, edge cases, etc.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
    
    Example:
        >>> result = complex_function("test", 5)
        >>> print(result)
        {'status': 'success'}
    """
    pass
```

---

## 🧪 Testing Guidelines

### Write Tests for New Features

```python
# test_new_feature.py
import pytest
from your_module import your_function

def test_your_function_success():
    """Test successful case"""
    result = your_function("input")
    assert result == "expected"

def test_your_function_error():
    """Test error handling"""
    with pytest.raises(ValueError):
        your_function("invalid")
```

### Test Coverage

- Aim for >80% coverage
- Test happy paths
- Test error cases
- Test edge cases

### Manual Testing

Before submitting:
1. Test all API endpoints
2. Verify error handling
3. Check response format
4. Test with different inputs

---

## 📚 Documentation Guidelines

### Update Documentation

When making changes, update:

1. **Code Comments**
   - Explain complex logic
   - Document assumptions
   - Note TODOs

2. **Docstrings**
   - Update function descriptions
   - Update parameters
   - Update return values

3. **README.md**
   - Update if API changes
   - Add new features
   - Update examples

4. **CHANGELOG.md**
   - Add entry for your change
   - Follow format
   - Include version

5. **API_REFERENCE.md**
   - Update if endpoints change
   - Add new endpoints
   - Update examples

### Documentation Style

```markdown
# Use Clear Headings

## Subsections

### Details

- Use bullet points
- Keep it concise
- Add examples

**Bold** for emphasis
`code` for technical terms

```python
# Code blocks with syntax highlighting
def example():
    pass
```

[Links](URL) to related docs
```

---

## 🔄 Commit Message Format

Use conventional commits:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, etc)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```bash
# Feature
git commit -m "feat(api): add streaming response support"

# Bug fix
git commit -m "fix(rag): correct time zone calculation"

# Documentation
git commit -m "docs(readme): update installation steps"

# With body
git commit -m "feat(search): improve vector search accuracy

- Increase top_k to 15
- Add relevance threshold
- Filter by score"

# Breaking change
git commit -m "feat(api): change response format

BREAKING CHANGE: restaurants field now returns array of objects instead of strings"
```

---

## 🐛 Bug Report Template

When reporting bugs, include:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows/Linux/Mac
- Python version: 3.9
- Package versions: (from pip list)

## Error Messages
```
Paste full error message and traceback
```

## Additional Context
Any other relevant information
```

---

## 💡 Feature Request Template

When suggesting features:

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?
Who will benefit?

## Proposed Solution
How should it work?

## Alternatives Considered
Other ways to solve this

## Additional Context
Mockups, examples, references
```

---

## 🔍 Code Review Checklist

Before submitting PR:

### Functionality
- [ ] Code works as intended
- [ ] All tests pass
- [ ] No breaking changes (or documented)
- [ ] Error handling implemented

### Code Quality
- [ ] Follows style guidelines
- [ ] No code duplication
- [ ] Efficient implementation
- [ ] Readable and maintainable

### Documentation
- [ ] Code comments added
- [ ] Docstrings updated
- [ ] README updated if needed
- [ ] CHANGELOG updated

### Testing
- [ ] Unit tests added
- [ ] Integration tests pass
- [ ] Manual testing done
- [ ] Edge cases covered

---

## 🎨 Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing done

## Screenshots (if applicable)
Add screenshots

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added
- [ ] All tests pass
```

---

## 🚫 What NOT to Do

### Don't
- ❌ Submit untested code
- ❌ Break existing functionality
- ❌ Ignore code style
- ❌ Skip documentation
- ❌ Commit secrets/credentials
- ❌ Make unrelated changes
- ❌ Use offensive language

### Do
- ✅ Test thoroughly
- ✅ Follow guidelines
- ✅ Write clear commits
- ✅ Update documentation
- ✅ Ask questions
- ✅ Be respectful
- ✅ Keep PRs focused

---

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in CHANGELOG.md
- Credited in release notes

---

## 📞 Getting Help

### Questions?
- Check documentation first
- Search existing issues
- Ask in discussions
- Contact maintainers

### Stuck?
- Review examples
- Check troubleshooting guide
- Ask for help
- Pair with maintainer

---

## 📋 Development Workflow

### 1. Planning
- Discuss feature/fix
- Get approval
- Plan implementation

### 2. Development
- Create branch
- Write code
- Add tests
- Update docs

### 3. Review
- Self-review
- Run tests
- Check style
- Update changelog

### 4. Submit
- Push branch
- Create PR
- Address feedback
- Merge

### 5. Release
- Version bump
- Update changelog
- Tag release
- Deploy

---

## 🔐 Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email security contact
2. Provide detailed description
3. Include reproduction steps
4. Suggest fix if possible

### Security Best Practices

- Never commit secrets
- Use environment variables
- Validate all inputs
- Sanitize user data
- Follow OWASP guidelines

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## 🙏 Thank You!

Every contribution helps make this project better. Whether it's:
- Reporting a bug
- Suggesting a feature
- Fixing a typo
- Writing code

Your effort is appreciated! 🎉

---

## 📚 Additional Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Questions?** Check [INDEX.md](INDEX.md) for documentation navigation.
