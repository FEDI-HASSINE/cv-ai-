"""
Resume Rewriter Page
AI-powered resume optimization and rewriting suggestions
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json
import re
from io import BytesIO
from openai import OpenAI
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

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


def optimize_with_deepseek(resume_text: str, basic_analysis: dict) -> dict:
    """
    Optimisation avancée du CV avec DeepSeek R1
    
    Args:
        resume_text: Texte complet du CV
        basic_analysis: Analyse basique existante (fallback)
        
    Returns:
        dict: Suggestions optimisées avec DeepSeek ou fallback
    """
    if not st.session_state.get('use_rewriter_deepseek', False):
        # Fallback : retourner l'analyse basique
        return basic_analysis
    
    try:
        client = st.session_state['rewriter_deepseek_client']
        
        # Construire le prompt pour DeepSeek
        prompt = f"""You are an expert resume writer and career coach specializing in ATS-optimized resumes. 

RESUME TO OPTIMIZE:
{resume_text}

CURRENT BASIC ANALYSIS:
- Weak phrases detected: {len(basic_analysis.get('weak_phrases', []))}
- Basic action verbs suggested: {len(basic_analysis.get('action_verbs', {}))}
- Basic formatting issues: {len(basic_analysis.get('formatting', []))}

YOUR MISSION:
Provide a comprehensive, personalized optimization analysis of this specific resume.

REQUIRED OUTPUT (in JSON format):

1. WEAK_PHRASES_ANALYSIS:
   - Identify ALL weak/passive phrases in this resume
   - For each, provide:
     * Original phrase (exact quote from resume)
     * Why it's weak (specific explanation)
     * Stronger alternative (contextualized to this resume)
     * Priority (High/Medium/Low)
   
2. ACTION_VERBS_SUGGESTIONS:
   - Analyze current verbs used in this resume
   - Suggest 10-15 BETTER action verbs categorized by:
     * Leadership verbs (if applicable)
     * Technical verbs (if applicable)
     * Achievement verbs
     * Innovation verbs
   - For each verb, provide example usage in THIS resume's context

3. QUANTIFICATION_OPPORTUNITIES:
   - Identify 5-10 specific statements that need quantification
   - For each:
     * Original vague statement (exact quote)
     * Suggested quantified version (with example metrics)
     * Impact explanation

4. FORMATTING_IMPROVEMENTS:
   - List 5-8 specific formatting issues in THIS resume
   - Provide actionable fixes

5. PRIORITY_RECOMMENDATIONS:
   - 3-5 HIGH priority changes (biggest impact)
   - 3-5 MEDIUM priority improvements
   - 2-3 LOW priority nice-to-haves
   - For each: specific action + expected impact

6. OPTIMIZED_RESUME_SECTIONS:
   - Rewrite the MOST IMPORTANT sections (Summary, Experience bullets)
   - Keep original structure but optimize language
   - Maintain factual accuracy

7. IMPROVEMENT_SCORE:
   - Current score: 0-100
   - Potential score after improvements: 0-100
   - Key areas of improvement

Return your analysis in valid JSON format with these exact keys:
{{
  "weak_phrases": [...],
  "action_verbs": {{...}},
  "quantification": [...],
  "formatting": [...],
  "priority_recommendations": {{...}},
  "optimized_sections": {{...}},
  "improvement_score": {{...}}
}}

Be specific, actionable, and reference the actual content of this resume."""

        # Appel API DeepSeek R1
        with st.spinner("🤖 DeepSeek R1 analyse votre CV en profondeur..."):
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/FEDI-HASSINE/cv-ai-",
                    "X-Title": "UtopiaHire Resume Rewriter",
                },
                model="deepseek/deepseek-r1",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
        
        # Extraire et parser la réponse
        response_text = completion.choices[0].message.content
        
        # Essayer de parser le JSON
        try:
            # Extraire le JSON de la réponse (peut être entouré de ```json...```)
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                json_text = response_text
            
            deepseek_data = json.loads(json_text)
            
            # Enrichir l'analyse basique avec DeepSeek
            enhanced_analysis = basic_analysis.copy()
            enhanced_analysis.update({
                'deepseek_enabled': True,
                'deepseek_weak_phrases': deepseek_data.get('weak_phrases', []),
                'deepseek_action_verbs': deepseek_data.get('action_verbs', {}),
                'deepseek_quantification': deepseek_data.get('quantification', []),
                'deepseek_formatting': deepseek_data.get('formatting', []),
                'deepseek_recommendations': deepseek_data.get('priority_recommendations', {}),
                'deepseek_optimized': deepseek_data.get('optimized_sections', {}),
                'deepseek_scores': deepseek_data.get('improvement_score', {}),
                'deepseek_raw_response': response_text
            })
            
            st.success("✅ Analyse DeepSeek R1 terminée avec succès!")
            return enhanced_analysis
            
        except json.JSONDecodeError:
            # Si JSON invalide, retourner la réponse brute
            st.warning("⚠️ Réponse DeepSeek reçue mais format non-JSON, utilisation en mode texte")
            enhanced_analysis = basic_analysis.copy()
            enhanced_analysis.update({
                'deepseek_enabled': True,
                'deepseek_raw_response': response_text,
                'deepseek_text_mode': True
            })
            return enhanced_analysis
        
    except Exception as e:
        st.error(f"❌ Erreur DeepSeek R1: {str(e)}")
        st.info("💡 Utilisation de l'analyse standard")
        return basic_analysis


def generate_optimized_resume_docx(original_text: str, optimized_data: dict) -> BytesIO:
    """
    Génère un CV optimisé au format DOCX
    
    Args:
        original_text: Texte original du CV
        optimized_data: Données d'optimisation (DeepSeek ou standard)
        
    Returns:
        BytesIO: Document DOCX en mémoire
    """
    doc = Document()
    
    # Styles
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    # Titre
    title = doc.add_heading('OPTIMIZED RESUME', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Note d'optimisation
    note = doc.add_paragraph()
    note.add_run('✨ This resume has been optimized using AI-powered suggestions\n').bold = True
    note.add_run(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()  # Spacing
    
    # Si DeepSeek a optimisé des sections
    if optimized_data.get('deepseek_enabled') and optimized_data.get('deepseek_optimized'):
        optimized_sections = optimized_data['deepseek_optimized']
        
        # Summary optimisé
        if optimized_sections.get('summary'):
            doc.add_heading('PROFESSIONAL SUMMARY', 1)
            doc.add_paragraph(optimized_sections['summary'])
            doc.add_paragraph()
        
        # Experience optimisée
        if optimized_sections.get('experience'):
            doc.add_heading('PROFESSIONAL EXPERIENCE', 1)
            for exp in optimized_sections['experience']:
                p = doc.add_paragraph()
                p.add_run(exp.get('title', '')).bold = True
                doc.add_paragraph(exp.get('description', ''))
            doc.add_paragraph()
        
        # Skills
        if optimized_sections.get('skills'):
            doc.add_heading('SKILLS', 1)
            doc.add_paragraph(optimized_sections['skills'])
            doc.add_paragraph()
    else:
        # Fallback : utiliser le texte original avec suggestions
        doc.add_heading('ORIGINAL CONTENT', 1)
        doc.add_paragraph(original_text)
        doc.add_paragraph()
    
    # Section des suggestions appliquées
    doc.add_page_break()
    doc.add_heading('OPTIMIZATION NOTES', 1)
    
    if optimized_data.get('deepseek_recommendations'):
        recs = optimized_data['deepseek_recommendations']
        
        if recs.get('high_priority'):
            doc.add_heading('High Priority Changes Applied:', 2)
            for rec in recs['high_priority']:
                doc.add_paragraph(f"• {rec}", style='List Bullet')
            doc.add_paragraph()
        
        if recs.get('medium_priority'):
            doc.add_heading('Medium Priority Improvements:', 2)
            for rec in recs['medium_priority']:
                doc.add_paragraph(f"• {rec}", style='List Bullet')
            doc.add_paragraph()
    
    # Sauvegarder en mémoire
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


def generate_optimized_resume_pdf(original_text: str, optimized_data: dict) -> BytesIO:
    """
    Génère un CV optimisé au format PDF
    
    Args:
        original_text: Texte original du CV
        optimized_data: Données d'optimisation
        
    Returns:
        BytesIO: Document PDF en mémoire
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=1*inch, bottomMargin=1*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#2E86AB',
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2E86AB',
        spaceAfter=6
    )
    
    # Contenu
    story = []
    
    # Titre
    story.append(Paragraph("OPTIMIZED RESUME", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Note
    note_text = f"✨ <b>This resume has been optimized using AI-powered suggestions</b><br/>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    story.append(Paragraph(note_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Contenu optimisé
    if optimized_data.get('deepseek_enabled') and optimized_data.get('deepseek_optimized'):
        optimized_sections = optimized_data['deepseek_optimized']
        
        if optimized_sections.get('summary'):
            story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
            story.append(Paragraph(optimized_sections['summary'], styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Autres sections...
    else:
        story.append(Paragraph("ORIGINAL CONTENT", heading_style))
        story.append(Paragraph(original_text.replace('\n', '<br/>'), styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


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
        
        # AI Configuration
        st.markdown("### 🤖 AI Configuration")
        st.markdown("*Pour des suggestions personnalisées*")
        
        ai_model = st.radio(
            "Moteur d'optimisation",
            options=["DeepSeek R1 (Recommandé)", "Analyse Standard"],
            index=0,
            help="DeepSeek R1 génère des suggestions personnalisées basées sur votre CV"
        )
        
        if ai_model == "DeepSeek R1 (Recommandé)":
            st.markdown("#### 🚀 DeepSeek R1 Configuration")
            
            openrouter_key = st.text_input(
                "OpenRouter API Key",
                type="password",
                help="Clé API OpenRouter pour DeepSeek R1",
                placeholder="sk-or-v1-...",
                key="rewriter_openrouter_key"
            )
            
            if openrouter_key:
                st.success("✅ DeepSeek R1 activé")
                st.session_state['rewriter_deepseek_client'] = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_key,
                )
                st.session_state['use_rewriter_deepseek'] = True
            else:
                st.warning("⚠️ Clé API requise pour suggestions personnalisées")
                st.session_state['use_rewriter_deepseek'] = False
                st.info("💡 Sans clé : suggestions basiques maintenues")
        else:
            st.session_state['use_rewriter_deepseek'] = False
            st.info("💡 Mode standard : suggestions basiques")
        
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
                
                # Enrichir avec DeepSeek si activé
                if st.session_state.get('use_rewriter_deepseek', False):
                    rewrite = optimize_with_deepseek(parsed["text"], rewrite)
                
                st.session_state.rewrite = rewrite
        
        # Display results
        if 'rewrite' in st.session_state:
            rewrite = st.session_state.rewrite
            
            st.markdown("---")
            st.markdown("## ✨ Optimization Suggestions")
            
            # Afficher le score DeepSeek si disponible
            if rewrite.get('deepseek_enabled') and rewrite.get('deepseek_scores'):
                scores = rewrite['deepseek_scores']
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "📊 Current Score",
                        f"{scores.get('current', 50)}/100",
                        help="Score actuel de votre CV"
                    )
                
                with col2:
                    improvement = scores.get('potential', 80) - scores.get('current', 50)
                    st.metric(
                        "🚀 Potential Score",
                        f"{scores.get('potential', 80)}/100",
                        delta=f"+{improvement}",
                        help="Score après optimisations"
                    )
                
                st.progress(scores.get('potential', 80) / 100)
            else:
                # Fallback : affichage standard
                improvement_score = rewrite.get('improvement_score', 50)
                st.markdown(f"""
                <div class="improvement-card">
                    <h3>📈 Improvement Potential: {improvement_score}/100</h3>
                    <p>Your resume has significant potential for optimization!</p>
                </div>
                """, unsafe_allow_html=True)
                st.progress(improvement_score / 100)
            
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
                            &#10060; <span style="color: #dc3545;">{wp['weak_phrase']}</span><br>
                            &#9989; <span style="color: #28a745;">{wp['strong_alternative']}</span><br>
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
                            &#128161; <strong>{opp['suggestion']}</strong>
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
            
            # DeepSeek R1 Optimizations Section
            if rewrite.get('deepseek_enabled'):
                st.markdown("---")
                st.markdown("## 🤖 DeepSeek R1 - Personalized Optimization")
                
                # Weak Phrases avec DeepSeek
                if rewrite.get('deepseek_weak_phrases'):
                    st.markdown("### 🔄 Weak Phrases (AI-Detected)")
                    
                    for i, phrase in enumerate(rewrite['deepseek_weak_phrases'][:10], 1):
                        with st.expander(f"❌ Phrase {i}: \"{phrase.get('original', 'N/A')}\"", expanded=(i <= 3)):
                            st.markdown(f"**Why it's weak:** {phrase.get('reason', 'Generic language')}")
                            st.markdown(f"**✅ Stronger alternative:**")
                            st.success(phrase.get('alternative', 'Use more specific action verbs'))
                            
                            priority = phrase.get('priority', 'Medium')
                            if priority == 'High':
                                st.error(f"🔥 Priority: {priority}")
                            elif priority == 'Medium':
                                st.warning(f"⚠️ Priority: {priority}")
                            else:
                                st.info(f"💡 Priority: {priority}")
                
                # Action Verbs avec DeepSeek
                if rewrite.get('deepseek_action_verbs'):
                    st.markdown("### 💪 Action Verbs (Contextualized)")
                    
                    verbs = rewrite['deepseek_action_verbs']
                    verb_categories = list(verbs.keys())[:4]  # Max 4 catégories
                    
                    if verb_categories:
                        tabs = st.tabs(verb_categories)
                        
                        for tab, category in zip(tabs, verb_categories):
                            with tab:
                                verb_list = verbs[category]
                                for verb_data in verb_list[:5]:
                                    if isinstance(verb_data, dict):
                                        st.markdown(f"**{verb_data.get('verb', 'N/A')}**")
                                        st.caption(f"Example: {verb_data.get('example', 'N/A')}")
                                    else:
                                        st.markdown(f"**{verb_data}**")
                                    st.markdown("---")
                
                # Quantification avec DeepSeek
                if rewrite.get('deepseek_quantification'):
                    st.markdown("### 📊 Quantification Opportunities (AI-Identified)")
                    
                    for i, quant in enumerate(rewrite['deepseek_quantification'][:5], 1):
                        with st.expander(f"📈 Opportunity {i}", expanded=(i == 1)):
                            st.markdown("**Original (vague):**")
                            st.info(quant.get('original', 'N/A'))
                            
                            st.markdown("**✅ Quantified version:**")
                            st.success(quant.get('quantified', 'N/A'))
                            
                            st.markdown(f"**Impact:** {quant.get('impact', 'Makes achievement measurable')}")
                
                # Formatting avec DeepSeek
                if rewrite.get('deepseek_formatting'):
                    st.markdown("### 🎨 Formatting Improvements (AI-Detected)")
                    
                    for issue in rewrite['deepseek_formatting']:
                        st.markdown(f"• {issue}")
                
                # Priority Recommendations avec DeepSeek
                if rewrite.get('deepseek_recommendations'):
                    st.markdown("### 🎯 Priority Recommendations (AI-Personalized)")
                    
                    recs = rewrite['deepseek_recommendations']
                    
                    if recs.get('high_priority'):
                        st.markdown("#### 🔥 High Priority")
                        for rec in recs['high_priority']:
                            st.error(f"• {rec}")
                    
                    if recs.get('medium_priority'):
                        st.markdown("#### ⚠️ Medium Priority")
                        for rec in recs['medium_priority']:
                            st.warning(f"• {rec}")
                    
                    if recs.get('low_priority'):
                        st.markdown("#### 💡 Low Priority")
                        for rec in recs['low_priority']:
                            st.info(f"• {rec}")
                
                # Texte brut si mode texte
                if rewrite.get('deepseek_text_mode'):
                    with st.expander("📝 DeepSeek Full Response (Text Mode)", expanded=False):
                        st.text_area("Raw Response", rewrite.get('deepseek_raw_response', ''), height=400, key="deepseek_raw")
            
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
            st.markdown("### 📥 Download Optimized Resume")
            
            # Check if DeepSeek generated optimized content
            if rewrite.get('deepseek_enabled') and rewrite.get('deepseek_optimized'):
                st.success("✅ Une version optimisée de votre CV a été générée !")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Génération DOCX
                    try:
                        with st.spinner("Generating DOCX..."):
                            docx_buffer = generate_optimized_resume_docx(parsed["text"], rewrite)
                        
                        st.download_button(
                            label="📄 Download as DOCX",
                            data=docx_buffer,
                            file_name=f"optimized_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            help="Télécharger le CV optimisé en format Word"
                        )
                    except Exception as e:
                        st.error(f"Error generating DOCX: {str(e)}")
                
                with col2:
                    # Génération PDF
                    try:
                        with st.spinner("Generating PDF..."):
                            pdf_buffer = generate_optimized_resume_pdf(parsed["text"], rewrite)
                        
                        st.download_button(
                            label="📕 Download as PDF",
                            data=pdf_buffer,
                            file_name=f"optimized_resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            help="Télécharger le CV optimisé en format PDF"
                        )
                    except ImportError:
                        st.warning("⚠️ PDF generation requires reportlab. Install with: pip install reportlab")
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")
            else:
                st.info("💡 Activez DeepSeek R1 pour générer une version complète optimisée de votre CV téléchargeable en PDF/DOCX")
            
            # Standard report downloads
            st.markdown("---")
            st.markdown("### 📥 Download Rewriting Report")
            
            # Generate comprehensive report
            report_text = f"""
UtopiaHire - Resume Rewriting Suggestions Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================

IMPROVEMENT POTENTIAL: {rewrite.get('improvement_score', 'N/A')}/100

WEAK PHRASES TO REPLACE ({len(rewrite.get('weak_phrases', []))})
========================
"""
            
            for idx, wp in enumerate(rewrite.get('weak_phrases', []), 1):
                report_text += f"""
{idx}. Weak: "{wp['weak_phrase']}"
   Strong: "{wp['strong_alternative']}"
   Context: "{wp['context'][:80]}..."
"""
            
            report_text += f"""

ACTION VERBS BY CATEGORY
========================
"""
            for category, verbs in rewrite.get('action_verbs', {}).items():
                report_text += f"\n{category}:\n  {', '.join(verbs)}\n"
            
            report_text += f"""

QUANTIFICATION OPPORTUNITIES ({len(rewrite.get('quantification', []))})
============================
"""
            for idx, opp in enumerate(rewrite.get('quantification', []), 1):
                report_text += f"""
{idx}. Context: "{opp['context'][:80]}..."
   Suggestion: {opp['suggestion']}
"""
            
            report_text += f"""

FORMATTING IMPROVEMENTS
=======================
"""
            for fmt in rewrite.get('formatting', []):
                report_text += f"• {fmt}\n"
            
            report_text += f"""

CONTENT ENHANCEMENTS
====================
"""
            for enh in rewrite.get('content_enhancements', []):
                report_text += f"• {enh}\n"
            
            report_text += f"""

PRIORITY RECOMMENDATIONS
========================
"""
            for rec in rewrite.get('recommendations', []):
                report_text += f"""
[{rec['priority']} Priority] {rec['category']}
  Recommendation: {rec['recommendation']}
  Impact: {rec['impact']}
"""
            
            report_text += f"""

OPTIMIZED SECTION EXAMPLES
==========================
"""
            for section_name, content in rewrite.get('optimized_sections', {}).items():
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
