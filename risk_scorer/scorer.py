"""
Risk Scoring & Aggregation implementation
"""
from datetime import datetime
from typing import Dict, Optional

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class RiskScorer:
    def __init__(self, git_metrics: Dict[str, pd.DataFrame], 
                 static_metrics: Dict[str, pd.DataFrame]):
        """
        Initialize the Risk Scorer.
        
        Args:
            git_metrics (Dict[str, pd.DataFrame]): Metrics from Git Activity Analyzer
            static_metrics (Dict[str, pd.DataFrame]): Metrics from Static Code Analyzer
        """
        self.git_metrics = git_metrics
        self.static_metrics = static_metrics
        self.scaler = MinMaxScaler()

    def _normalize_metric(self, df: pd.DataFrame, column: str) -> pd.Series:
        """
        Normalize a metric column to [0, 1] range.
        
        Args:
            df (pd.DataFrame): DataFrame containing the metric
            column (str): Column name to normalize
            
        Returns:
            pd.Series: Normalized values
        """
        if df.empty or column not in df.columns:
            return pd.Series()
        
        values = df[column].values.reshape(-1, 1)
        normalized = self.scaler.fit_transform(values)
        return pd.Series(normalized.flatten(), index=df.index)

    def calculate_aging_score(self) -> pd.DataFrame:
        """
        Calculate aging score based on file modification dates.
        
        Returns:
            pd.DataFrame: DataFrame with aging scores
        """
        try:
            # Get last modified dates
            last_modified = self.git_metrics['last_modified']
            if last_modified.empty:
                return pd.DataFrame()
            
            # Convert to UTC datetime
            last_modified['last_modified'] = pd.to_datetime(last_modified['last_modified'], utc=True)
            
            # Calculate age in days
            now = pd.Timestamp.now(tz='UTC')
            last_modified['age_days'] = (now - last_modified['last_modified']).dt.total_seconds() / (24 * 3600)
            
            # Calculate aging score (higher score for older files)
            max_age = last_modified['age_days'].max()
            last_modified['aging_score'] = last_modified['age_days'] / max_age if max_age > 0 else 0
            
            return last_modified[['file_path', 'aging_score']]
            
        except Exception as e:
            self.logger.error(f"Error calculating aging score: {str(e)}")
            return pd.DataFrame()

    def calculate_change_frequency_score(self) -> pd.DataFrame:
        """
        Calculate change frequency score.
        
        Returns:
            pd.DataFrame: DataFrame with change frequency scores
        """
        change_freq = self.git_metrics['change_frequency']
        if change_freq.empty:
            return pd.DataFrame()
        
        # Aggregate change counts per file
        freq_scores = change_freq.groupby('file_path')['change_count'].mean()
        freq_scores = freq_scores.reset_index()
        
        # Normalize and calculate frequency score
        freq_scores['frequency_score'] = self._normalize_metric(
            freq_scores, 'change_count'
        )
        
        return freq_scores[['file_path', 'frequency_score']]

    def calculate_complexity_score(self) -> pd.DataFrame:
        """
        Calculate complexity score based on cyclomatic complexity.
        
        Returns:
            pd.DataFrame: DataFrame with complexity scores
        """
        complexity = self.static_metrics['complexity']
        if complexity.empty:
            return pd.DataFrame()
        
        # Aggregate complexity per file
        comp_scores = complexity.groupby('file_path')['complexity'].mean()
        comp_scores = comp_scores.reset_index()
        
        # Normalize and calculate complexity score
        comp_scores['complexity_score'] = self._normalize_metric(
            comp_scores, 'complexity'
        )
        
        return comp_scores[['file_path', 'complexity_score']]

    def calculate_maintainability_score(self) -> pd.DataFrame:
        """
        Calculate maintainability score based on maintainability index.
        
        Returns:
            pd.DataFrame: DataFrame with maintainability scores
        """
        maintainability = self.static_metrics['maintainability']
        if maintainability.empty:
            return pd.DataFrame()
        
        # Normalize maintainability index (higher is better)
        maintainability['maintainability_score'] = self._normalize_metric(
            maintainability, 'maintainability_index'
        )
        
        return maintainability[['file_path', 'maintainability_score']]

    def calculate_coverage_score(self) -> pd.DataFrame:
        """
        Calculate test coverage score.
        
        Returns:
            pd.DataFrame: DataFrame with coverage scores
        """
        coverage = self.static_metrics['test_coverage']
        if coverage.empty:
            return pd.DataFrame()
        
        # Normalize coverage percentage
        coverage['coverage_score'] = self._normalize_metric(
            coverage, 'line_coverage'
        )
        
        return coverage[['file_path', 'coverage_score']]

    def calculate_risk_score(self, weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Calculate overall risk score by combining all metrics.
        
        Args:
            weights (Optional[Dict[str, float]]): Weights for each component score
            
        Returns:
            pd.DataFrame: DataFrame with final risk scores
        """
        # Default weights if not provided
        if weights is None:
            weights = {
                'aging': 0.2,
                'frequency': 0.2,
                'complexity': 0.3,
                'maintainability': 0.2,
                'coverage': 0.1
            }
        
        # Get all component scores
        scores = [
            self.calculate_aging_score(),
            self.calculate_change_frequency_score(),
            self.calculate_complexity_score(),
            self.calculate_maintainability_score(),
            self.calculate_coverage_score()
        ]
        
        # Merge all scores on file_path
        risk_df = pd.DataFrame()
        for score_df in scores:
            if not score_df.empty:
                if risk_df.empty:
                    risk_df = score_df
                else:
                    risk_df = pd.merge(risk_df, score_df, on='file_path', how='outer')
        
        if risk_df.empty:
            return pd.DataFrame()
        
        # Fill NaN values with 0.5 (neutral score)
        risk_df = risk_df.fillna(0.5)
        
        # Calculate weighted risk score, handling missing metrics
        risk_score = 0
        total_weight = 0
        
        if 'aging_score' in risk_df.columns:
            risk_score += weights['aging'] * risk_df['aging_score']
            total_weight += weights['aging']
            
        if 'frequency_score' in risk_df.columns:
            risk_score += weights['frequency'] * risk_df['frequency_score']
            total_weight += weights['frequency']
            
        if 'complexity_score' in risk_df.columns:
            risk_score += weights['complexity'] * risk_df['complexity_score']
            total_weight += weights['complexity']
            
        if 'maintainability_score' in risk_df.columns:
            risk_score += weights['maintainability'] * (1 - risk_df['maintainability_score'])
            total_weight += weights['maintainability']
            
        if 'coverage_score' in risk_df.columns:
            risk_score += weights['coverage'] * (1 - risk_df['coverage_score'])
            total_weight += weights['coverage']
        
        # Normalize by total weight used
        if total_weight > 0:
            risk_df['risk_score'] = risk_score / total_weight
        else:
            risk_df['risk_score'] = 0.5  # Neutral score if no metrics available
        
        # Sort by risk score
        risk_df = risk_df.sort_values('risk_score', ascending=False)
        
        return risk_df 