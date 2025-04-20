# Technical Debt Analyzer

A Python-based tool that analyzes technical debt in codebases by combining git history analysis, static code analysis, and risk scoring. Built with Streamlit for easy deployment and visualization.

## Key Features

- **Git Analysis**: Track file modification history, change frequency, and authorship patterns
- **Static Analysis**: Measure code complexity, detect dead code, and identify code smells
- **Risk Scoring**: Calculate technical debt risk based on multiple metrics
- **Streamlit Dashboard**: Interactive visualization of analysis results

## Project Structure

```
tech_debt_analyzer/
├── git_analyzer/     # Git history analysis
├── static_analyzer/  # Code quality analysis
├── risk_scorer/     # Risk calculation
├── visualizer/      # Streamlit dashboard
└── utils/           # Shared utilities
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Clone the repository
2. Install dependencies
3. Run the Streamlit app:
```bash
streamlit run application.py
```

## Future Enhancements

- Enhanced visualization capabilities
- Customizable analysis parameters
- Integration with CI/CD pipelines
- Support for multiple programming languages

## License

MIT License