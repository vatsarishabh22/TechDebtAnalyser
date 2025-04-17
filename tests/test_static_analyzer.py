import os
import tempfile
from pathlib import Path
import pytest
from static_analyzer.analyzer import StaticCodeAnalyzer

@pytest.fixture
def sample_python_file():
    """Create a temporary Python file with some code to analyze."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a sample Python file
        file_path = Path(tmpdir) / "sample.py"
        with open(file_path, "w") as f:
            f.write("""
def example_function(x):
    if x > 0:
        return x * 2
    else:
        return x + 1

class ExampleClass:
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value
""")
        yield tmpdir

def test_analyze_complexity(sample_python_file):
    """Test complexity analysis on a sample Python file."""
    analyzer = StaticCodeAnalyzer(sample_python_file)
    complexity_df = analyzer.analyze_complexity()
    
    assert not complexity_df.empty
    assert 'file_path' in complexity_df.columns
    assert 'function_name' in complexity_df.columns
    assert 'complexity' in complexity_df.columns
    assert 'line_number' in complexity_df.columns

def test_analyze_maintainability(sample_python_file):
    """Test maintainability analysis on a sample Python file."""
    analyzer = StaticCodeAnalyzer(sample_python_file)
    maintainability_df = analyzer.analyze_maintainability()
    
    assert not maintainability_df.empty
    assert 'file_path' in maintainability_df.columns
    assert 'maintainability_index' in maintainability_df.columns

def test_analyze_dead_code(sample_python_file):
    """Test dead code analysis on a sample Python file."""
    analyzer = StaticCodeAnalyzer(sample_python_file)
    dead_code_df = analyzer.analyze_dead_code()
    
    # The DataFrame might be empty if no dead code is found
    if not dead_code_df.empty:
        assert 'file_path' in dead_code_df.columns
        assert 'first_line' in dead_code_df.columns
        assert 'last_line' in dead_code_df.columns
        assert 'type' in dead_code_df.columns
        assert 'name' in dead_code_df.columns

def test_analyze_code_smells(sample_python_file):
    """Test code smells analysis on a sample Python file."""
    analyzer = StaticCodeAnalyzer(sample_python_file)
    code_smells_df = analyzer.analyze_code_smells()
    
    # The DataFrame might be empty if no code smells are found
    if not code_smells_df.empty:
        assert 'file_path' in code_smells_df.columns
        assert 'line_number' in code_smells_df.columns
        assert 'message' in code_smells_df.columns
        assert 'message_id' in code_smells_df.columns
        assert 'symbol' in code_smells_df.columns 