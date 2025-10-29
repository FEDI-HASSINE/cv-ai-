"""
Resume Reviewer Page
Comprehensive resume analysis with ATS scoring and insights
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

# ⭐ NOUVEAU: Import pour DeepSeek R1 via OpenRouter
from openai import OpenAI

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


def extract_section(text: str, keyword: str) -> list:
    """
    Extrait une section du texte DeepSeek
    
    Args:
        text: Texte complet de l'analyse
        keyword: Mot-clé pour identifier la section
        
    Returns:
        Liste des éléments de la section
    """
    lines = text.split('\n')
    section_lines = []
    in_section = False
    
    for line in lines:
        if keyword in line.upper():
            in_section = True
            continue
        if in_section:
            if line.strip().startswith(('-', '•', '*')):
                section_lines.append(line.strip())
            elif line.strip() and not any(line.strip().startswith(str(i)) for i in range(1, 10)):
                # Stop if we hit a line that doesn't start with bullet or number
                if not line.strip().startswith(('-', '•', '*')):
                    break
    
    return section_lines if section_lines else ["Analyse en cours..."]


def analyze_with_deepseek(resume_text: str, basic_analysis: dict) -> dict:
    """
    Analyse avancée du CV avec DeepSeek R1 via 3 prompts séparés
    
    Args:
        resume_text: Texte complet du CV
        basic_analysis: Résultats de l'analyse basique
        
    Returns:
        dict: Analyse enrichie avec insights DeepSeek
    """
    if not st.session_state.get('use_deepseek', False):
        return basic_analysis
    
    try:
        client = st.session_state.deepseek_client
        
        # Informations de base pour tous les prompts
        base_info = f"""RESUME TEXT:
{resume_text}

BASIC ANALYSIS:
- ATS Score: {basic_analysis['ats_score']}/100
- Experience: {basic_analysis['experience_years']} years
- Technical Skills: {', '.join(basic_analysis['technical_skills'][:10])}
- Soft Skills: {', '.join(basic_analysis['soft_skills'][:5])}
"""

        # ⭐ PROMPT 1: Générer Strengths & Weaknesses
        prompt_strengths = f"""You are an expert HR analyst. Analyze this resume and identify its strengths and weaknesses.

{base_info}

Please provide:

**STRENGTHS** (3-5 detailed points):
- What makes this resume stand out?
- What are the candidate's key competitive advantages?

**WEAKNESSES** (3-5 detailed points):
- What critical elements are missing?
- What could significantly improve the resume?

Format your response with clear sections using bullet points (- or •).
Be specific, actionable, and professional."""

        # Appel API pour Strengths & Weaknesses
        completion_strengths = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": st.session_state.get('site_url', ''),
                "X-Title": st.session_state.get('site_name', ''),
            },
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[{"role": "user", "content": prompt_strengths}],
            temperature=0.7,
            max_tokens=1500
        )
        
        strengths_weaknesses_text = completion_strengths.choices[0].message.content
        
        # ⭐ PROMPT 2: Générer Improvement Suggestions
        prompt_suggestions = f"""You are an expert career coach. Analyze this resume and provide actionable improvement suggestions.

{base_info}

Please provide:

**IMPROVEMENT SUGGESTIONS** (5-7 actionable recommendations):
- Specific, prioritized actions to enhance the resume
- Include examples where applicable
- Focus on high-impact changes

Format your response with numbered or bulleted suggestions.
Be specific, actionable, and professional."""

        # Appel API pour Improvement Suggestions
        completion_suggestions = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": st.session_state.get('site_url', ''),
                "X-Title": st.session_state.get('site_name', ''),
            },
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[{"role": "user", "content": prompt_suggestions}],
            temperature=0.7,
            max_tokens=1500
        )
        
        suggestions_text = completion_suggestions.choices[0].message.content
        
        # ⭐ PROMPT 3: Générer Complete Analysis
        prompt_complete = f"""You are an expert HR analyst and career coach. Provide a comprehensive resume analysis.

{base_info}

Provide a complete professional assessment covering:
- Overall impression
- Key observations
- Market competitiveness
- Hiring potential

Be thorough, insightful, and professional."""

        # Appel API pour Complete Analysis
        completion_complete = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": st.session_state.get('site_url', ''),
                "X-Title": st.session_state.get('site_name', ''),
            },
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[{"role": "user", "content": prompt_complete}],
            temperature=0.7,
            max_tokens=2000
        )
        
        complete_analysis_text = completion_complete.choices[0].message.content
        
        # Enrichir l'analyse basique
        basic_analysis['deepseek_analysis'] = {
            'strengths_weaknesses_full': strengths_weaknesses_text,
            'suggestions_full': suggestions_text,
            'complete_analysis': complete_analysis_text,
            'strengths_detailed': extract_section(strengths_weaknesses_text, 'STRENGTHS'),
            'weaknesses_detailed': extract_section(strengths_weaknesses_text, 'WEAKNESSES'),
            'suggestions_detailed': extract_section(suggestions_text, 'SUGGESTION')
        }
        
        st.success("✅ Analyse DeepSeek R1 complétée avec succès!")
        
    except Exception as e:
        st.error(f"❌ Erreur DeepSeek R1: {str(e)}")
        st.info("💡 Utilisation de l'analyse standard")
    
    return basic_analysis


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
        st.markdown("*Choisissez votre moteur d'analyse IA*")
        
        # Sélecteur de modèle IA
        ai_model = st.radio(
            "Modèle IA",
            options=["DeepSeek R1 (Recommandé)", "OpenAI GPT", "Hugging Face (Gratuit)"],
            index=0,
            help="DeepSeek R1 offre les meilleures performances pour l'analyse de CV"
        )
        
        if ai_model == "DeepSeek R1 (Recommandé)":
            st.markdown("### 🚀 DeepSeek R1 Configuration")
            
            openrouter_key = st.text_input(
                "OpenRouter API Key",
                type="password",
                help="Votre clé API OpenRouter pour accéder à DeepSeek R1",
                placeholder="sk-or-v1-...",
                key="openrouter_key"
            )
            
            site_url = st.text_input(
                "Site URL (Optionnel)",
                placeholder="https://votre-site.com",
                help="Pour les rankings sur openrouter.ai",
                key="site_url"
            )
            
            site_name = st.text_input(
                "Site Name (Optionnel)",
                placeholder="Mon Application CV",
                help="Nom de votre application",
                key="site_name"
            )
            
            if openrouter_key:
                st.success("✅ DeepSeek R1 activé - Analyse avancée disponible")
                # Initialiser le client DeepSeek
                st.session_state.deepseek_client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_key,
                )
                st.session_state.use_deepseek = True
                st.session_state.site_url = site_url or "https://github.com/FEDI-HASSINE/cv-ai-"
                st.session_state.site_name = site_name or "UtopiaHire CV Analyzer"
            else:
                st.warning("⚠️ Clé API requise pour DeepSeek R1")
                st.session_state.use_deepseek = False
                st.info("💡 Obtenez votre clé sur: https://openrouter.ai/")
        
        elif ai_model == "OpenAI GPT":
            st.markdown("### 🔓 OpenAI Configuration")
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Votre clé OpenAI pour GPT",
                placeholder="sk-..."
            )
            
            if openai_key:
                st.success("✅ OpenAI GPT activé")
                st.session_state.analyzer = ResumeAnalyzer(openai_api_key=openai_key)
                st.session_state.use_deepseek = False
            else:
                st.info("💡 Utilisation des modèles gratuits")
                st.session_state.use_deepseek = False
        
        else:  # Hugging Face
            st.info("💡 Utilisation des modèles Hugging Face gratuits (peut être lent)")
            st.session_state.use_deepseek = False
    
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
        
        # Afficher TOUT le texte extrait (pas de limite)
        with st.expander("🔍 View Extracted Text (for debugging)", expanded=False):
            st.text_area(
                "Raw Text (Complete)", 
                parsed["text"], 
                height=400,  # Augmenté pour plus de visibilité
                help="Texte complet extrait du CV (sans limite de caractères)"
            )
            st.info(f"📊 Total: {len(parsed['text'])} caractères | {len(parsed['text'].split())} mots")
        
        # Analyze button
        if st.button("🔍 Analyze Resume", type="primary"):
            with st.spinner("🤖 Analyzing your resume... This may take a moment."):
                analysis = st.session_state.analyzer.analyze(parsed["text"])
                
                # ⭐ NOUVEAU: Enrichir avec DeepSeek si activé
                if st.session_state.get('use_deepseek', False):
                    with st.spinner("🚀 Enrichissement avec DeepSeek R1..."):
                        analysis = analyze_with_deepseek(parsed["text"], analysis)
                
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
            
            # ⭐ NOUVEAU: Section DeepSeek R1 Analysis
            if 'deepseek_analysis' in analysis:
                st.markdown("---")
                st.markdown("## 🤖 DeepSeek R1 - Analyse Avancée")
                
                with st.expander("📊 Analyse Complète DeepSeek", expanded=True):
                    st.markdown(analysis['deepseek_analysis']['complete_analysis'])
                
                st.markdown("---")
                
                # Affichage en colonnes pour Strengths et Weaknesses
                col1, col2 = st.columns(2)
                
                with col1:
                    # Strengths détaillées
                    st.markdown("### 💪 Forces Identifiées (DeepSeek)")
                    if analysis['deepseek_analysis']['strengths_detailed']:
                        for strength in analysis['deepseek_analysis']['strengths_detailed']:
                            st.markdown(f"{strength}")
                    else:
                        st.info("Aucune force spécifique identifiée")
                    
                    # Afficher aussi le texte brut des forces
                    with st.expander("📄 Détails Forces & Faiblesses", expanded=False):
                        st.markdown(analysis['deepseek_analysis']['strengths_weaknesses_full'])
                
                with col2:
                    # Weaknesses détaillées
                    st.markdown("### ⚠️ Points à Améliorer (DeepSeek)")
                    if analysis['deepseek_analysis']['weaknesses_detailed']:
                        for weakness in analysis['deepseek_analysis']['weaknesses_detailed']:
                            st.markdown(f"{weakness}")
                    else:
                        st.success("Aucune faiblesse majeure identifiée")
                
                st.markdown("---")
                
                # Suggestions détaillées
                st.markdown("### 💡 Recommandations Détaillées (DeepSeek)")
                if analysis['deepseek_analysis']['suggestions_detailed']:
                    for i, suggestion in enumerate(analysis['deepseek_analysis']['suggestions_detailed'], 1):
                        st.markdown(f"{i}. {suggestion}")
                else:
                    st.info("Aucune suggestion spécifique")
                
                # Afficher aussi le texte brut des suggestions
                with st.expander("📄 Détails Suggestions Complètes", expanded=False):
                    st.markdown(analysis['deepseek_analysis']['suggestions_full'])
            
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
