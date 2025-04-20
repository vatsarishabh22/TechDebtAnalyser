"""
Visualization & Interaction implementation
"""
from typing import Dict, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import json


class Visualizer:
    def __init__(self, risk_scores: pd.DataFrame, 
                 git_metrics: Dict[str, pd.DataFrame],
                 static_metrics: Dict[str, pd.DataFrame]):
        """
        Initialize the Visualizer.
        
        Args:
            risk_scores (pd.DataFrame): Risk scores from RiskScorer
            git_metrics (Dict[str, pd.DataFrame]): Metrics from Git Activity Analyzer
            static_metrics (Dict[str, pd.DataFrame]): Metrics from Static Code Analyzer
        """
        self.risk_scores = risk_scores
        self.git_metrics = git_metrics
        self.static_metrics = static_metrics

    def show_risk_heatmap(self):
        """Display a heatmap of risk scores by file."""
        if self.risk_scores.empty:
            st.warning("No risk scores available to display.")
            return
        
        fig = px.treemap(
            self.risk_scores,
            path=['file_path'],
            values='risk_score',
            color='risk_score',
            color_continuous_scale='RdYlGn_r',  # Red-Yellow-Green (reversed)
            title='Technical Debt Risk Heatmap'
        )
        st.plotly_chart(fig)

    def show_complexity_distribution(self):
        """Display the distribution of code complexity."""
        complexity = self.static_metrics['complexity']
        if complexity.empty:
            st.warning("No complexity metrics available to display.")
            return
        
        fig = px.histogram(
            complexity,
            x='complexity',
            title='Code Complexity Distribution',
            labels={'complexity': 'Cyclomatic Complexity'}
        )
        st.plotly_chart(fig)

    def show_maintainability_trend(self):
        """Display maintainability index trend over time."""
        maintainability = self.static_metrics['maintainability']
        if maintainability.empty:
            st.warning("No maintainability metrics available to display.")
            return
        
        fig = px.bar(
            maintainability,
            x='file_path',
            y='maintainability_index',
            title='Maintainability Index by File',
            labels={
                'file_path': 'File',
                'maintainability_index': 'Maintainability Index'
            }
        )
        st.plotly_chart(fig)

    def show_coverage_report(self):
        """Display test coverage metrics."""
        coverage = self.static_metrics['test_coverage']
        if coverage.empty:
            st.warning("No coverage metrics available to display.")
            return
        
        fig = go.Figure(data=[
            go.Bar(
                name='Line Coverage',
                x=coverage['file_path'],
                y=coverage['line_coverage']
            ),
            go.Bar(
                name='Missing Lines',
                x=coverage['file_path'],
                y=coverage['missing_lines']
            )
        ])
        fig.update_layout(
            title='Test Coverage Report',
            barmode='group',
            xaxis_title='File',
            yaxis_title='Count'
        )
        st.plotly_chart(fig)

    def show_change_frequency(self):
        """Display change frequency over time."""
        change_freq = self.git_metrics['change_frequency']
        if change_freq.empty:
            st.warning("No change frequency metrics available to display.")
            return
        
        fig = px.line(
            change_freq,
            x='window_end',
            y='change_count',
            color='file_path',
            title='Change Frequency Over Time',
            labels={
                'window_end': 'Time',
                'change_count': 'Number of Changes',
                'file_path': 'File'
            }
        )
        st.plotly_chart(fig)

    def show_file_aging(self):
        """Display file aging metrics."""
        last_modified = self.git_metrics['last_modified']
        if last_modified.empty:
            st.warning("No file aging metrics available to display.")
            return
        
        # Convert to datetime if not already
        last_modified['last_modified'] = pd.to_datetime(last_modified['last_modified'], utc=True)
        
        # Calculate age in days
        now = pd.Timestamp.now(tz='UTC')
        last_modified['age_days'] = (now - last_modified['last_modified']).dt.total_seconds() / (24 * 3600)
        
        # Create two columns for different views
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart of file ages
            fig = px.bar(
                last_modified,
                x='file_path',
                y='age_days',
                title='File Age in Days',
                labels={
                    'file_path': 'File',
                    'age_days': 'Age (days)'
                }
            )
            st.plotly_chart(fig)
        
        with col2:
            # Heatmap of modification dates
            last_modified['month'] = last_modified['last_modified'].dt.strftime('%Y-%m')
            monthly_counts = last_modified.groupby('month').size().reset_index(name='count')
            
            fig = px.bar(
                monthly_counts,
                x='month',
                y='count',
                title='File Modifications by Month',
                labels={
                    'month': 'Month',
                    'count': 'Number of Files Modified'
                }
            )
            st.plotly_chart(fig)

    def show_authorship_churn(self):
        """Display authorship churn metrics."""
        authorship = self.git_metrics['authorship_churn']
        if authorship.empty:
            st.warning("No authorship churn metrics available to display.")
            return
        
        # Create two columns for the metrics
        col1, col2 = st.columns(2)
        
        with col1:
            # Number of authors per file
            fig = px.bar(
                authorship,
                x='file_path',
                y='num_authors',
                title='Number of Authors per File',
                labels={
                    'file_path': 'File',
                    'num_authors': 'Number of Authors'
                }
            )
            st.plotly_chart(fig)
        
        with col2:
            # Top two authors contribution
            fig = px.bar(
                authorship,
                x='file_path',
                y='top_two_authors_contribution',
                title='Top Two Authors Contribution',
                labels={
                    'file_path': 'File',
                    'top_two_authors_contribution': 'Contribution Percentage'
                }
            )
            st.plotly_chart(fig)

    def show_dashboard(self):
        """Display the complete dashboard with all visualizations."""
        st.title('Technical Debt Analysis Dashboard')
        
        # Risk Overview
        st.header('Risk Overview')
        self.show_risk_heatmap()
        
        # Code Quality Metrics
        st.header('Code Quality Metrics')
        col1, col2 = st.columns(2)
        with col1:
            self.show_complexity_distribution()
        with col2:
            self.show_maintainability_trend()
        
        # Test Coverage
        st.header('Test Coverage')
        self.show_coverage_report()
        
        # Change History
        st.header('Change History')
        self.show_change_frequency()
        
        # File Aging
        st.header('File Aging')
        self.show_file_aging()
        
        # Authorship Analysis
        st.header('Authorship Analysis')
        self.show_authorship_churn()
        
        # Detailed Metrics
        st.header('Detailed Metrics')
        if not self.risk_scores.empty:
            st.dataframe(self.risk_scores)

    def export_report(self, format: str = 'html'):
        """
        Export the analysis report in the specified format.
        
        Args:
            format (str): Export format ('html', 'csv', or 'json')
            
        Returns:
            bytes: The report data in the specified format
        """
        if format == 'csv':
            # Export risk scores as CSV
            return self.risk_scores.to_csv(index=False).encode()
        elif format == 'json':
            # Export all metrics as JSON
            report = {
                'risk_scores': self.risk_scores.to_dict(),
                'git_metrics': {k: v.to_dict() for k, v in self.git_metrics.items()},
                'static_metrics': {k: v.to_dict() for k, v in self.static_metrics.items()}
            }
            return json.dumps(report).encode()
        else:
            raise ValueError(f"Unsupported export format: {format}") 