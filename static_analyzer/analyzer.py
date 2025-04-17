"""
Static Code Analyzer implementation
"""
import json
import subprocess
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

import pandas as pd
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from vulture import Vulture

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class StaticCodeAnalyzer:
    def __init__(self, repo_path: str):
        """
        Initialize the Static Code Analyzer.
        
        Args:
            repo_path (str): Path to the repository to analyze
        """
        self.repo_path = Path(repo_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize sets for ignored paths
        self.ignored_paths: Set[str] = set()
        self._setup_ignored_paths()
        
        # Get filtered Python files
        self.python_files = self._get_filtered_python_files()

    def _setup_ignored_paths(self):
        """Setup paths to ignore during analysis."""
        # Ignore site-packages
        self.ignored_paths.add('site-packages')
        # Ignore common cache and build directories
        self.ignored_paths.update({
            '__pycache__',
            '.pytest_cache',
            '.git',
            'node_modules',
            'venv',
            '.venv',
            'env',
            'dist',
            'build',
            '.mypy_cache',
            '.ruff_cache'
        })

    def _should_ignore_file(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored based on its path.
        
        Args:
            file_path (Path): The path to check
            
        Returns:
            bool: True if the file should be ignored, False otherwise
        """
        # Check if the path is in site-packages
        if 'site-packages' in file_path.parts:
            return True
            
        # Check if any of the ignored directories are in the path
        for part in file_path.parts:
            if part in self.ignored_paths:
                return True
                
        return False

    def _get_filtered_python_files(self) -> List[Path]:
        """
        Get all Python files in the repository, excluding ignored paths.
        
        Returns:
            List[Path]: List of Python file paths
        """
        self.logger.info("Collecting Python files...")
        python_files = []
        
        for file_path in self.repo_path.rglob('*.py'):
            if not self._should_ignore_file(file_path):
                python_files.append(file_path)
                
        self.logger.info(f"Found {len(python_files)} Python files after filtering")
        return python_files

    def analyze_complexity(self) -> pd.DataFrame:
        """
        Analyze code complexity using Radon.
        
        Returns:
            pd.DataFrame: DataFrame with complexity metrics per file/function
        """
        complexity_data = []
        for file_path in self.python_files:
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                
                # Get complexity metrics
                results = cc_visit(code)
                for item in results:
                    complexity_data.append({
                        'file_path': str(file_path.relative_to(self.repo_path)),
                        'function_name': item.name,
                        'complexity': item.complexity,
                        'line_number': item.lineno
                    })
            except Exception as e:
                print(f"Error analyzing {file_path}: {str(e)}")
        
        return pd.DataFrame(complexity_data)

    def analyze_maintainability(self) -> pd.DataFrame:
        """
        Analyze code maintainability using Radon's maintainability index.
        
        Returns:
            pd.DataFrame: DataFrame with maintainability metrics per file
        """
        maintainability_data = []
        for file_path in self.python_files:
            try:
                with open(file_path, 'r') as f:
                    code = f.read()
                
                mi_score = mi_visit(code, multi=True)
                maintainability_data.append({
                    'file_path': str(file_path.relative_to(self.repo_path)),
                    'maintainability_index': mi_score
                })
            except Exception as e:
                print(f"Error analyzing {file_path}: {str(e)}")
        
        return pd.DataFrame(maintainability_data)

    def analyze_dead_code(self) -> pd.DataFrame:
        """
        Analyze dead code using Vulture.
        
        Returns:
            pd.DataFrame: DataFrame with dead code findings
        """
        dead_code_data = []
        for file_path in self.python_files:
            try:
                vulture = Vulture()
                with open(file_path, 'r') as f:
                    code = f.read()
                vulture.scan(code, filename=str(file_path))
                
                for item in vulture.get_unused_code():
                    dead_code_data.append({
                        'file_path': str(file_path.relative_to(self.repo_path)),
                        'first_line': item.first_lineno,
                        'last_line': item.last_lineno,
                        'type': item.typ,
                        'name': item.name,
                        'message': item.message,
                        'confidence': item.confidence
                    })
            except Exception as e:
                self.logger.error(f"Error analyzing {file_path}: {str(e)}")
        
        return pd.DataFrame(dead_code_data)

    def analyze_code_smells(self) -> pd.DataFrame:
        """
        Analyze code smells using Pylint.
        
        Returns:
            pd.DataFrame: DataFrame with code smell findings
        """
        # Run pylint and capture output
        cmd = ['pylint', '--output-format=json', str(self.repo_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        try:
            pylint_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            pylint_data = []
        
        smell_data = []
        for item in pylint_data:
            smell_data.append({
                'file_path': str(Path(item['path']).relative_to(self.repo_path)),
                'line_number': item['line'],
                'message': item['message'],
                'message_id': item['message-id'],
                'symbol': item['symbol']
            })
        
        return pd.DataFrame(smell_data)

    def analyze_test_coverage(self) -> pd.DataFrame:
        """
        Analyze test coverage using coverage.py.
        
        Returns:
            pd.DataFrame: DataFrame with coverage metrics
        """
        try:
            # Check if tests directory exists and has test files
            tests_dir = self.repo_path / 'tests'
            if not tests_dir.exists():
                self.logger.warning("No tests directory found. Skipping coverage analysis.")
                return pd.DataFrame()
            
            # Check for test files
            test_files = list(tests_dir.glob('test_*.py'))
            if not test_files:
                self.logger.warning("No test files found in tests directory. Skipping coverage analysis.")
                return pd.DataFrame()
            
            # Run coverage analysis
            cmd = ['coverage', 'run', '-m', 'pytest', str(tests_dir)]
            result = subprocess.run(cmd, cwd=str(self.repo_path), capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.warning(f"Test execution failed: {result.stderr}")
                return pd.DataFrame()
            
            # Get coverage report
            cmd = ['coverage', 'json', '--include=*.py']
            result = subprocess.run(cmd, cwd=str(self.repo_path), capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.warning(f"Failed to generate coverage report: {result.stderr}")
                return pd.DataFrame()
            
            try:
                with open('coverage.json', 'r') as f:
                    coverage_data = json.load(f)
            except FileNotFoundError:
                self.logger.warning("No coverage data found. Skipping coverage analysis.")
                return pd.DataFrame()
            
            if not coverage_data.get('files'):
                self.logger.warning("No files were covered during testing. Skipping coverage analysis.")
                return pd.DataFrame()
            
            coverage_metrics = []
            for file_path, metrics in coverage_data['files'].items():
                # Skip test files themselves
                if 'tests/' in file_path:
                    continue
                    
                coverage_metrics.append({
                    'file_path': str(Path(file_path).relative_to(self.repo_path)),
                    'line_coverage': metrics['summary']['percent_covered'],
                    'missing_lines': len(metrics['missing_lines']),
                    'excluded_lines': len(metrics['excluded_lines'])
                })
            
            if not coverage_metrics:
                self.logger.warning("No coverage data for non-test files. Skipping coverage analysis.")
                return pd.DataFrame()
            
            return pd.DataFrame(coverage_metrics)
        except Exception as e:
            self.logger.error(f"Error in coverage analysis: {str(e)}")
            return pd.DataFrame()

    def analyze(self) -> Dict[str, pd.DataFrame]:
        """
        Run all static analyses and return a dictionary of results.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all analysis results
        """
        return {
            'complexity': self.analyze_complexity(),
            'maintainability': self.analyze_maintainability(),
            'dead_code': self.analyze_dead_code(),
            'code_smells': self.analyze_code_smells(),
            'test_coverage': self.analyze_test_coverage()
        } 