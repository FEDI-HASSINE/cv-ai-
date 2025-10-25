"""
Footprint Scanner Page
Analyze professional digital presence across LinkedIn, GitHub, and StackOverflow
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config, COLORS
from src.core.footprint_scanner import FootprintScanner

st.set_page_config(page_title="Footprint Scanner", page_icon="🌐", layout="wide")

st.markdown(f"""
    <style>
        .platform-card {{
            background-color: #ffffff;
            border: 2px solid {COLORS['info']};
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
        }}
        .score-badge {{
            background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['info']});
            color: white;
            padding: 0.5rem 1.5rem;
            border-radius: 20px;
            font-size: 1.2rem;
            font-weight: bold;
            display: inline-block;
        }}
        .recommendation {{
            background-color: #fff3cd;
            border-left: 4px solid {COLORS['warning']};
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 5px;
        }}
        .strength {{
            background-color: #d4edda;
            border-left: 4px solid {COLORS['success']};
            padding: 0.8rem;
            margin: 0.3rem 0;
            border-radius: 5px;
        }}
        .improvement {{
            background-color: #f8d7da;
            border-left: 4px solid {COLORS['danger']};
            padding: 0.8rem;
            margin: 0.3rem 0;
            border-radius: 5px;
        }}
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("🌐 Digital Footprint Scanner")
    st.markdown("Analyze your professional online presence across major platforms")
    
    # Initialize
    if 'scanner' not in st.session_state:
        st.session_state.scanner = FootprintScanner()
    
    config = Config()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 What We Analyze")
        st.markdown("""
        **LinkedIn**
        - Profile completeness
        - Network size
        - Engagement activity
        - Endorsements
        
        **GitHub**
        - Repository quality
        - Contribution activity
        - Code quality
        - Community engagement
        
        **StackOverflow**
        - Reputation score
        - Answer quality
        - Expertise areas
        - Community involvement
        """)
        
        st.markdown("---")
        st.markdown("### 💡 Why It Matters")
        st.info("""
        A strong digital footprint:
        - Increases visibility to recruiters
        - Demonstrates expertise
        - Shows continuous learning
        - Builds professional credibility
        """)
    
    # Main content
    st.markdown("---")
    st.markdown("### 📝 Enter Your Profile URLs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        linkedin_url = st.text_input(
            "🔗 LinkedIn Profile URL",
            placeholder="https://linkedin.com/in/your-profile",
            help="Your LinkedIn profile URL"
        )
        
        github_username = st.text_input(
            "💻 GitHub Username",
            placeholder="yourusername",
            help="Your GitHub username (not full URL)"
        )
    
    with col2:
        stackoverflow_url = st.text_input(
            "📚 StackOverflow Profile URL",
            placeholder="https://stackoverflow.com/users/12345/your-name",
            help="Your StackOverflow profile URL"
        )
        
        st.markdown("")
        st.markdown("")
        st.info("💡 **Tip:** Provide at least one profile URL for analysis")
    
    # Scan button
    st.markdown("---")
    
    if st.button("🔍 Scan Digital Footprint", type="primary"):
        # Validate at least one input
        if not any([linkedin_url, github_username, stackoverflow_url]):
            st.error("Please provide at least one profile URL/username")
        else:
            with st.spinner("🌐 Scanning your digital footprint... This may take a moment."):
                analysis = st.session_state.scanner.analyze_footprint(
                    linkedin_url=linkedin_url if linkedin_url else None,
                    github_username=github_username if github_username else None,
                    stackoverflow_url=stackoverflow_url if stackoverflow_url else None
                )
                st.session_state.footprint_analysis = analysis
    
    # Display results
    if 'footprint_analysis' in st.session_state:
        analysis = st.session_state.footprint_analysis
        
        st.markdown("---")
        st.markdown("## 📊 Footprint Analysis Results")
        
        # Overall score
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 1.2rem; color: #666; margin-bottom: 1rem;">Overall Score</div>
                <div class="score-badge">{analysis['overall_score']}/100</div>
                <div style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
                    Based on {len(analysis['platforms_analyzed'])} platform(s)
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabs for detailed analysis
        tabs = ["📋 Overview", "🏆 Strengths", "📈 Improvements", "💡 Recommendations"]
        
        # Add platform-specific tabs
        if "LinkedIn" in analysis['platforms_analyzed']:
            tabs.append("🔗 LinkedIn")
        if "GitHub" in analysis['platforms_analyzed']:
            tabs.append("💻 GitHub")
        if "StackOverflow" in analysis['platforms_analyzed']:
            tabs.append("📚 StackOverflow")
        
        tab_objects = st.tabs(tabs)
        
        # Overview tab
        with tab_objects[0]:
            st.markdown("### Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Platforms Analyzed**")
                for platform in analysis['platforms_analyzed']:
                    st.success(f"✅ {platform}")
                
                # Missing platforms
                all_platforms = ["LinkedIn", "GitHub", "StackOverflow"]
                missing = [p for p in all_platforms if p not in analysis['platforms_analyzed']]
                
                if missing:
                    st.markdown("**Not Analyzed**")
                    for platform in missing:
                        st.warning(f"❌ {platform}")
            
            with col2:
                st.markdown("**Quick Stats**")
                st.metric("Platforms Active", len(analysis['platforms_analyzed']))
                st.metric("Overall Score", f"{analysis['overall_score']}/100")
                st.metric("Key Strengths", len(analysis.get('strengths', [])))
                st.metric("Areas to Improve", len(analysis.get('areas_for_improvement', [])))
        
        # Strengths tab
        with tab_objects[1]:
            st.markdown("### 🏆 Your Strengths")
            
            if analysis['strengths']:
                for strength in analysis['strengths']:
                    st.markdown(f"""
                    <div class="strength">
                        ✅ {strength}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Start building your online presence to develop strengths")
        
        # Improvements tab
        with tab_objects[2]:
            st.markdown("### 📈 Areas for Improvement")
            
            if analysis['areas_for_improvement']:
                for improvement in analysis['areas_for_improvement']:
                    st.markdown(f"""
                    <div class="improvement">
                        ⚠️ {improvement}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Great! No major areas for improvement identified")
        
        # Recommendations tab
        with tab_objects[3]:
            st.markdown("### 💡 Personalized Recommendations")
            
            if analysis['recommendations']:
                for rec in analysis['recommendations']:
                    priority = rec['priority']
                    
                    priority_colors = {
                        'Critical': COLORS['danger'],
                        'High': COLORS['warning'],
                        'Medium': COLORS['info'],
                        'Low': COLORS['primary']
                    }
                    
                    color = priority_colors.get(priority, COLORS['info'])
                    
                    st.markdown(f"""
                    <div style="border-left: 4px solid {color}; padding: 1rem; margin: 0.5rem 0; background-color: #f8f9fa;">
                        <strong>{priority} Priority</strong><br>
                        {rec['recommendation']}<br>
                        <small style="color: #666;"><em>Impact: {rec['impact']}</em></small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Keep maintaining your current online presence!")
        
        # Platform-specific tabs
        tab_index = 4
        
        if "LinkedIn" in analysis['platforms_analyzed']:
            with tab_objects[tab_index]:
                linkedin = analysis['linkedin']
                
                st.markdown("### 🔗 LinkedIn Analysis")
                st.markdown(f"""
                <div class="platform-card">
                    <h4>Profile Score: {linkedin['score']}/100</h4>
                    <p><strong>URL:</strong> {linkedin['url']}</p>
                    <p><strong>Status:</strong> {'✅ Valid' if linkedin['is_valid'] else '❌ Invalid'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if linkedin['insights']:
                    st.markdown("**Insights:**")
                    for insight in linkedin['insights']:
                        st.markdown(f"""
                        - **{insight['category']}**: {insight['status']}
                          <br><small>{insight['description']}</small>
                        """, unsafe_allow_html=True)
                
                if linkedin['recommendations']:
                    st.markdown("**Recommendations:**")
                    for rec in linkedin['recommendations']:
                        st.markdown(f"• {rec}")
            
            tab_index += 1
        
        if "GitHub" in analysis['platforms_analyzed']:
            with tab_objects[tab_index]:
                github = analysis['github']
                
                st.markdown("### 💻 GitHub Analysis")
                st.markdown(f"""
                <div class="platform-card">
                    <h4>Profile Score: {github['score']}/100</h4>
                    <p><strong>Username:</strong> {github['username']}</p>
                    <p><strong>Profile:</strong> <a href="{github['demo_stats']['profile_url']}" target="_blank">
                        {github['demo_stats']['profile_url']}
                    </a></p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**Demo Stats** *(Full stats available with API integration)*")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Activity Level:** {github['demo_stats']['activity_level']}")
                    st.write(f"**Popular Languages:** {', '.join(github['demo_stats']['popular_languages'])}")
                
                with col2:
                    st.info("Connect GitHub API to get:\n- Public repos count\n- Followers\n- Contribution graph\n- Stars & Forks")
                
                if github['insights']:
                    st.markdown("**Insights:**")
                    for insight in github['insights']:
                        st.markdown(f"- **{insight['category']}**: {insight['status']}")
                
                if github['recommendations']:
                    st.markdown("**Recommendations:**")
                    for rec in github['recommendations']:
                        st.markdown(f"• {rec}")
            
            tab_index += 1
        
        if "StackOverflow" in analysis['platforms_analyzed']:
            with tab_objects[tab_index]:
                stackoverflow = analysis['stackoverflow']
                
                st.markdown("### 📚 StackOverflow Analysis")
                st.markdown(f"""
                <div class="platform-card">
                    <h4>Profile Score: {stackoverflow['score']}/100</h4>
                    <p><strong>URL:</strong> {stackoverflow['url']}</p>
                    <p><strong>Status:</strong> {'✅ Valid' if stackoverflow['is_valid'] else '❌ Invalid'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**Demo Stats** *(Full stats available with API integration)*")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Top Tags:** {', '.join(stackoverflow['demo_stats']['top_tags'])}")
                
                with col2:
                    st.info("Connect StackOverflow API to get:\n- Reputation score\n- Badges earned\n- Answers & Questions\n- Accept rate")
                
                if stackoverflow['insights']:
                    st.markdown("**Insights:**")
                    for insight in stackoverflow['insights']:
                        st.markdown(f"- **{insight['category']}**: {insight['status']}")
                
                if stackoverflow['recommendations']:
                    st.markdown("**Recommendations:**")
                    for rec in stackoverflow['recommendations']:
                        st.markdown(f"• {rec}")
        
        # Download report
        st.markdown("---")
        st.markdown("### 📥 Download Footprint Analysis Report")
        
        # Generate comprehensive report
        report_text = f"""
UtopiaHire - Digital Footprint Analysis Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
==============================================

OVERALL ASSESSMENT
------------------
Overall Score: {analysis['overall_score']}/100
Platforms Analyzed: {', '.join(analysis['platforms_analyzed'])}
Total Platforms: {len(analysis['platforms_analyzed'])}

KEY STRENGTHS ({len(analysis.get('strengths', []))})
============
"""
        
        if analysis.get('strengths'):
            for idx, strength in enumerate(analysis['strengths'], 1):
                report_text += f"{idx}. {strength}\n"
        else:
            report_text += "No major strengths identified yet\n"
        
        report_text += f"""

AREAS FOR IMPROVEMENT ({len(analysis.get('areas_for_improvement', []))})
=====================
"""
        
        if analysis.get('areas_for_improvement'):
            for idx, improvement in enumerate(analysis['areas_for_improvement'], 1):
                report_text += f"{idx}. {improvement}\n"
        else:
            report_text += "No major improvements needed\n"
        
        report_text += f"""

RECOMMENDATIONS ({len(analysis.get('recommendations', []))})
===============
"""
        
        if analysis.get('recommendations'):
            for rec in analysis['recommendations']:
                report_text += f"""
Priority: {rec['priority']}
Recommendation: {rec['recommendation']}
Expected Impact: {rec['impact']}
---
"""
        else:
            report_text += "Keep maintaining your current online presence!\n"
        
        # Platform-specific details
        report_text += """

PLATFORM-SPECIFIC ANALYSIS
==========================
"""
        
        if "LinkedIn" in analysis['platforms_analyzed']:
            linkedin = analysis['linkedin']
            report_text += f"""
LINKEDIN
--------
Score: {linkedin['score']}/100
URL: {linkedin['url']}
Status: {'Valid' if linkedin['is_valid'] else 'Invalid'}

Insights:
"""
            if linkedin.get('insights'):
                for insight in linkedin['insights']:
                    report_text += f"  • {insight['category']}: {insight['status']}\n    {insight['description']}\n"
            
            report_text += "\nRecommendations:\n"
            if linkedin.get('recommendations'):
                for rec in linkedin['recommendations']:
                    report_text += f"  • {rec}\n"
            report_text += "\n"
        
        if "GitHub" in analysis['platforms_analyzed']:
            github = analysis['github']
            report_text += f"""
GITHUB
------
Score: {github['score']}/100
Username: {github['username']}
Profile: {github['demo_stats']['profile_url']}
Activity Level: {github['demo_stats']['activity_level']}
Popular Languages: {', '.join(github['demo_stats']['popular_languages'])}

Insights:
"""
            if github.get('insights'):
                for insight in github['insights']:
                    report_text += f"  • {insight['category']}: {insight['status']}\n"
            
            report_text += "\nRecommendations:\n"
            if github.get('recommendations'):
                for rec in github['recommendations']:
                    report_text += f"  • {rec}\n"
            report_text += "\n"
        
        if "StackOverflow" in analysis['platforms_analyzed']:
            stackoverflow = analysis['stackoverflow']
            report_text += f"""
STACKOVERFLOW
-------------
Score: {stackoverflow['score']}/100
URL: {stackoverflow['url']}
Status: {'Valid' if stackoverflow['is_valid'] else 'Invalid'}
Top Tags: {', '.join(stackoverflow['demo_stats']['top_tags'])}

Insights:
"""
            if stackoverflow.get('insights'):
                for insight in stackoverflow['insights']:
                    report_text += f"  • {insight['category']}: {insight['status']}\n"
            
            report_text += "\nRecommendations:\n"
            if stackoverflow.get('recommendations'):
                for rec in stackoverflow['recommendations']:
                    report_text += f"  • {rec}\n"
            report_text += "\n"
        
        report_text += """

30-DAY ACTION PLAN
==================

Week 1-2: Foundation
- Complete all profile sections
- Add professional photo
- Update work experience
- List all relevant skills

Week 3-4: Engagement
- Start contributing code/content
- Engage with communities
- Share insights/articles
- Request endorsements

Ongoing Maintenance:
- Maintain regular activity
- Update achievements
- Network actively
- Share learnings

==============================================
Report generated by UtopiaHire - AI Career Architect
Next Steps: Implement high-priority recommendations first
"""
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 Download Text Report",
                data=report_text,
                file_name=f"footprint_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                help="Download comprehensive analysis as text file"
            )
        
        with col2:
            json_report = json.dumps(analysis, indent=2, default=str)
            
            st.download_button(
                label="📊 Download JSON Report",
                data=json_report,
                file_name=f"footprint_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Download structured data for programmatic use"
            )
        
        # Action plan
        st.markdown("---")
        st.markdown("### 📋 30-Day Action Plan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Week 1-2**")
            st.markdown("""
            - Complete all profile sections
            - Add professional photo
            - Update work experience
            - List all relevant skills
            """)
        
        with col2:
            st.markdown("**Week 3-4**")
            st.markdown("""
            - Start contributing code/content
            - Engage with communities
            - Share insights/articles
            - Request endorsements
            """)
        
        with col3:
            st.markdown("**Ongoing**")
            st.markdown("""
            - Maintain regular activity
            - Update achievements
            - Network actively
            - Share learnings
            """)
        
        # API Integration info
        st.markdown("---")
        with st.expander("🔌 API Integration Notice"):
            st.markdown("""
            This demo version provides URL/username validation and basic analysis.
            
            **For full functionality**, integrate with platform APIs:
            
            - **LinkedIn API**: Profile data, connections, posts, endorsements
            - **GitHub API**: Repositories, contributions, stars, followers
            - **StackOverflow API**: Reputation, badges, answers, questions
            
            API integration will provide:
            - Real-time data fetching
            - Detailed metrics and analytics
            - Historical trend analysis
            - Automated monitoring
            
            The current architecture is ready for API integration!
            """)

if __name__ == "__main__":
    main()
