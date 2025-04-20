import streamlit as st
from pathlib import Path
import base64
from PIL import Image
import io
import tempfile
import shutil
from git import Repo

from git_analyzer import GitActivityAnalyzer
from static_analyzer import StaticCodeAnalyzer
from risk_scorer import RiskScorer
from visualizer import Visualizer


def load_logo():
    """Load and display the logo if it exists."""
    logo_path = Path("static/images/logo.png")
    if logo_path.exists():
        image = Image.open(logo_path)
        st.image(image, width=200)
    else:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1>🔍</h1>
        </div>
        """, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="Technical Debt Analyzer",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-size: 1.1em;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Header with logo
    st.markdown('<div class="header">', unsafe_allow_html=True)
    load_logo()
    st.title("Technical Debt Analyzer")
    st.markdown("""
    <div style='text-align: left; color: #666; margin-bottom: 2rem;'>
        Analyze and visualize technical debt in your Python projects
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content in two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="metric-box">
            <h3>🔍 Repository Analysis</h3>
            <p>Enter your repository path to begin analysis</p>
        </div>
        """, unsafe_allow_html=True)

        analysis_mode = st.radio("Select input mode:", ["Local Repository", "Public GitHub URL"], horizontal=True)

        if analysis_mode == "Local Repository":
            repo_path_input = st.text_input(
                "Repository Path:",
                placeholder="/path/to/your/repository",
                key="repo_path"
            )
            if not repo_path_input:
                st.warning("Please enter a repository path")
                return

            repo_path = Path(repo_path_input)
            if not repo_path.exists():
                st.error(f"Repository path does not exist: {repo_path}")
                return

        else:
            github_url = st.text_input(
                "GitHub Repository URL:",
                placeholder="https://github.com/username/repository",
                key="github_url"
            )
            if not github_url:
                st.warning("Please enter a GitHub repository URL")
                return

            # Clone into temp directory
            temp_dir = tempfile.mkdtemp()
            try:
                with st.spinner("Cloning repository..."):
                    Repo.clone_from(github_url, temp_dir)
                    repo_path = Path(temp_dir)
            except Exception as e:
                st.error(f"Error cloning repository: {str(e)}")
                shutil.rmtree(temp_dir)
                return

    
    with col2:
        st.markdown("""
        <div class="metric-box">
            <h3>⚙️ Analysis Options</h3>
            <p>Configure your analysis settings</p>
        </div>
        """, unsafe_allow_html=True)
        
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
        authorship_weight = st.sidebar.slider("Authorship churn weight", 0.0, 1.0, 0.1)
    
    # Normalize weights
    total_weight = aging_weight + frequency_weight + complexity_weight + maintainability_weight + coverage_weight + authorship_weight
    if total_weight > 0:
        aging_weight /= total_weight
        frequency_weight /= total_weight
        complexity_weight /= total_weight
        maintainability_weight /= total_weight
        coverage_weight /= total_weight
        authorship_weight /= total_weight
    
    weights = {
        'aging': aging_weight,
        'frequency': frequency_weight,
        'complexity': complexity_weight,
        'maintainability': maintainability_weight,
        'coverage': coverage_weight,
        'authorship': authorship_weight
    }
    
    # Run analysis button
    if st.button("🚀 Start Analysis", key="analyze_button"):
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

        if analysis_mode == "Public GitHub URL":
            shutil.rmtree(temp_dir)
        
        # Create a container for the export button
        export_container = st.sidebar.container()
        
        if export_container.button("Export Report"):
            try:
                report_data = visualizer.export_report(export_format)
                # Handle both string and bytes data types
                if isinstance(report_data, bytes):
                    data = report_data
                else:
                    data = report_data.encode()
                
                # Set correct MIME type
                mime_type = "text/csv" if export_format == "csv" else "application/json"
                
                # Use Streamlit's native download button
                export_container.download_button(
                    label="Download Report",
                    data=data,
                    file_name=f"technical_debt_report.{export_format}",
                    mime=mime_type
                )
            except Exception as e:
                st.sidebar.error(f"Error exporting report: {str(e)}")


if __name__ == "__main__":
    main()
