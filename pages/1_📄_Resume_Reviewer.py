"""
Resume Reviewer Page
Comprehensive resume analysis with ATS scoring and insights
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config, COLORS
from src.utils.file_parser import parse_file
from src.utils.helpers import get_file_size_mb, validate_file_extension
from src.core.resume_analyzer import ResumeAnalyzer

st.set_page_config(page_title="Resume Reviewer", page_icon="📄", layout="wide")

# Custom CSS
st.markdown(f"""
    <style>
        .score-card {{
            background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['info']});
            color: white;
            padding: 2rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
        }}
        .score-number {{
            font-size: 3rem;
            font-weight: bold;
        }}
        .skill-tag {{
            background-color: {COLORS['info']};
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            margin: 0.2rem;
            display: inline-block;
            font-size: 0.9rem;
        }}
        .strength-item {{
            color: {COLORS['success']};
            padding: 0.5rem;
        }}
        .weakness-item {{
            color: {COLORS['danger']};
            padding: 0.5rem;
        }}
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("📄 Resume Reviewer")
    st.markdown("Upload your resume for comprehensive AI-powered analysis")
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = ResumeAnalyzer()
    
    config = Config()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📋 Upload Settings")
        st.info(f"""
        **Supported formats:**  
        {', '.join(config.ALLOWED_EXTENSIONS)}
        
        **Max file size:**  
        {config.MAX_FILE_SIZE_MB} MB
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ What We Analyze")
        st.markdown("""
        - **ATS Compatibility Score**
        - **Contact Information**
        - **Section Structure**
        - **Technical Skills**
        - **Soft Skills**
        - **Experience Level**
        - **Education Background**
        - **Improvement Suggestions**
        """)
    
    # Main content
    st.markdown("---")
    
    # AI Configuration (in sidebar)
    with st.sidebar:
        st.markdown("---")
        st.subheader("🤖 AI Configuration")
        st.markdown("*Optional: For better extraction*")
        
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key for GPT-powered extraction (optional)",
            placeholder="sk-..."
        )
        
        if openai_key:
            st.success("✅ OpenAI key provided - Using GPT for extraction")
            # Reinitialize analyzer with API key
            st.session_state.analyzer = ResumeAnalyzer(openai_api_key=openai_key)
        else:
            st.info("💡 Using free Hugging Face models (may be slower first time)")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=['pdf', 'docx', 'doc', 'txt'],
        help="Upload your resume in PDF, DOCX, or TXT format"
    )
    
    if uploaded_file is not None:
        # Validate file
        file_bytes = uploaded_file.read()
        file_size = get_file_size_mb(file_bytes)
        
        if file_size > config.MAX_FILE_SIZE_MB:
            st.error(f"File size ({file_size:.2f} MB) exceeds maximum allowed size ({config.MAX_FILE_SIZE_MB} MB)")
            return
        
        if not validate_file_extension(uploaded_file.name, config.ALLOWED_EXTENSIONS):
            st.error(f"File format not supported. Please upload: {', '.join(config.ALLOWED_EXTENSIONS)}")
            return
        
        # Show file info
        st.success(f"✅ File uploaded: {uploaded_file.name} ({file_size:.2f} MB)")
        
        # Parse file
        with st.spinner("📖 Parsing resume..."):
            parsed = parse_file(uploaded_file.name, file_bytes)
        
        if parsed["status"] == "error":
            st.error(f"Error parsing file: {parsed['error']}")
            return
        
        st.info(f"📊 Extracted {parsed['word_count']} words, {parsed['char_count']} characters")
        
        # Show extracted text preview for debugging
        with st.expander("🔍 View Extracted Text (for debugging)", expanded=False):
            st.text_area("Raw Text", parsed["text"][:2000] + "..." if len(parsed["text"]) > 2000 else parsed["text"], height=200)
        
        # Analyze button
        if st.button("🔍 Analyze Resume", type="primary"):
            with st.spinner("🤖 Analyzing your resume... This may take a moment."):
                analysis = st.session_state.analyzer.analyze(parsed["text"])
                st.session_state.analysis = analysis
        
        # Display results if analysis exists
        if 'analysis' in st.session_state:
            analysis = st.session_state.analysis
            
            st.markdown("---")
            st.markdown("## 📊 Analysis Results")
            
            # Show AI usage indicator
            if analysis.get('ai_extracted'):
                st.success("🤖 **AI-Powered Extraction Used** - High accuracy data extraction!")
            else:
                st.info("📝 **Regex-Based Extraction** - Add OpenAI key in sidebar for better results")
            
            # Overall Score
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="score-card">
                    <div>Overall Score</div>
                    <div class="score-number">{analysis['overall_score']}/100</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="score-card">
                    <div>ATS Score</div>
                    <div class="score-number">{analysis['ats_score']}/100</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="score-card">
                    <div>Experience</div>
                    <div class="score-number">{analysis['experience_years']} yrs</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Tabs for detailed analysis
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "� Complete Analysis",
                "💪 Strengths & Weaknesses",
                "💼 Skills",
                "🎯 ATS Details",
                "💡 Suggestions"
            ])
            
            with tab1:
                st.markdown("### 📊 Complete Resume Analysis")
                
                # Score Summary Cards
                st.markdown("#### 🎯 Overall Performance")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    score_color = "🟢" if analysis['overall_score'] >= 70 else "🟡" if analysis['overall_score'] >= 50 else "🔴"
                    st.metric("Overall Score", f"{analysis['overall_score']}/100", delta=score_color)
                
                with col2:
                    ats_color = "🟢" if analysis['ats_score'] >= 70 else "🟡" if analysis['ats_score'] >= 50 else "🔴"
                    st.metric("ATS Compatibility", f"{analysis['ats_score']}/100", delta=ats_color)
                
                with col3:
                    skills_total = len(analysis['technical_skills']) + len(analysis['soft_skills'])
                    st.metric("Total Skills", skills_total)
                
                with col4:
                    st.metric("Experience", f"{analysis['experience_years']} years")
                
                st.markdown("---")
                
                # Detailed Breakdown
                st.markdown("#### 📇 Contact & Professional Info")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    contact = analysis['contact_info']
                    st.markdown("**Contact Details**")
                    
                    if contact.get('email'):
                        st.success(f"✅ Email: {contact['email']}")
                    else:
                        st.error("❌ Email: Not found - CRITICAL!")
                    
                    if contact.get('phone'):
                        st.success(f"✅ Phone: {contact['phone']}")
                    else:
                        st.warning("⚠️ Phone: Not found")
                    
                with col2:
                    st.markdown("**Online Presence**")
                    
                    urls_found = contact.get('urls', [])
                    if urls_found:
                        st.success(f"✅ URLs: {len(urls_found)} found")
                        for url in urls_found[:3]:
                            st.caption(f"• {url}")
                    else:
                        st.warning("⚠️ No LinkedIn/GitHub/Portfolio found")
                
                with col3:
                    st.markdown("**Education & Experience**")
                    st.info(f"📚 Education: {analysis['education_level']}")
                    st.info(f"💼 Experience: {analysis['experience_years']} years")
                    st.info(f"📝 Word Count: {analysis['word_count']} words")
                
                st.markdown("---")
                
                # Document Structure Analysis
                st.markdown("#### 📑 Document Structure")
                
                sections = analysis['sections_found']
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if sections:
                        st.markdown("**Sections Detected:**")
                        sections_html = " ".join([
                            f'<span class="skill-tag">{section}</span>'
                            for section in sections
                        ])
                        st.markdown(sections_html, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ No clear sections detected - Resume may be poorly structured")
                
                with col2:
                    # Section completeness
                    required_sections = ['Experience', 'Education', 'Skills']
                    found_required = sum(1 for req in required_sections if any(req.lower() in s.lower() for s in sections))
                    completeness = (found_required / len(required_sections)) * 100
                    
                    st.metric("Structure Score", f"{int(completeness)}%")
                    if completeness >= 80:
                        st.success("✅ Well structured")
                    elif completeness >= 50:
                        st.warning("⚠️ Missing key sections")
                    else:
                        st.error("❌ Poorly structured")
                
                st.markdown("---")
                
                # Skills Overview
                st.markdown("#### 💡 Skills Overview")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    tech_count = len(analysis['technical_skills'])
                    st.markdown(f"**🔧 Technical Skills: {tech_count}**")
                    
                    if tech_count >= 10:
                        st.success(f"✅ Excellent! {tech_count} technical skills found")
                    elif tech_count >= 5:
                        st.info(f"👍 Good! {tech_count} technical skills found")
                    elif tech_count > 0:
                        st.warning(f"⚠️ Limited: Only {tech_count} technical skills")
                    else:
                        st.error("❌ No technical skills detected!")
                    
                    # Show top skills
                    if tech_count > 0:
                        st.caption("**Top Skills:**")
                        for skill in analysis['technical_skills'][:5]:
                            st.caption(f"• {skill}")
                
                with col2:
                    soft_count = len(analysis['soft_skills'])
                    st.markdown(f"**🤝 Soft Skills: {soft_count}**")
                    
                    if soft_count >= 5:
                        st.success(f"✅ Great! {soft_count} soft skills found")
                    elif soft_count >= 3:
                        st.info(f"👍 Good! {soft_count} soft skills found")
                    elif soft_count > 0:
                        st.warning(f"⚠️ Limited: Only {soft_count} soft skills")
                    else:
                        st.error("❌ No soft skills detected!")
                    
                    # Show soft skills
                    if soft_count > 0:
                        st.caption("**Key Soft Skills:**")
                        for skill in analysis['soft_skills']:
                            st.caption(f"• {skill}")
                
                st.markdown("---")
                
                # ATS Compatibility Summary
                st.markdown("#### 🎯 ATS Compatibility Summary")
                
                ats = analysis['ats_analysis']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Keywords Found", f"{len(ats['found_keywords'])}/{ats['total_keywords']}")
                    keyword_pct = (len(ats['found_keywords']) / ats['total_keywords'] * 100) if ats['total_keywords'] > 0 else 0
                    st.progress(keyword_pct / 100)
                
                with col2:
                    st.metric("Missing Keywords", len(ats['missing_keywords']))
                    if len(ats['missing_keywords']) == 0:
                        st.success("✅ Perfect!")
                    elif len(ats['missing_keywords']) <= 5:
                        st.info("👍 Good")
                    else:
                        st.warning("⚠️ Needs improvement")
                
                with col3:
                    st.metric("ATS Pass Likelihood", f"{ats['percentage']}%")
                    if ats['percentage'] >= 80:
                        st.success("✅ High chance")
                    elif ats['percentage'] >= 60:
                        st.info("👍 Moderate chance")
                    else:
                        st.error("❌ Low chance")
                
                # Quick insights
                st.markdown("---")
                st.markdown("#### 💡 Quick Insights")
                
                insights = []
                
                # Generate insights based on analysis
                if analysis['overall_score'] >= 80:
                    insights.append("🌟 **Excellent Resume!** Your resume is well-optimized.")
                elif analysis['overall_score'] >= 60:
                    insights.append("👍 **Good Resume** with room for improvement.")
                else:
                    insights.append("⚠️ **Needs Improvement** - Several areas require attention.")
                
                if tech_count >= 10:
                    insights.append("✅ **Strong Technical Profile** - Diverse skill set detected.")
                elif tech_count < 5:
                    insights.append("⚠️ **Limited Technical Skills** - Add more relevant technologies.")
                
                if ats['percentage'] >= 70:
                    insights.append("✅ **ATS-Friendly** - Good keyword optimization.")
                else:
                    insights.append("❌ **ATS Risk** - May be filtered out by Applicant Tracking Systems.")
                
                if not contact.get('email'):
                    insights.append("🚨 **CRITICAL: Missing Email** - Add contact information immediately!")
                
                if analysis['experience_years'] == 0:
                    insights.append("⚠️ **No Experience Detected** - Ensure dates are clearly formatted (YYYY-YYYY).")
                
                for insight in insights:
                    st.markdown(f"""
                    <div style="padding: 10px; margin: 5px 0; background-color: #f0f2f6; border-radius: 5px; border-left: 4px solid #1f77b4;">
                        {insight}
                    </div>
                    """, unsafe_allow_html=True)
            
            with tab2:
                st.markdown("### Strengths & Weaknesses")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### ✅ Strengths")
                    if analysis['strengths']:
                        for strength in analysis['strengths']:
                            st.markdown(f'<div class="strength-item">✓ {strength}</div>', unsafe_allow_html=True)
                    else:
                        st.info("Keep building your resume!")
                
                with col2:
                    st.markdown("#### ⚠️ Areas for Improvement")
                    if analysis['weaknesses']:
                        for weakness in analysis['weaknesses']:
                            st.markdown(f'<div class="weakness-item">• {weakness}</div>', unsafe_allow_html=True)
                    else:
                        st.success("Great! No major weaknesses detected!")
            
            with tab3:
                st.markdown("### Skills Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"#### 🔧 Technical Skills ({len(analysis['technical_skills'])})")
                    if analysis['technical_skills']:
                        skills_html = " ".join([
                            f'<span class="skill-tag">{skill}</span>'
                            for skill in analysis['technical_skills']
                        ])
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.warning("No technical skills detected")
                
                with col2:
                    st.markdown(f"#### 🤝 Soft Skills ({len(analysis['soft_skills'])})")
                    if analysis['soft_skills']:
                        skills_html = " ".join([
                            f'<span class="skill-tag">{skill}</span>'
                            for skill in analysis['soft_skills']
                        ])
                        st.markdown(skills_html, unsafe_allow_html=True)
                    else:
                        st.warning("No soft skills detected")
            
            with tab4:
                st.markdown("### ATS Analysis Details")
                
                ats = analysis['ats_analysis']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Keywords Found", f"{ats['found_keywords'].__len__()}/{ats['total_keywords']}")
                    if ats['found_keywords']:
                        st.markdown("**Found Keywords:**")
                        st.write(", ".join(ats['found_keywords']))
                
                with col2:
                    if ats['missing_keywords']:
                        st.markdown("**Missing Important Keywords:**")
                        st.write(", ".join(ats['missing_keywords'][:5]))
                        st.caption("Consider adding these to improve ATS score")
            
            with tab5:
                st.markdown("### 💡 Improvement Suggestions")
                
                if analysis['suggestions']:
                    for idx, suggestion in enumerate(analysis['suggestions'], 1):
                        st.markdown(f"**{idx}.** {suggestion}")
                else:
                    st.success("Your resume looks great!")
            
            # Download report button
            st.markdown("---")
            
            # Generate report
            report_text = f"""
UtopiaHire - Resume Analysis Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
=====================================

OVERALL ASSESSMENT
------------------
Overall Score: {analysis['overall_score']}/100
ATS Score: {analysis['ats_score']}/100
Experience: {analysis['experience_years']} years
Education Level: {analysis['education_level']}
Word Count: {analysis['word_count']}

CONTACT INFORMATION
-------------------
Email: {analysis['contact_info']['email'] or 'Not found'}
Phone: {analysis['contact_info']['phone'] or 'Not found'}
URLs Found: {len(analysis['contact_info']['urls'])}

SECTIONS DETECTED
-----------------
{', '.join(analysis['sections_found']) if analysis['sections_found'] else 'No clear sections detected'}

TECHNICAL SKILLS ({len(analysis['technical_skills'])})
------------------
{', '.join(analysis['technical_skills']) if analysis['technical_skills'] else 'None detected'}

SOFT SKILLS ({len(analysis['soft_skills'])})
------------
{', '.join(analysis['soft_skills']) if analysis['soft_skills'] else 'None detected'}

STRENGTHS
---------
{chr(10).join(f"✓ {s}" for s in analysis['strengths']) if analysis['strengths'] else 'Keep building!'}

AREAS FOR IMPROVEMENT
---------------------
{chr(10).join(f"• {w}" for w in analysis['weaknesses']) if analysis['weaknesses'] else 'Great job!'}

ATS ANALYSIS
------------
Keywords Found: {len(analysis['ats_analysis']['found_keywords'])}/{analysis['ats_analysis']['total_keywords']}
Found: {', '.join(analysis['ats_analysis']['found_keywords'][:10])}
Missing: {', '.join(analysis['ats_analysis']['missing_keywords'][:10])}

IMPROVEMENT SUGGESTIONS
-----------------------
{chr(10).join(f"{i}. {s}" for i, s in enumerate(analysis['suggestions'], 1))}

=====================================
Report generated by UtopiaHire - AI Career Architect
For more information, visit your dashboard
"""
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Text report download
                st.download_button(
                    label="📄 Download Text Report",
                    data=report_text,
                    file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            with col2:
                # JSON report download
                json_report = json.dumps(analysis, indent=2, default=str)
                st.download_button(
                    label="📊 Download JSON Report",
                    data=json_report,
                    file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

if __name__ == "__main__":
    main()
