import os
import tempfile
from pathlib import Path
import pytest
import git
from git_analyzer.analyzer import GitActivityAnalyzer

@pytest.fixture
def sample_git_repo():
    """Create a temporary Git repository with some sample commits."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize a Git repository
        repo = git.Repo.init(tmpdir)
        
        # Create a sample Python file
        file_path = Path(tmpdir) / "sample.py"
        with open(file_path, "w") as f:
            f.write("def hello():\n    return 'Hello, World!'\n")
        
        # Add and commit the file
        repo.index.add([str(file_path)])
        repo.index.commit("Initial commit")
        
        # Make some changes and commit
        with open(file_path, "a") as f:
            f.write("\ndef goodbye():\n    return 'Goodbye, World!'\n")
        
        repo.index.add([str(file_path)])
        repo.index.commit("Add goodbye function")
        
        yield tmpdir

def test_analyze_change_frequency(sample_git_repo):
    """Test change frequency analysis on a sample Git repository."""
    analyzer = GitActivityAnalyzer(sample_git_repo)
    git_metrics = analyzer.analyze()
    
    assert 'change_frequency' in git_metrics
    change_freq_df = git_metrics['change_frequency']
    
    assert not change_freq_df.empty
    assert 'file_path' in change_freq_df.columns
    assert 'window_end' in change_freq_df.columns
    assert 'change_count' in change_freq_df.columns

def test_analyze_file_age(sample_git_repo):
    """Test file age analysis on a sample Git repository."""
    analyzer = GitActivityAnalyzer(sample_git_repo)
    git_metrics = analyzer.analyze()
    
    assert 'file_age' in git_metrics
    file_age_df = git_metrics['file_age']
    
    assert not file_age_df.empty
    assert 'file_path' in file_age_df.columns
    assert 'last_modified' in file_age_df.columns
    assert 'age_days' in file_age_df.columns 