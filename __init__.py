"""
Tech Debt Analyzer - A comprehensive tool for analyzing technical debt in Python projects.
"""

__version__ = "0.1.0"

from .git_analyzer import GitActivityAnalyzer
from .static_analyzer import StaticCodeAnalyzer
from .risk_scorer import RiskScorer
from .visualizer import Visualizer 