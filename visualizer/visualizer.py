"""
Visualization & Interaction implementation
"""
from typing import Dict, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


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
        
        # Detailed Metrics
        st.header('Detailed Metrics')
        if not self.risk_scores.empty:
            st.dataframe(self.risk_scores)

    def export_report(self, format: str = 'html'):
        """
        Export the analysis report in the specified format.
        
        Args:
            format (str): Export format ('html', 'csv', or 'json')
        """
        if format == 'html':
            # Create HTML report with all visualizations
            pass  # Implement HTML export
        elif format == 'csv':
            # Export risk scores as CSV
            self.risk_scores.to_csv('technical_debt_report.csv', index=False)
        elif format == 'json':
            # Export all metrics as JSON
            report = {
                'risk_scores': self.risk_scores.to_dict(),
                'git_metrics': {k: v.to_dict() for k, v in self.git_metrics.items()},
                'static_metrics': {k: v.to_dict() for k, v in self.static_metrics.items()}
            }
            import json
            with open('technical_debt_report.json', 'w') as f:
                json.dump(report, f) 