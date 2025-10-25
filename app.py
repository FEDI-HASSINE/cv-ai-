"""
UtopiaHire - AI Career Architect
Main Streamlit Application

Professional CV analysis system with:
- Resume Review & Analysis
- AI-Powered Resume Rewriting
- Regional Job Matching
- Digital Footprint Scanner
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config, STREAMLIT_CONFIG, COLORS

# Page configuration
st.set_page_config(**STREAMLIT_CONFIG)

# Custom CSS
st.markdown(f"""
    <style>
        .main-header {{
            font-size: 3rem;
            font-weight: bold;
            color: {COLORS['primary']};
            text-align: center;
            padding: 1rem 0;
        }}
        .sub-header {{
            font-size: 1.2rem;
            color: {COLORS['secondary']};
            text-align: center;
            padding-bottom: 2rem;
        }}
        .feature-card {{
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid {COLORS['primary']};
            margin: 1rem 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['info']});
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }}
        .stButton>button {{
            background-color: {COLORS['primary']};
            color: white;
            border-radius: 5px;
            padding: 0.5rem 2rem;
            font-weight: bold;
        }}
        .stButton>button:hover {{
            background-color: {COLORS['info']};
        }}
    </style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<div class="main-header">💼 UtopiaHire</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI Career Architect - Empowering Careers in MENA & Sub-Saharan Africa</div>',
        unsafe_allow_html=True
    )
    
    # Introduction
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>📄 Resume Analysis</h3>
            <p>AI-powered resume review with ATS scoring, skill extraction, and improvement suggestions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>✍️ Resume Rewriting</h3>
            <p>Get professional rewriting suggestions to optimize your resume for better opportunities.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🎯 Job Matching</h3>
            <p>Discover regionally relevant job opportunities tailored to your skills and experience.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🚀 Get Started")
    st.markdown("""
    Choose a feature from the sidebar to begin your career enhancement journey:
    
    1. **📄 Resume Reviewer** - Upload your resume for comprehensive analysis
    2. **✍️ Resume Rewriter** - Get AI-powered optimization suggestions
    3. **🎯 Job Matcher** - Find jobs matching your profile
    4. **🌐 Footprint Scanner** - Analyze your online professional presence
    """)
    
    # Statistics
    st.markdown("---")
    st.markdown("### 📊 Platform Capabilities")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>50+</h2>
            <p>Technical Skills Tracked</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>4</h2>
            <p>Regions Covered</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>10+</h2>
            <p>Industries Supported</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h2>3</h2>
            <p>Platforms Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
    # About
    st.markdown("---")
    with st.expander("ℹ️ About UtopiaHire"):
        st.markdown("""
        **UtopiaHire** is an AI-powered career development platform designed specifically for 
        job seekers in MENA and Sub-Saharan Africa regions.
        
        #### Key Features:
        - **Resume Reviewer**: Comprehensive NLP-based analysis with ATS scoring
        - **Resume Rewriter**: AI-powered optimization suggestions
        - **Job Matcher**: Regional job recommendations with skill-based matching
        - **Footprint Scanner**: LinkedIn, GitHub, and StackOverflow profile analysis
        
        #### Technology Stack:
        - Python with Streamlit for the interface
        - NLP for text analysis and skill extraction
        - Machine Learning for job matching algorithms
        - API-ready architecture for future integrations
        
        #### Target Regions:
        - MENA (Middle East & North Africa)
        - Sub-Saharan Africa
        - North Africa
        - Global opportunities
        
        ---
        
        **Version**: 1.0.0  
        **Built for**: IEEE TSYP13 Technical Challenge  
        **Focus**: Regional employment challenges and opportunities
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🌍 Empowering careers across Africa and MENA regions</p>
        <p style="font-size: 0.9rem;">Built with ❤️ using Streamlit & Python</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
