# Contributing to Classical Chinese Translator

Thank you for considering contributing to this project! Here are some guidelines to help you get started.

## Code of Conduct

- Respect fellow contributors and users
- Be open to constructive feedback
- Focus on improving the quality and functionality of the translation system

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:
- Clear title describing the issue
- Detailed steps to reproduce the bug
- Expected behavior vs. actual behavior
- Any error messages or logs
- Your environment (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for improvements! When proposing an enhancement:
- Describe the current limitation or problem
- Explain how your enhancement addresses it
- Provide examples of how the feature would work

### Code Contributions

1. Fork the repository
2. Create a new branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Add or update tests as needed
5. Update documentation if relevant
6. Commit your changes (`git commit -m 'Add new feature'`)
7. Push to your branch (`git push origin feature/my-feature`)
8. Open a Pull Request

### Pull Request Guidelines

- Keep PRs focused on a single change
- Update documentation for any changed functionality
- Make sure the code passes all tests
- Follow the existing code style

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For development, also install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Testing

Run tests with:
```bash
python -m unittest discover tests
```

## Documentation

- Keep docstrings up to date
- Follow Google-style docstring format
- Update README.md and other docs when adding or changing features

## Feature Focus Areas

These areas could use improvement and would be particularly welcome:

1. **Alternative Language Models**: Support for different translation models
2. **Performance Optimization**: Improve token usage and processing speed
3. **Batch Processing**: Support for translating multiple files
4. **GUI Interface**: A simple interface for non-technical users
5. **Quality Metrics**: Automated evaluation of translation quality

## Questions?

If you have any questions or need help, please open an issue asking for help or clarification.

Thank you for contributing!
