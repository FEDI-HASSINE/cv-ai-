"""
Resume Rewriter Page
AI-powered resume optimization and rewriting suggestions
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config, COLORS
from src.utils.file_parser import parse_file
from src.utils.helpers import get_file_size_mb, validate_file_extension
from src.core.resume_analyzer import ResumeAnalyzer
from src.core.resume_rewriter import ResumeRewriter

st.set_page_config(page_title="Resume Rewriter", page_icon="✍️", layout="wide")

st.markdown(f"""
    <style>
        .improvement-card {{
            background-color: #f8f9fa;
            border-left: 4px solid {COLORS['warning']};
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 5px;
        }}
        .priority-high {{
            background-color: #fff3cd;
            border-left: 4px solid {COLORS['danger']};
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 5px;
        }}
        .priority-medium {{
            background-color: #d1ecf1;
            border-left: 4px solid {COLORS['info']};
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 5px;
        }}
        .example-box {{
            background-color: #e7f3ff;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
        }}
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("✍️ Resume Rewriter")
    st.markdown("Get AI-powered suggestions to optimize your resume")
    
    # Initialize
    if 'rewriter' not in st.session_state:
        st.session_state.rewriter = ResumeRewriter()
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = ResumeAnalyzer()
    
    config = Config()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ✨ Rewriting Features")
        st.markdown("""
        - **Weak Phrase Detection**
        - **Action Verb Suggestions**
        - **Quantification Opportunities**
        - **Formatting Improvements**
        - **Content Enhancement**
        - **Optimized Examples**
        """)
        
        st.markdown("---")
        st.markdown("### 💡 Best Practices")
        st.info("""
        - Use strong action verbs
        - Quantify achievements
        - Focus on results
        - Keep it concise
        - Tailor to job descriptions
        """)
    
    # Main content
    st.markdown("---")
    
    # Upload
    uploaded_file = st.file_uploader(
        "Upload your resume for rewriting suggestions",
        type=['pdf', 'docx', 'doc', 'txt'],
        help="We'll analyze your content and provide optimization suggestions"
    )
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_size = get_file_size_mb(file_bytes)
        
        if file_size > config.MAX_FILE_SIZE_MB:
            st.error(f"File too large: {file_size:.2f} MB (max: {config.MAX_FILE_SIZE_MB} MB)")
            return
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Parse
        with st.spinner("📖 Parsing resume..."):
            parsed = parse_file(uploaded_file.name, file_bytes)
        
        if parsed["status"] == "error":
            st.error(f"Error: {parsed['error']}")
            return
        
        # Options
        col1, col2 = st.columns(2)
        
        with col1:
            include_analysis = st.checkbox(
                "Include resume analysis",
                value=True,
                help="Analyze resume first for better suggestions"
            )
        
        with col2:
            show_examples = st.checkbox(
                "Show optimized examples",
                value=True,
                help="Display example sections"
            )
        
        # Analyze & Rewrite button
        if st.button("✨ Generate Rewriting Suggestions", type="primary"):
            with st.spinner("🤖 Analyzing and generating suggestions..."):
                # Optional analysis
                analysis = None
                if include_analysis:
                    analysis = st.session_state.analyzer.analyze(parsed["text"])
                    st.session_state.analysis = analysis
                
                # Rewrite suggestions
                rewrite = st.session_state.rewriter.rewrite(parsed["text"], analysis)
                st.session_state.rewrite = rewrite
        
        # Display results
        if 'rewrite' in st.session_state:
            rewrite = st.session_state.rewrite
            
            st.markdown("---")
            st.markdown("## ✨ Optimization Suggestions")
            
            # Improvement potential
            st.markdown(f"""
            <div class="improvement-card">
                <h3>📈 Improvement Potential: {rewrite['improvement_score']}/100</h3>
                <p>Your resume has significant potential for optimization!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "🔄 Weak Phrases",
                "💪 Action Verbs",
                "📊 Quantification",
                "🎨 Formatting",
                "📝 Examples"
            ])
            
            with tab1:
                st.markdown("### 🔄 Weak Phrases to Improve")
                
                if rewrite['weak_phrases']:
                    st.info(f"Found {len(rewrite['weak_phrases'])} weak phrases that can be strengthened")
                    
                    for idx, wp in enumerate(rewrite['weak_phrases'][:10], 1):
                        st.markdown(f"""
                        <div class="improvement-card">
                            <strong>Example {idx}</strong><br>
                            ❌ <span style="color: #dc3545;">{wp['weak_phrase']}</span><br>
                            ✅ <span style="color: #28a745;">{wp['strong_alternative']}</span><br>
                            <small><em>Context: "{wp['context'][:100]}..."</em></small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ No weak phrases detected! Your language is strong.")
            
            with tab2:
                st.markdown("### 💪 Action Verb Suggestions")
                
                if rewrite['action_verbs']:
                    st.info("Diversify your resume with these powerful action verbs")
                    
                    for category, verbs in rewrite['action_verbs'].items():
                        with st.expander(f"📌 {category} Verbs"):
                            st.markdown(", ".join(verbs))
                            st.caption(f"Use these verbs to describe {category.lower()} activities")
                else:
                    st.success("✅ Good variety of action verbs!")
            
            with tab3:
                st.markdown("### 📊 Quantification Opportunities")
                
                if rewrite['quantification']:
                    st.warning(f"Found {len(rewrite['quantification'])} opportunities to add metrics")
                    
                    for idx, opp in enumerate(rewrite['quantification'][:8], 1):
                        st.markdown(f"""
                        <div class="improvement-card">
                            <strong>Opportunity {idx}</strong><br>
                            <em>"{opp['context'][:100]}..."</em><br>
                            💡 <strong>{opp['suggestion']}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    **💡 Tips for Quantification:**
                    - Add percentages (improved by X%)
                    - Include numbers (managed team of X)
                    - Specify amounts (saved $X)
                    - Show scale (X users, X projects)
                    """)
                else:
                    st.success("✅ Good use of quantifiable metrics!")
            
            with tab4:
                st.markdown("### 🎨 Formatting Improvements")
                
                if rewrite['formatting']:
                    for fmt in rewrite['formatting']:
                        st.markdown(f"• {fmt}")
                else:
                    st.success("✅ Formatting looks good!")
                
                st.markdown("---")
                st.markdown("#### 📋 General Formatting Best Practices")
                st.markdown("""
                - Use consistent bullet points (•)
                - Keep dates in same format (MM/YYYY)
                - Use clear section headers
                - Maintain proper spacing
                - Ensure readability with appropriate line breaks
                - Use bold for emphasis on key achievements
                """)
            
            with tab5:
                if show_examples and rewrite['optimized_sections']:
                    st.markdown("### 📝 Optimized Section Examples")
                    
                    sections = rewrite['optimized_sections']
                    
                    # Professional Summary
                    if 'Professional Summary' in sections:
                        st.markdown("#### 💼 Professional Summary Example")
                        st.markdown(f"""
                        <div class="example-box">
                        {sections['Professional Summary']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Experience bullets
                    if 'Experience Bullet Points' in sections:
                        st.markdown("#### 📌 Experience Bullet Point Examples")
                        for bullet in sections['Experience Bullet Points']:
                            st.markdown(f"""
                            <div class="example-box">
                            {bullet}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Skills section
                    if 'Skills Section' in sections:
                        st.markdown("#### 🔧 Skills Section Example")
                        st.markdown(f"""
                        <div class="example-box">
                        <pre>{sections['Skills Section']}</pre>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Recommendations
            st.markdown("---")
            st.markdown("### 🎯 Priority Recommendations")
            
            for rec in rewrite['recommendations']:
                priority = rec['priority']
                css_class = f"priority-{priority.lower()}"
                
                st.markdown(f"""
                <div class="{css_class}">
                    <strong>🔥 {priority} Priority - {rec['category']}</strong><br>
                    {rec['recommendation']}<br>
                    <small><em>Impact: {rec['impact']}</em></small>
                </div>
                """, unsafe_allow_html=True)
            
            # Action items
            st.markdown("---")
            st.markdown("### ✅ Next Steps")
            st.markdown("""
            1. Review and implement high-priority suggestions
            2. Replace weak phrases with stronger alternatives
            3. Add quantifiable metrics to your achievements
            4. Diversify your action verbs
            5. Ensure consistent formatting throughout
            6. Tailor your resume for specific job applications
            """)
            
            # Download report
            st.markdown("---")
            st.markdown("### 📥 Download Rewriting Report")
            
            # Generate comprehensive report
            report_text = f"""
UtopiaHire - Resume Rewriting Suggestions Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================

IMPROVEMENT POTENTIAL: {rewrite['improvement_score']}/100

WEAK PHRASES TO REPLACE ({len(rewrite['weak_phrases'])})
========================
"""
            
            for idx, wp in enumerate(rewrite['weak_phrases'], 1):
                report_text += f"""
{idx}. Weak: "{wp['weak_phrase']}"
   Strong: "{wp['strong_alternative']}"
   Context: "{wp['context'][:80]}..."
"""
            
            report_text += f"""

ACTION VERBS BY CATEGORY
========================
"""
            for category, verbs in rewrite['action_verbs'].items():
                report_text += f"\n{category}:\n  {', '.join(verbs)}\n"
            
            report_text += f"""

QUANTIFICATION OPPORTUNITIES ({len(rewrite['quantification'])})
============================
"""
            for idx, opp in enumerate(rewrite['quantification'], 1):
                report_text += f"""
{idx}. Context: "{opp['context'][:80]}..."
   Suggestion: {opp['suggestion']}
"""
            
            report_text += f"""

FORMATTING IMPROVEMENTS
=======================
"""
            for fmt in rewrite['formatting']:
                report_text += f"• {fmt}\n"
            
            report_text += f"""

CONTENT ENHANCEMENTS
====================
"""
            for enh in rewrite['content_enhancements']:
                report_text += f"• {enh}\n"
            
            report_text += f"""

PRIORITY RECOMMENDATIONS
========================
"""
            for rec in rewrite['recommendations']:
                report_text += f"""
[{rec['priority']} Priority] {rec['category']}
  Recommendation: {rec['recommendation']}
  Impact: {rec['impact']}
"""
            
            report_text += f"""

OPTIMIZED SECTION EXAMPLES
==========================
"""
            for section_name, content in rewrite['optimized_sections'].items():
                report_text += f"\n{section_name}:\n"
                if isinstance(content, list):
                    for item in content:
                        report_text += f"  {item}\n"
                else:
                    report_text += f"  {content}\n"
            
            report_text += """

================================================
Report generated by UtopiaHire - AI Career Architect
Next Steps: Implement suggestions and re-analyze your resume
"""
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Text report download
                st.download_button(
                    label="📄 Download Text Report",
                    data=report_text,
                    file_name=f"resume_rewriting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    help="Download complete rewriting suggestions as text file"
                )
            
            with col2:
                # JSON report download
                json_report = json.dumps(rewrite, indent=2, default=str)
                st.download_button(
                    label="📊 Download JSON Report",
                    data=json_report,
                    file_name=f"resume_rewriting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    help="Download structured data for programmatic use"
                )

if __name__ == "__main__":
    main()
