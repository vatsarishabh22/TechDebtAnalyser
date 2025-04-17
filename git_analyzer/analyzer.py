"""
Git Activity Analyzer implementation
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import pandas as pd
from git import Repo
from pydriller import Repository, Commit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

class GitActivityAnalyzer:
    def __init__(self, repo_path: str):
        """
        Initialize the Git Activity Analyzer.
        
        Args:
            repo_path (str): Path to the git repository
        """
        self.repo_path = Path(repo_path)
        self.repo = Repo(str(self.repo_path))
        self.logger = logging.getLogger(__name__)
        
        # Initialize sets for ignored paths
        self.ignored_paths: Set[str] = set()
        self._setup_ignored_paths()
        
        # Initialize repository with filtered commits
        self.driller_repo = self._get_filtered_repository()

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

    def _should_ignore_file(self, file_path: str) -> bool:
        """
        Check if a file should be ignored based on its path.
        
        Args:
            file_path (str): The path to check
            
        Returns:
            bool: True if the file should be ignored, False otherwise
        """
        if not file_path:
            return True
            
        # Convert to Path object for proper path handling
        path = Path(file_path)
        
        # Check if the path is in site-packages
        if 'site-packages' in path.parts:
            return True
            
        # Check if any of the ignored directories are in the path
        for part in path.parts:
            if part in self.ignored_paths:
                return True
                
        return False

    def _should_ignore_commit(self, commit: Commit) -> bool:
        """
        Check if a commit should be ignored based on its modified files.
        
        Args:
            commit (Commit): The commit to check
            
        Returns:
            bool: True if the commit should be ignored, False otherwise
        """
        for modified_file in commit.modified_files:
            if self._should_ignore_file(modified_file.new_path):
                return True
        return False

    def _get_filtered_repository(self) -> Repository:
        """
        Create a filtered repository that excludes commits modifying ignored files.
        
        Returns:
            Repository: Filtered repository instance
        """
        # Initialize repository with basic filters
        repo = Repository(
            str(self.repo_path),
            only_modifications_with_file_types=['.py'],
            only_in_branch='main',
            only_no_merge=True
        )
        
        # Get all commit hashes that don't modify ignored files
        valid_commits = set()
        for commit in repo.traverse_commits():
            if not self._should_ignore_commit(commit):
                valid_commits.add(commit.hash)
        
        # Return a new repository instance with the filtered commits
        return Repository(
            str(self.repo_path),
            only_modifications_with_file_types=['.py'],
            only_in_branch='main',
            only_no_merge=True,
            only_commits=valid_commits
        )

    def get_file_last_modified(self) -> pd.DataFrame:
        """
        Get the last modified date for each file in the repository.
        
        Returns:
            pd.DataFrame: DataFrame with file paths and their last modified dates
        """
        try:
            self.logger.info("Starting file last modified analysis...")
            file_dates = []
            total_commits = sum(1 for _ in self.driller_repo.traverse_commits())
            processed_commits = 0
            
            for commit in self.driller_repo.traverse_commits():
                processed_commits += 1
                if processed_commits % 100 == 0:
                    self.logger.info(f"Processed {processed_commits}/{total_commits} commits")
                
                for modified_file in commit.modified_files:
                    if self._should_ignore_file(modified_file.new_path):
                        continue
                        
                    file_dates.append({
                        'file_path': modified_file.new_path,
                        'last_modified': commit.committer_date,
                        'author': commit.author.name
                    })
            
            df = pd.DataFrame(file_dates)
            if not df.empty:
                df = df.sort_values('last_modified').groupby('file_path').last().reset_index()
            self.logger.info("File last modified analysis completed successfully")
            return df
            
        except Exception as e:
            self.logger.error(f"Error in get_file_last_modified: {str(e)}")
            raise

    def get_change_frequency(self, time_window: str = '30D') -> pd.DataFrame:
        """
        Calculate change frequency for each file.
        
        Args:
            time_window (str): Pandas time window string (e.g., '30D' for 30 days)
            
        Returns:
            pd.DataFrame: DataFrame with file paths and their change frequencies
        """
        try:
            self.logger.info("Starting change frequency analysis...")
            changes = []
            total_commits = sum(1 for _ in self.driller_repo.traverse_commits())
            processed_commits = 0
            
            for commit in self.driller_repo.traverse_commits():
                processed_commits += 1
                if processed_commits % 100 == 0:
                    self.logger.info(f"Processed {processed_commits}/{total_commits} commits")
                
                for modified_file in commit.modified_files:
                    if self._should_ignore_file(modified_file.new_path):
                        continue
                        
                    changes.append({
                        'file_path': modified_file.new_path,
                        'commit_date': commit.committer_date
                    })
            
            df = pd.DataFrame(changes)
            if df.empty:
                self.logger.warning("No changes found in the repository")
                return pd.DataFrame()
                
            # Convert to UTC and then to datetime64
            df['commit_date'] = pd.to_datetime(df['commit_date'], utc=True)
            df.set_index('commit_date', inplace=True)
            
            # Resample and count changes per time window
            frequency = df.groupby('file_path').resample(time_window).size()
            frequency = frequency.reset_index()
            frequency.columns = ['file_path', 'window_end', 'change_count']
            
            self.logger.info("Change frequency analysis completed successfully")
            return frequency
            
        except Exception as e:
            self.logger.error(f"Error in get_change_frequency: {str(e)}")
            raise

    def get_authorship_churn(self) -> pd.DataFrame:
        """
        Calculate authorship churn metrics for each file.
        
        Returns:
            pd.DataFrame: DataFrame with file paths and authorship metrics
        """
        try:
            self.logger.info("Starting authorship churn analysis...")
            author_changes = []
            total_commits = sum(1 for _ in self.driller_repo.traverse_commits())
            processed_commits = 0
            
            for commit in self.driller_repo.traverse_commits():
                processed_commits += 1
                if processed_commits % 100 == 0:
                    self.logger.info(f"Processed {processed_commits}/{total_commits} commits")
                
                for modified_file in commit.modified_files:
                    if self._should_ignore_file(modified_file.new_path):
                        continue
                        
                    author_changes.append({
                        'file_path': modified_file.new_path,
                        'author': commit.author.name,
                        'changes': modified_file.added_lines + modified_file.deleted_lines
                    })
            
            df = pd.DataFrame(author_changes)
            if df.empty:
                self.logger.warning("No author changes found in the repository")
                return pd.DataFrame()
                
            # Calculate metrics
            author_metrics = df.groupby(['file_path', 'author']).agg({
                'changes': 'sum'
            }).reset_index()
            
            # Calculate total changes per file
            total_changes = author_metrics.groupby('file_path')['changes'].sum()
            
            # Calculate author distribution
            author_dist = author_metrics.groupby('file_path').agg({
                'author': 'count',
                'changes': lambda x: x.nlargest(2).sum() / total_changes[x.name] if total_changes[x.name] > 0 else 0
            })
            
            author_dist.columns = ['num_authors', 'top_two_authors_contribution']
            self.logger.info("Authorship churn analysis completed successfully")
            return author_dist.reset_index()
            
        except Exception as e:
            self.logger.error(f"Error in get_authorship_churn: {str(e)}")
            raise

    def analyze(self) -> Dict[str, pd.DataFrame]:
        """
        Run all analyses and return a dictionary of results.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all analysis results
        """
        try:
            self.logger.info("Starting repository analysis...")
            results = {
                'last_modified': self.get_file_last_modified(),
                'change_frequency': self.get_change_frequency(),
                'authorship_churn': self.get_authorship_churn()
            }
            self.logger.info("Repository analysis completed successfully")
            return results
        except Exception as e:
            self.logger.error(f"Error in analyze: {str(e)}")
            raise 