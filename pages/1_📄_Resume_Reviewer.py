"""
Resume Reviewer Page
Comprehensive resume analysis with ATS scoring and insights
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json
import requests
import re
import os

# ⭐ NOUVEAU: Import pour DeepSeek R1 via OpenRouter
from openai import OpenAI
class _SimpleChoice:
    def __init__(self, content: str):
        self.message = type("_Msg", (), {"content": content})


class _SimpleCompletion:
    def __init__(self, content: str):
        self.choices = [_SimpleChoice(content)]


class SimpleOpenAIClient:
    """
    Client minimaliste compatible avec l'API OpenAI pour des serveurs locaux (ex: Ollama).
    Implémente uniquement chat.completions.create utilisé dans cette page.
    """

    def __init__(self, base_url: str, api_key: str | None = None, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout
        self.chat = type("_Chat", (), {"completions": self})

    # API: chat.completions.create(...)
    def create(self, *, model: str, messages, temperature: float = 0.7, max_tokens: int = 1000, extra_headers=None):
        url = f"{self.base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if extra_headers:
            headers.update(extra_headers)
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        # Renvoyer un objet avec la même interface minimale que openai
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return _SimpleCompletion(content)

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
    
    bullet_prefixes = ('-', '•', '*', '–', '—')
    number_item = re.compile(r"^\s*\d+[\.)]\s+")
    md_heading = re.compile(r"^\s{0,3}#{1,6}\s+")

    for line in lines:
        up = line.upper()
        if keyword in up:
            in_section = True
            continue
        if in_section:
            s = line.strip()
            if not s:
                # Skip empty lines inside section
                continue
            # Stop if we hit a new heading (ALL CAPS short line or markdown heading)
            if md_heading.match(line) or (s.isupper() and 1 <= len(s) <= 80):
                break
            # Collect bullet-like or numbered items
            if s.startswith(bullet_prefixes) or number_item.match(s):
                section_lines.append(s)
            else:
                # Also collect short paragraph lines as items when LLM didn't add bullets
                if len(s) <= 300:
                    section_lines.append(s)
    
    return section_lines if section_lines else ["Analyse en cours..."]


def split_recommendations_from_complete(text: str):
    """
    Sépare la section 'Recommendations for Enhancement' du texte 'complete_analysis'.
    Retourne (texte_sans_reco, reco_markdown_list)
    - reco_markdown_list: liste de blocs markdown à afficher dans l'onglet Suggestions
    """
    if not text:
        return text, []
    lower = text.lower()
    key = 'recommendations for enhancement'
    idx = lower.find(key)
    if idx == -1:
        return text, []
    before = text[:idx].rstrip()
    recommendations_block = text[idx:].strip()
    return before, [recommendations_block]


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
        model_name = st.session_state.get('llm_model', "tngtech/deepseek-r1t2-chimera:free")
        extra_headers = st.session_state.get('llm_extra_headers', {})
        
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
            extra_headers=extra_headers,
            model=model_name,
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
            extra_headers=extra_headers,
            model=model_name,
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
            extra_headers=extra_headers,
            model=model_name,
            messages=[{"role": "user", "content": prompt_complete}],
            temperature=0.7,
            max_tokens=2000
        )
        
        complete_analysis_text = completion_complete.choices[0].message.content
        # Séparer la section 'Recommendations for Enhancement' pour l'afficher dans l'onglet Suggestions
        complete_main, reco_from_complete = split_recommendations_from_complete(complete_analysis_text)

        # ⭐ PROMPT 4: Estimer les années d'expérience (extraction LLM concise)
        prompt_experience = f"""From the resume text below, estimate TOTAL years of professional experience.

Return ONLY a number in years (decimals allowed), no words, no units, no explanation.

RESUME:
{resume_text}
"""

        try:
            completion_exp = client.chat.completions.create(
                extra_headers=extra_headers,
                model=model_name,
                messages=[{"role": "user", "content": prompt_experience}],
                temperature=0.2,
                max_tokens=16
            )
            exp_text = completion_exp.choices[0].message.content.strip()
            # Extraire un nombre flottant
            import re as _re
            m = _re.search(r"\d+(?:[\.,]\d+)?", exp_text)
            if m:
                years = float(m.group(0).replace(',', '.'))
                # Met à jour l'analyse avec la valeur LLM si plausible
                if 0.0 <= years <= 50.0:
                    basic_analysis['experience_years'] = round(years, 1)
                    basic_analysis.setdefault('ai_extracted_fields', {})['experience_years'] = 'llm'
        except Exception:
            pass
        
        # Enrichir l'analyse basique
        basic_analysis['deepseek_analysis'] = {
            'strengths_weaknesses_full': strengths_weaknesses_text,
            'suggestions_full': suggestions_text,
            'complete_analysis': complete_analysis_text,
            'complete_analysis_main': complete_main,  # sans la section recommandations si détectée
            'suggestions_from_complete': reco_from_complete,  # section recommandations extraite
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
            options=["DeepSeek R1 (Recommandé)", "Local LLM (Ollama)", "OpenAI GPT", "Hugging Face (Gratuit)"],
            index=0,
            help="DeepSeek R1 offre les meilleures performances pour l'analyse de CV"
        )
        
        if ai_model == "DeepSeek R1 (Recommandé)":
            st.markdown("### 🚀 DeepSeek R1 Configuration")
            
            # Lecture clé via secrets/env si disponible
            auto_key = None
            try:
                auto_key = st.secrets.get("OPENROUTER_API_KEY", None)
            except Exception:
                auto_key = None
            auto_key = auto_key or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")

            openrouter_key = None
            if not auto_key:
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
            
            effective_key = auto_key or openrouter_key
            if effective_key:
                st.success("✅ DeepSeek R1 activé - Analyse avancée disponible")
                # Utiliser le client simple compatible OpenAI pour éviter les problèmes de proxies
                st.session_state.deepseek_client = SimpleOpenAIClient(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=effective_key,
                )
                st.session_state.llm_model = "tngtech/deepseek-r1t2-chimera:free"
                st.session_state.llm_extra_headers = {
                    "HTTP-Referer": st.session_state.get('site_url', '') or "https://github.com/FEDI-HASSINE/cv-ai-",
                    "X-Title": st.session_state.get('site_name', '') or "UtopiaHire CV Analyzer",
                }
                st.session_state.use_deepseek = True
                if auto_key:
                    st.caption("Clé chargée automatiquement via environnement/secrets.")
            else:
                st.warning("⚠️ Clé API requise pour DeepSeek R1")
                st.session_state.use_deepseek = False
                st.info("💡 Obtenez votre clé sur: https://openrouter.ai/")
        elif ai_model == "Local LLM (Ollama)":
            st.markdown("### 🖥️ Local LLM (Ollama)")
            base_url = st.text_input(
                "Base URL",
                value="http://localhost:11434/v1",
                help="Endpoint API compatible OpenAI exposé par Ollama",
                key="ollama_base_url"
            )
            model_name = st.text_input(
                "Model Name",
                value="qwen2.5:1.5b-instruct",
                help="Nom du modèle Ollama (par ex. qwen2.5:1.5b-instruct, phi3:mini, mistral:7b-instruct)",
                key="ollama_model"
            )
            api_key = st.text_input(
                "API Key",
                value="ollama",
                help="Valeur arbitraire exigée par le client; pas utilisée par Ollama",
                key="ollama_api_key"
            )
            if base_url and model_name:
                try:
                    # Utiliser le client simple compatible OpenAI pour éviter les incohérences de dépendances
                    st.session_state.deepseek_client = SimpleOpenAIClient(
                        base_url=base_url,
                        api_key=api_key or "ollama",
                    )
                    st.session_state.llm_model = model_name
                    st.session_state.llm_extra_headers = {}
                    st.session_state.use_deepseek = True
                    st.success(f"✅ Local LLM prêt: {model_name}")
                    st.caption("Assurez-vous qu'Ollama tourne localement et que le modèle est installé.")
                except Exception as e:
                    st.error(f"Impossible d'initialiser le client local: {e}")
                    st.session_state.use_deepseek = False
        
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
                
                # If DeepSeek analysis is available, show the LLM comprehensive analysis here
                deepseek = analysis.get('deepseek_analysis')
                if deepseek and (deepseek.get('complete_analysis_main') or deepseek.get('complete_analysis')):
                    # Affiche la version sans 'Recommendations for Enhancement' si disponible
                    st.markdown(deepseek.get('complete_analysis_main') or deepseek.get('complete_analysis'))
                    st.markdown("---")
                else:
                    st.info("Activez DeepSeek dans la barre latérale pour afficher l'analyse complète générée par LLM dans cette section.")
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
                
                # Quick Insights section removed per request
            
            with tab2:
                st.markdown("### Strengths & Weaknesses (LLM)")
                deepseek = analysis.get('deepseek_analysis')
                if deepseek:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### ✅ Strengths")
                        strengths_llm = deepseek.get('strengths_detailed') or []
                        if strengths_llm:
                            for strength in strengths_llm:
                                st.markdown(f'<div class="strength-item">{strength}</div>', unsafe_allow_html=True)
                        else:
                            st.info("No strengths provided by LLM.")
                    with col2:
                        st.markdown("#### ⚠️ Weaknesses")
                        weaknesses_llm = deepseek.get('weaknesses_detailed') or []
                        if weaknesses_llm:
                            for weakness in weaknesses_llm:
                                st.markdown(f'<div class="weakness-item">{weakness}</div>', unsafe_allow_html=True)
                        else:
                            st.info("No weaknesses provided by LLM.")
                else:
                    st.info("Activez DeepSeek dans la barre latérale pour voir les forces et faiblesses générées par LLM.")
            
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
                st.markdown("### 💡 Improvement Suggestions (LLM)")
                deepseek = analysis.get('deepseek_analysis')
                if deepseek:
                    # Suggestions issues du prompt dédié
                    if deepseek.get('suggestions_detailed'):
                        for i, suggestion in enumerate(deepseek['suggestions_detailed'], 1):
                            st.markdown(f"{i}. {suggestion}")
                    # Recommandations extraites de l'analyse complète
                    if deepseek.get('suggestions_from_complete'):
                        st.markdown("---")
                        st.markdown("#### 📌 Recommendations for Enhancement (LLM)")
                        for block in deepseek['suggestions_from_complete']:
                            st.markdown(block)
                else:
                    st.info("Activez DeepSeek dans la barre latérale pour voir les suggestions générées par LLM.")
            
            # DeepSeek section centralisée supprimée: le contenu est désormais réparti dans les onglets.
            
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
