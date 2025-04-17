# Technical Debt Analyzer

A comprehensive tool for analyzing technical debt in Python projects through IDE plugins. This tool combines git history analysis, static code analysis, and risk scoring to provide real-time insights into technical debt and code quality directly within your IDE.

## Features

- **Git Activity Analysis**
  - Last modified date tracking
  - Change frequency analysis
  - Authorship churn metrics

- **Static Code Analysis**
  - Code complexity (using Radon)
  - Dead code detection (using Vulture)
  - Code smells (using Pylint)
  - Test coverage analysis

- **Risk Scoring**
  - Composite risk scores based on multiple metrics
  - Configurable weights for different factors
  - Aging, maintainability, and complexity scoring

- **IDE Integration**
  - Real-time code quality feedback
  - Inline annotations for technical debt
  - Quick fixes and suggestions
  - Customizable analysis settings

## Supported IDEs

- VS Code (Coming Soon)
- PyCharm (Coming Soon)
- Sublime Text (Coming Soon)
- Vim (Coming Soon)

## Project Structure

```
tech_debt_analyzer/
├── core/                 # Core analysis engine
│   ├── git_analyzer/     # Git activity analysis
│   ├── static_analyzer/  # Static code analysis
│   └── risk_scorer/     # Risk scoring and aggregation
├── ide_plugins/          # IDE-specific plugin implementations
│   ├── vscode/          # VS Code extension
│   ├── pycharm/         # PyCharm plugin
│   ├── sublime/         # Sublime Text plugin
│   └── vim/             # Vim plugin
└── shared/              # Shared utilities and interfaces
```

## Development Status

This project is currently in active development. The following features are planned:

- [ ] VS Code Extension
  - [ ] Real-time analysis
  - [ ] Inline annotations
  - [ ] Quick fixes
  - [ ] Settings UI

- [ ] PyCharm Plugin
  - [ ] Integration with PyCharm's inspection system
  - [ ] Custom inspection rules
  - [ ] Quick fixes

- [ ] Sublime Text Plugin
  - [ ] Command palette integration
  - [ ] Status bar indicators
  - [ ] Custom commands

- [ ] Vim Plugin
  - [ ] Vim commands
  - [ ] Quickfix integration
  - [ ] Status line integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. We're particularly interested in contributions for:

- IDE plugin implementations
- New analysis features
- Performance improvements
- Documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.