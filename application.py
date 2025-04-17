import streamlit as st
from pathlib import Path

from git_analyzer import GitActivityAnalyzer
from static_analyzer import StaticCodeAnalyzer
from risk_scorer import RiskScorer
from visualizer import Visualizer


def main():
    st.set_page_config(
        page_title="Technical Debt Analyzer",
        page_icon="🔍",
        layout="wide"
    )
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    st.title("Technical Debt Analyzer")
    st.write("Analyze technical debt in your Python projects")
    
    # Get repository path
    repo_path = st.text_input(
        "Enter the path to your Git repository:",
        placeholder="/path/to/your/repository"
    )
    
    if not repo_path:
        st.warning("Please enter a repository path")
        return
    
    repo_path = Path(repo_path)
    if not repo_path.exists():
        st.error(f"Repository path does not exist: {repo_path}")
        return
    
    # Analysis options
    st.sidebar.header("Analysis Options")
    
    # Git analysis options
    st.sidebar.subheader("Git Analysis")
    time_window = st.sidebar.selectbox(
        "Change frequency time window",
        options=["7D", "30D", "90D", "180D"],
        index=1
    )
    
    # Static analysis options
    st.sidebar.subheader("Static Analysis")
    analyze_complexity = st.sidebar.checkbox("Analyze complexity", value=True)
    analyze_maintainability = st.sidebar.checkbox("Analyze maintainability", value=True)
    analyze_dead_code = st.sidebar.checkbox("Analyze dead code", value=True)
    analyze_code_smells = st.sidebar.checkbox("Analyze code smells", value=True)
    analyze_coverage = st.sidebar.checkbox("Analyze test coverage", value=True)
    
    # Risk scoring options
    st.sidebar.subheader("Risk Scoring")
    aging_weight = st.sidebar.slider("Aging weight", 0.0, 1.0, 0.2)
    frequency_weight = st.sidebar.slider("Change frequency weight", 0.0, 1.0, 0.2)
    complexity_weight = st.sidebar.slider("Complexity weight", 0.0, 1.0, 0.3)
    maintainability_weight = st.sidebar.slider("Maintainability weight", 0.0, 1.0, 0.2)
    coverage_weight = st.sidebar.slider("Coverage weight", 0.0, 1.0, 0.1)
    
    # Normalize weights
    total_weight = aging_weight + frequency_weight + complexity_weight + maintainability_weight + coverage_weight
    if total_weight > 0:
        aging_weight /= total_weight
        frequency_weight /= total_weight
        complexity_weight /= total_weight
        maintainability_weight /= total_weight
        coverage_weight /= total_weight
    
    weights = {
        'aging': aging_weight,
        'frequency': frequency_weight,
        'complexity': complexity_weight,
        'maintainability': maintainability_weight,
        'coverage': coverage_weight
    }
    
    # Run analysis
    if st.button("Analyze"):
        with st.spinner("Analyzing repository..."):
            try:
                # Git analysis
                git_analyzer = GitActivityAnalyzer(str(repo_path))
                git_metrics = git_analyzer.analyze()
                
                # Static analysis
                static_analyzer = StaticCodeAnalyzer(str(repo_path))
                static_metrics = {}
                
                # Run static analyses based on selected options
                if analyze_complexity:
                    static_metrics['complexity'] = static_analyzer.analyze_complexity()
                if analyze_maintainability:
                    static_metrics['maintainability'] = static_analyzer.analyze_maintainability()
                if analyze_dead_code:
                    static_metrics['dead_code'] = static_analyzer.analyze_dead_code()
                if analyze_code_smells:
                    static_metrics['code_smells'] = static_analyzer.analyze_code_smells()
                if analyze_coverage:
                    static_metrics['test_coverage'] = static_analyzer.analyze_test_coverage()
                
                # Risk scoring
                risk_scorer = RiskScorer(git_metrics, static_metrics)
                risk_scores = risk_scorer.calculate_risk_score(weights)
                
                # Store results in session state
                st.session_state.analysis_results = {
                    'risk_scores': risk_scores,
                    'git_metrics': git_metrics,
                    'static_metrics': static_metrics
                }
                
                st.success("Analysis completed successfully!")
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.session_state.analysis_results = None
    
    # Show dashboard if analysis results exist
    if st.session_state.analysis_results:
        visualizer = Visualizer(
            st.session_state.analysis_results['risk_scores'],
            st.session_state.analysis_results['git_metrics'],
            st.session_state.analysis_results['static_metrics']
        )
        visualizer.show_dashboard()
        
        # Export options
        st.sidebar.subheader("Export")
        export_format = st.sidebar.selectbox(
            "Export format",
            options=["csv", "json"],
            index=0
        )
        if st.sidebar.button("Export Report"):
            try:
                visualizer.export_report(export_format)
                st.sidebar.success(f"Report exported as {export_format.upper()}")
            except Exception as e:
                st.sidebar.error(f"Error exporting report: {str(e)}")


if __name__ == "__main__":
    main()
