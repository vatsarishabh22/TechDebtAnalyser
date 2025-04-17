from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tech-debt-analyzer",
    version="0.1.0",
    author="Rishabh Vatsa",
    author_email="vatsarishabh22@gmail.com",
    description="A comprehensive tool for analyzing technical debt in Python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tech-debt-analyzer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "streamlit==1.32.0",
        "pandas==2.2.1",
        "gitpython==3.1.30",
        "python-dateutil==2.8.2",
        "pydriller==2.5",
        "pytz==2024.1",
        
        # Module 1: Git Activity Analyzer
        "matplotlib==3.8.3",
        "seaborn==0.13.2",
        
        # Module 2: Static Code Analyzer
        "radon==6.0.1",
        "vulture==2.10",
        "pylint==3.0.3",
        "pytest-cov==4.1.0",
        "coverage==7.4.1",
        
        # Module 3: Risk Scoring & Aggregation
        "numpy==1.26.4",
        "scikit-learn==1.4.1.post1",
        
        # Module 4: Visualization & Interaction
        "plotly==5.19.0",
        "dash==2.15.0",
    ],
    entry_points={
        "console_scripts": [
            "tech-debt-analyzer=tech_debt_analyzer.main:main",
        ],
    },
) 