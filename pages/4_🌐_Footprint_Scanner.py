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

st.markdown(
    f"""
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
    """,
    unsafe_allow_html=True,
)


def main():
    st.title("🌐 Digital Footprint Scanner")
    st.markdown("Analyze your professional online presence across major platforms")

    if "scanner" not in st.session_state:
        st.session_state.scanner = FootprintScanner()

    Config()  # not used directly but keeps config in sync if needed

    # Sidebar info
    with st.sidebar:
        st.markdown("### 🔍 What We Analyze")
        st.markdown(
            """
            **LinkedIn**: Profile completeness, network, engagement, endorsements

            **GitHub**: Repos, contributions, code quality, community

            **StackOverflow**: Reputation, badges, answers, tags
            """
        )

    # Inputs
    st.markdown("---")
    st.markdown("### 📝 Enter Your Profile URLs")
    c1, c2 = st.columns(2)
    with c1:
        linkedin_url = st.text_input(
            "🔗 LinkedIn Profile URL",
            placeholder="https://linkedin.com/in/your-profile",
        )
        github_username = st.text_input(
            "💻 GitHub Username",
            placeholder="yourusername (URL accepted)",
            help="You can paste your profile URL; we'll extract the username.",
        )
    with c2:
        stackoverflow_url = st.text_input(
            "📚 StackOverflow Profile URL",
            placeholder="https://stackoverflow.com/users/12345/your-name",
        )

    st.markdown("---")
    if st.button("🔍 Scan Digital Footprint", type="primary"):
        if not any([linkedin_url, github_username, stackoverflow_url]):
            st.error("Please provide at least one profile URL/username")
        else:
            with st.spinner("🌐 Scanning your digital footprint... This may take a moment."):
                analysis = st.session_state.scanner.analyze_footprint(
                    linkedin_url=linkedin_url or None,
                    github_username=github_username or None,
                    stackoverflow_url=stackoverflow_url or None,
                )
                st.session_state.footprint_analysis = analysis

    # Results
    if "footprint_analysis" in st.session_state:
        analysis = st.session_state.footprint_analysis
        summary = st.session_state.scanner.get_summary(analysis)
        overall_score = summary.get("overall_score", 0)
        platforms_analyzed = summary.get("platforms_analyzed", [])

        st.markdown("---")
        st.markdown("## 📊 Footprint Analysis Results")
        _, mid, _ = st.columns([2, 1, 2])
        with mid:
            st.markdown(
                f"""
                <div style=\"text-align: center; padding: 2rem;\">
                    <div style=\"font-size: 1.2rem; color: #666; margin-bottom: 1rem;\">Overall Score</div>
                    <div class=\"score-badge\">{overall_score}/100</div>
                    <div style=\"margin-top: 1rem; font-size: 0.9rem; color: #666;\">
                        Based on {len(platforms_analyzed)} platform(s)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")
        tabs = ["📋 Overview", "🏆 Strengths", "📈 Improvements", "💡 Recommendations"]
        if "LinkedIn" in platforms_analyzed:
            tabs.append("🔗 LinkedIn")
        if "GitHub" in platforms_analyzed:
            tabs.append("💻 GitHub")
        if "StackOverflow" in platforms_analyzed:
            tabs.append("📚 StackOverflow")
        pages = st.tabs(tabs)

        # Overview
        with pages[0]:
            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown("**Platforms Analyzed**")
                for p in platforms_analyzed:
                    st.success(f"✅ {p}")
                missing = [p for p in ["LinkedIn", "GitHub", "StackOverflow"] if p not in platforms_analyzed]
                if missing:
                    st.markdown("**Not Analyzed**")
                    for p in missing:
                        st.warning(f"❌ {p}")
            with cc2:
                st.markdown("**Quick Stats**")
                st.metric("Platforms Active", len(platforms_analyzed))
                st.metric("Overall Score", f"{overall_score}/100")
                st.metric("Key Strengths", len(analysis.get("strengths", [])))
                st.metric("Areas to Improve", len(analysis.get("areas_for_improvement", [])))

        # Strengths
        with pages[1]:
            st.markdown("### 🏆 Your Strengths")
            if analysis.get("strengths"):
                for s in analysis.get("strengths", []):
                    st.markdown(f"<div class=\"strength\">✅ {s}</div>", unsafe_allow_html=True)
            else:
                st.info("Start building your online presence to develop strengths")

        # Improvements
        with pages[2]:
            st.markdown("### 📈 Areas for Improvement")
            if analysis.get("areas_for_improvement"):
                for imp in analysis.get("areas_for_improvement", []):
                    st.markdown(f"<div class=\"improvement\">⚠️ {imp}</div>", unsafe_allow_html=True)
            else:
                st.success("Great! No major areas for improvement identified")

        # Recommendations
        with pages[3]:
            st.markdown("### 💡 Personalized Recommendations")
            recs = analysis.get("recommendations", [])
            if recs:
                for rec in recs:
                    if isinstance(rec, dict):
                        priority = rec.get("priority", "Medium")
                        recommendation_text = rec.get("recommendation", "")
                        impact_text = rec.get("impact", "")
                    else:
                        priority = "Medium"
                        recommendation_text = str(rec)
                        impact_text = ""
                    color = {
                        "Critical": COLORS["danger"],
                        "High": COLORS["warning"],
                        "Medium": COLORS["info"],
                        "Low": COLORS["primary"],
                    }.get(priority, COLORS["info"])
                    st.markdown(
                        f"<div style=\"border-left: 4px solid {color}; padding: 1rem; margin: 0.5rem 0; background-color: #f8f9fa;\"><strong>{priority} Priority</strong><br>{recommendation_text}<br><small style=\"color:#666;\"><em>Impact: {impact_text}</em></small></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("Keep maintaining your current online presence!")

        # LinkedIn
        idx = 4
        if "LinkedIn" in platforms_analyzed:
            with pages[idx]:
                li = analysis.get("linkedin", {})
                st.markdown("### 🔗 LinkedIn Analysis")
                st.markdown(
                    f"<div class=\"platform-card\"><h4>Profile Score: {li.get('score',0)}/100</h4><p><strong>URL:</strong> {li.get('url','')}</p><p><strong>Status:</strong> {'✅ Valid' if li.get('is_valid', False) else '❌ Invalid'}</p></div>",
                    unsafe_allow_html=True,
                )
                if li.get("insights"):
                    st.markdown("**Insights:**")
                    for ins in li.get("insights", []):
                        st.markdown(
                            f"- **{ins.get('category','')}**: {ins.get('status','')}\n  <br><small>{ins.get('description','')}</small>",
                            unsafe_allow_html=True,
                        )
                if li.get("recommendations"):
                    st.markdown("**Recommendations:**")
                    for r in li.get("recommendations", []):
                        st.markdown(f"• {r}")
            idx += 1

        # GitHub
        if "GitHub" in platforms_analyzed:
            with pages[idx]:
                gh = analysis.get("github", {})
                st.markdown("### 💻 GitHub Analysis")
                st.markdown(
                    f"<div class=\"platform-card\"><h4>Profile Score: {gh.get('score',0)}/100</h4><p><strong>Username:</strong> {gh.get('username','')}</p><p><strong>Profile:</strong> <a href=\"{gh.get('demo_stats',{}).get('profile_url','')}\" target=\"_blank\">{gh.get('demo_stats',{}).get('profile_url','')}</a></p></div>",
                    unsafe_allow_html=True,
                )
                st.markdown("**Demo Stats** *(Full stats available with API integration)*")
                dc1, dc2 = st.columns(2)
                with dc1:
                    st.write(
                        f"**Popular Languages:** {', '.join(gh.get('demo_stats',{}).get('popular_languages', []))}"
                    )
                with dc2:
                    st.info(
                        "Connect GitHub API to get:\n- Public repos count\n- Followers\n- Contribution graph\n- Stars & Forks"
                    )
                if gh.get("insights"):
                    st.markdown("**Insights:**")
                    for ins in gh.get("insights", []):
                        st.markdown(f"- **{ins.get('category','')}**: {ins.get('status','')}")
                if gh.get("recommendations"):
                    st.markdown("**Recommendations:**")
                    for r in gh.get("recommendations", []):
                        st.markdown(f"• {r}")
            idx += 1

        # StackOverflow
        if "StackOverflow" in platforms_analyzed and idx < len(pages):
            with pages[idx]:
                so = analysis.get("stackoverflow", {})
                st.markdown("### 📚 StackOverflow Analysis")
                st.markdown(
                    f"<div class=\"platform-card\"><h4>Profile Score: {so.get('score',0)}/100</h4><p><strong>URL:</strong> {so.get('url','')}</p><p><strong>Status:</strong> {'✅ Valid' if so.get('is_valid', False) else '❌ Invalid'}</p></div>",
                    unsafe_allow_html=True,
                )
                st.markdown("**Demo Stats** *(Full stats available with API integration)*")
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.write(
                        f"**Top Tags:** {', '.join(so.get('demo_stats',{}).get('top_tags', []))}"
                    )
                with sc2:
                    st.info(
                        "Connect StackOverflow API to get:\n- Reputation score\n- Badges earned\n- Answers & Questions\n- Accept rate"
                    )
                if so.get("insights"):
                    st.markdown("**Insights:**")
                    for ins in so.get("insights", []):
                        st.markdown(f"- **{ins.get('category','')}**: {ins.get('status','')}")
                if so.get("recommendations"):
                    st.markdown("**Recommendations:**")
                    for r in so.get("recommendations", []):
                        st.markdown(f"• {r}")

        # Download report
        st.markdown("---")
        st.markdown("### 📥 Download Footprint Analysis Report")
        report_text = f"""
UtopiaHire - Digital Footprint Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==============================================

OVERALL ASSESSMENT
------------------
Overall Score: {overall_score}/100
Platforms Analyzed: {', '.join(platforms_analyzed)}
Total Platforms: {len(platforms_analyzed)}

KEY STRENGTHS ({len(analysis.get('strengths', []))})
============
"""
        if analysis.get("strengths"):
            for i, s in enumerate(analysis.get("strengths", []), 1):
                report_text += f"{i}. {s}\n"
        else:
            report_text += "No major strengths identified yet\n"

        report_text += f"""

AREAS FOR IMPROVEMENT ({len(analysis.get('areas_for_improvement', []))})
=====================
"""
        if analysis.get("areas_for_improvement"):
            for i, imp in enumerate(analysis.get("areas_for_improvement", []), 1):
                report_text += f"{i}. {imp}\n"
        else:
            report_text += "No major improvements needed\n"

        report_text += f"""

RECOMMENDATIONS ({len(analysis.get('recommendations', []))})
===============
"""
        recs = analysis.get("recommendations", [])
        if recs:
            for rec in recs:
                if isinstance(rec, dict):
                    pri = rec.get('priority', '')
                    rec_txt = rec.get('recommendation', '')
                    imp = rec.get('impact', '')
                else:
                    pri = 'Medium'
                    rec_txt = str(rec)
                    imp = ''
                report_text += (
                    f"\nPriority: {pri}\nRecommendation: {rec_txt}\nExpected Impact: {imp}\n---\n"
                )
        else:
            report_text += "Keep maintaining your current online presence!\n"

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📄 Download Text Report",
                data=report_text,
                file_name=f"footprint_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
            )
        with col2:
            json_report = json.dumps(analysis, indent=2, default=str)
            st.download_button(
                label="📊 Download JSON Report",
                data=json_report,
                file_name=f"footprint_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )

    # Footer note
    st.markdown("---")
    with st.expander("🔌 API Integration Notice"):
        st.markdown(
            """
            This demo provides validation and structured analysis. For full data depth, connect platform APIs.
            """
        )


if __name__ == "__main__":
    main()
