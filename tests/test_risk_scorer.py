import pytest
import pandas as pd
from risk_scorer.scorer import RiskScorer

@pytest.fixture
def sample_metrics():
    """Create sample metrics for testing risk scoring."""
    # Sample git metrics
    git_metrics = {
        'change_frequency': pd.DataFrame({
            'file_path': ['file1.py', 'file2.py'],
            'window_end': ['2024-01-01', '2024-01-01'],
            'change_count': [5, 2]
        }),
        'file_age': pd.DataFrame({
            'file_path': ['file1.py', 'file2.py'],
            'last_modified': ['2024-01-01', '2023-12-01'],
            'age_days': [10, 40]
        })
    }
    
    # Sample static metrics
    static_metrics = {
        'complexity': pd.DataFrame({
            'file_path': ['file1.py', 'file2.py'],
            'function_name': ['func1', 'func2'],
            'complexity': [5, 3],
            'line_number': [10, 20]
        }),
        'maintainability': pd.DataFrame({
            'file_path': ['file1.py', 'file2.py'],
            'maintainability_index': [70, 85]
        }),
        'test_coverage': pd.DataFrame({
            'file_path': ['file1.py', 'file2.py'],
            'line_coverage': [80, 90],
            'missing_lines': [20, 10],
            'excluded_lines': [0, 0]
        })
    }
    
    return git_metrics, static_metrics

def test_calculate_risk_score(sample_metrics):
    """Test risk score calculation with sample metrics."""
    git_metrics, static_metrics = sample_metrics
    risk_scorer = RiskScorer(git_metrics, static_metrics)
    
    weights = {
        'aging': 0.2,
        'frequency': 0.2,
        'complexity': 0.3,
        'maintainability': 0.2,
        'coverage': 0.1
    }
    
    risk_scores = risk_scorer.calculate_risk_score(weights)
    
    assert not risk_scores.empty
    assert 'file_path' in risk_scores.columns
    assert 'risk_score' in risk_scores.columns
    assert all(0 <= score <= 1 for score in risk_scores['risk_score'])

def test_calculate_risk_score_missing_metrics(sample_metrics):
    """Test risk score calculation with missing metrics."""
    git_metrics, static_metrics = sample_metrics
    # Remove some metrics to test handling of missing data
    del static_metrics['test_coverage']
    
    risk_scorer = RiskScorer(git_metrics, static_metrics)
    
    weights = {
        'aging': 0.2,
        'frequency': 0.2,
        'complexity': 0.3,
        'maintainability': 0.2,
        'coverage': 0.1
    }
    
    risk_scores = risk_scorer.calculate_risk_score(weights)
    
    assert not risk_scores.empty
    assert 'file_path' in risk_scores.columns
    assert 'risk_score' in risk_scores.columns 