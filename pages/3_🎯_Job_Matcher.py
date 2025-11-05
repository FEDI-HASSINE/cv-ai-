"""
Job Matcher Page
Intelligent job matching based on skills, experience, and regional preferences
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config, COLORS
from src.utils.file_parser import parse_file
from src.core.resume_analyzer import ResumeAnalyzer
from src.core.job_matcher import JobMatcher

st.set_page_config(page_title="Job Matcher", page_icon="🎯", layout="wide")

st.markdown(f"""
    <style>
        .job-card {{
            background-color: #ffffff;
            border: 2px solid {COLORS['primary']};
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
        }}
        .match-score {{
            background: linear-gradient(135deg, {COLORS['success']}, {COLORS['info']});
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
        }}
        .job-title {{
            color: {COLORS['primary']};
            font-size: 1.5rem;
            font-weight: bold;
        }}
        .skill-match {{
            background-color: {COLORS['success']};
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 15px;
            margin: 0.2rem;
            display: inline-block;
            font-size: 0.85rem;
        }}
        .skill-missing {{
            background-color: {COLORS['danger']};
            color: white;
            padding: 0.2rem 0.6rem;
            border-radius: 15px;
            margin: 0.2rem;
            display: inline-block;
            font-size: 0.85rem;
        }}
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("🎯 Job Matcher")
    st.markdown("Find relevant job opportunities tailored to your profile")
    
    # Initialize
    if 'matcher' not in st.session_state:
        st.session_state.matcher = JobMatcher()
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = ResumeAnalyzer()
    
    config = Config()
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 Search Mode")
        
        search_mode = st.radio(
            "Job Search Type",
            ["Dynamic Search (Real Jobs)", "Sample Database"],
            help="Dynamic search finds real jobs from job boards"
        )
        
        st.markdown("---")
        st.markdown("### 🌍 Filter Options")
        
        selected_region = st.selectbox(
            "Target Region",
            options=["All Regions"] + config.REGIONS,
            help="Filter jobs by region"
        )
        
        selected_industry = st.multiselect(
            "Industries",
            options=config.INDUSTRIES,
            help="Filter by industry (optional)"
        )
        
        selected_level = st.multiselect(
            "Job Levels",
            options=config.JOB_LEVELS,
            help="Filter by seniority level (optional)"
        )
        
        num_results = st.slider(
            "Number of results",
            min_value=5,
            max_value=20,
            value=10,
            help="How many job matches to display"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Regional Insights")
        
        if st.button("View Market Insights"):
            st.session_state.show_insights = True
        
        # Dynamic search info
        if search_mode == "Dynamic Search (Real Jobs)":
            st.markdown("---")
            st.info("""
            🌐 **Dynamic Search**
            
            Searches real job boards:
            - LinkedIn Jobs
            - Indeed
            - Glassdoor
            - Google Jobs
            
            Note: May take a few seconds
            """)
    
    # Main content
    st.markdown("---")
    
    # Two modes: Upload resume or manual input
    mode = st.radio(
        "Choose input method:",
        ["Upload Resume", "Manual Input"],
        horizontal=True
    )
    
    candidate_profile = None
    
    if mode == "Upload Resume":
        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=['pdf', 'docx', 'doc', 'txt'],
            help="We'll extract your skills and experience automatically"
        )
        
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            with st.spinner("📖 Analyzing your resume..."):
                parsed = parse_file(uploaded_file.name, file_bytes)
                
                if parsed["status"] == "success":
                    analysis = st.session_state.analyzer.analyze(parsed["text"])
                    st.session_state.analysis = analysis
                    
                    # Create candidate profile
                    candidate_profile = {
                        "technical_skills": analysis["technical_skills"],
                        "soft_skills": analysis["soft_skills"],
                        "experience_years": analysis["experience_years"]
                    }
                    
                    # Display extracted info
                    with st.expander("📋 Extracted Profile", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Technical Skills", len(analysis["technical_skills"]))
                        with col2:
                            st.metric("Soft Skills", len(analysis["soft_skills"]))
                        with col3:
                            st.metric("Experience", f"{analysis['experience_years']} yrs")
    
    else:  # Manual Input
        st.markdown("#### Enter your profile details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tech_skills_input = st.text_area(
                "Technical Skills (comma-separated)",
                placeholder="Python, JavaScript, React, AWS, Docker, SQL",
                help="List your technical skills"
            )
        
        with col2:
            soft_skills_input = st.text_area(
                "Soft Skills (comma-separated)",
                placeholder="Leadership, Communication, Problem Solving",
                help="List your soft skills"
            )
        
        experience_years = st.number_input(
            "Years of Experience",
            min_value=0.0,
            max_value=50.0,
            value=3.0,
            step=0.5
        )
        
        job_title = st.text_input(
            "Desired Job Title (Optional)",
            placeholder="Software Engineer, Data Analyst, etc.",
            help="Add a job title for more targeted search"
        )
        
        if tech_skills_input:
            candidate_profile = {
                "technical_skills": [s.strip() for s in tech_skills_input.split(",") if s.strip()],
                "soft_skills": [s.strip() for s in soft_skills_input.split(",") if s.strip()],
                "experience_years": experience_years,
                "job_title": job_title if job_title else None
            }
    
    # Match jobs
    if candidate_profile:
        st.markdown("---")
        
        if st.button("🔍 Find Matching Jobs", type="primary"):
            use_dynamic = (search_mode == "Dynamic Search (Real Jobs)")
            
            with st.spinner("🔍 Searching for opportunities..." if use_dynamic else "🔍 Matching with job database..."):
                region_filter = None if selected_region == "All Regions" else selected_region
                
                if use_dynamic:
                    # Dynamic search from real job boards
                    matches = st.session_state.matcher.search_real_jobs(
                        candidate_profile=candidate_profile,
                        region=region_filter or "Global",
                        use_dynamic_search=True,
                        max_results=num_results
                    )
                else:
                    # Use sample database
                    matches = st.session_state.matcher.match_jobs(
                        candidate_profile=candidate_profile,
                        region=region_filter,
                        top_n=num_results
                    )
                
                st.session_state.matches = matches
                st.session_state.search_mode = search_mode
    
    # Display matches
    if 'matches' in st.session_state:
        matches = st.session_state.matches
        search_mode_used = st.session_state.get('search_mode', 'Sample Database')
        
        st.markdown("---")
        st.markdown(f"## 💼 Found {len(matches)} Matching Jobs")
        
        if search_mode_used == "Dynamic Search (Real Jobs)":
            st.info("🌐 **Live Results** - Jobs found from real job boards with direct application links")
        
        if not matches:
            st.warning("No jobs found matching your criteria. Try adjusting filters.")
        else:
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Jobs Found", len(matches))
            with col2:
                avg_match = sum(job.get('match_percentage', 0) for job in matches) / len(matches)
                st.metric("Average Match", f"{int(avg_match)}%")
            with col3:
                high_matches = sum(1 for job in matches if job.get('match_percentage', 0) >= 70)
                st.metric("High Matches (≥70%)", high_matches)
            with col4:
                remote_jobs = sum(1 for job in matches if job.get('remote', False) or 'remote' in job.get('title', '').lower())
                st.metric("Remote Jobs", remote_jobs)
            
            st.markdown("---")
            
            # Jobs Table View
            st.markdown("### 📊 Jobs Table")
            
            import pandas as pd
            
            # Prepare data for table
            table_data = []
            for idx, job in enumerate(matches, 1):
                match_percent = job.get('match_percentage', 0)
                
                # Create clickable link
                job_url = job.get('url', '#')
                if job_url and job_url != '#':
                    job_link = f'<a href="{job_url}" target="_blank">🔗 Apply</a>'
                else:
                    job_link = 'N/A'
                
                table_data.append({
                    '#': idx,
                    'Job Title': job['title'],
                    'Company': job['company'],
                    'Location': job['location'],
                    'Match': f"{match_percent}%",
                    'Source': job.get('source', job.get('region', 'Database')),
                    'Apply Link': job_url if job_url != '#' else 'N/A'
                })
            
            df = pd.DataFrame(table_data)
            
            # Display table with clickable links
            st.markdown("""
            <style>
            .job-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .job-table th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: bold;
            }
            .job-table td {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            .job-table tr:hover {
                background-color: #f5f5f5;
            }
            .match-high {
                color: #28a745;
                font-weight: bold;
            }
            .match-medium {
                color: #ffc107;
                font-weight: bold;
            }
            .match-low {
                color: #dc3545;
                font-weight: bold;
            }
            .apply-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 6px 16px;
                border-radius: 20px;
                text-decoration: none;
                font-weight: bold;
                display: inline-block;
            }
            .apply-btn:hover {
                opacity: 0.8;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Build HTML table
            html_table = '<table class="job-table"><thead><tr>'
            html_table += '<th>#</th><th>Job Title</th><th>Company</th><th>Location</th><th>Match Score</th><th>Source</th><th>Apply</th>'
            html_table += '</tr></thead><tbody>'
            
            for idx, job in enumerate(matches, 1):
                match_percent = job.get('match_percentage', 0)
                
                # Color code match percentage
                if match_percent >= 70:
                    match_class = 'match-high'
                elif match_percent >= 50:
                    match_class = 'match-medium'
                else:
                    match_class = 'match-low'
                
                job_url = job.get('url', '#')
                apply_link = f'<a href="{job_url}" target="_blank" class="apply-btn">🔗 Apply Now</a>' if job_url != '#' else 'N/A'
                
                html_table += f'''
                <tr>
                    <td>{idx}</td>
                    <td><strong>{job["title"]}</strong></td>
                    <td>{job["company"]}</td>
                    <td>{job["location"]}</td>
                    <td class="{match_class}">{match_percent}%</td>
                    <td>{job.get('source', job.get('region', 'Database'))}</td>
                    <td>{apply_link}</td>
                </tr>
                '''
            
            html_table += '</tbody></table>'
            
            st.markdown(html_table, unsafe_allow_html=True)
            
            # Download table as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Jobs Table (CSV)",
                data=csv,
                file_name=f"job_matches_table_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Download job matches as CSV file"
            )
            
            st.markdown("---")
            
            # Detailed Analysis Section
            st.markdown("### 🔍 Detailed Job Analysis & Enhancement Suggestions")
            
            st.info("💡 **Click on each job to see detailed match analysis and personalized recommendations**")
            
            # Sort options
            sort_by = st.selectbox(
                "Sort by:",
                ["Match Score (High to Low)", "Experience Required", "Company Name"],
                index=0
            )
            
            # Display jobs with detailed analysis
            for idx, job in enumerate(matches, 1):
                # Apply filters (only for sample database)
                if search_mode_used == "Sample Database":
                    if selected_industry and job.get('industry') and job['industry'] not in selected_industry:
                        continue
                    if selected_level and job.get('level') and job['level'] not in selected_level:
                        continue
                
                match_percent = job.get('match_percentage', 0)
                details = job.get('match_details', {})
                
                # Match status badge
                if match_percent >= 80:
                    match_status = "🟢 Excellent Match"
                    match_color = "#28a745"
                elif match_percent >= 60:
                    match_status = "🟡 Good Match"
                    match_color = "#ffc107"
                elif match_percent >= 40:
                    match_status = "🟠 Fair Match"
                    match_color = "#fd7e14"
                else:
                    match_status = "🔴 Low Match"
                    match_color = "#dc3545"
                
                # Check if it's a real job with URL
                has_url = 'url' in job and job['url']
                job_source = job.get('source', 'Database')
                
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div class="job-title">{idx}. {job['title']}</div>
                            <div style="color: #666; margin: 0.5rem 0;">
                                🏢 {job['company']} | 📍 {job['location']} | {'🌍 ' + job.get('region', 'Global') if job.get('region') else '🌐 ' + job_source}
                            </div>
                        </div>
                        <div class="match-score">
                            {match_percent}% Match
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Job Card Header with enhanced styling
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {match_color}15 0%, {match_color}05 100%); 
                            border-left: 5px solid {match_color}; 
                            padding: 20px; 
                            border-radius: 10px; 
                            margin: 15px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0; color: #333;">{idx}. {job['title']}</h3>
                            <p style="color: #666; margin: 8px 0 0 0;">
                                🏢 {job['company']} | 📍 {job['location']} | {match_status}
                            </p>
                        </div>
                        <div style="background: {match_color}; color: white; padding: 10px 20px; border-radius: 25px; font-size: 1.3em; font-weight: bold;">
                            {match_percent}%
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick Apply Button for jobs with URLs
                has_url = 'url' in job and job['url'] and job['url'] != '#'
                job_source = job.get('source', 'Database')
                
                if has_url:
                    col_btn1, col_btn2 = st.columns([1, 4])
                    with col_btn1:
                        st.link_button(
                            "🚀 Apply Now",
                            job['url'],
                            help=f"Open job listing on {job_source}",
                            use_container_width=True,
                            type="primary"
                        )
                
                # Detailed Analysis Expander
                with st.expander(f"📊 View Detailed Analysis & Enhancement Suggestions", expanded=False):
                    
                    # Three-column layout for detailed analysis
                    col1, col2, col3 = st.columns([2, 2, 2])
                    
                    with col1:
                        st.markdown("#### 📋 Job Information")
                        if job.get('industry'):
                            st.write(f"**Industry:** {job['industry']}")
                        if job.get('level'):
                            st.write(f"**Level:** {job['level']}")
                        if job.get('experience_years'):
                            st.write(f"**Experience Required:** {job['experience_years']} years")
                        if job.get('salary_range'):
                            st.write(f"**Salary Range:** {job['salary_range']}")
                        if 'remote' in job:
                            st.write(f"**Remote Work:** {'✅ Yes' if job['remote'] else '❌ Office Only'}")
                        
                        if job.get('description'):
                            st.markdown("**Job Description:**")
                            st.info(job['description'])
                    
                    with col2:
                        st.markdown("#### 🎯 Match Breakdown")
                        
                        # Visual match analysis
                        if details:
                            if 'skill_score' in details:
                                skill_pct = int(details['skill_score'] * 100)
                                st.progress(skill_pct / 100)
                                st.write(f"**Skills Match:** {skill_pct}%")
                            
                            if 'experience_score' in details:
                                exp_pct = int(details['experience_score'] * 100)
                                st.progress(exp_pct / 100)
                                st.write(f"**Experience Match:** {exp_pct}%")
                            
                            if 'level_score' in details:
                                level_pct = int(details['level_score'] * 100)
                                st.progress(level_pct / 100)
                                st.write(f"**Level Match:** {level_pct}%")
                        
                        # Skills analysis
                        if details and 'required_skills_total' in details:
                            st.markdown("---")
                            st.markdown(f"**Required Skills: {details['required_skills_matched']}/{details['required_skills_total']}**")
                            
                            for skill in job.get('required_skills', []):
                                if skill in candidate_profile['technical_skills'] + candidate_profile['soft_skills']:
                                    st.markdown(f'<span class="skill-match">✓ {skill}</span>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<span class="skill-missing">✗ {skill} (Missing)</span>', unsafe_allow_html=True)
                        
                        elif details and 'matched_skills' in details:
                            st.markdown("---")
                            st.markdown(f"**Your Skills Matched: {len(details['matched_skills'])}/{details['total_candidate_skills']}**")
                            if details['matched_skills']:
                                for skill in details['matched_skills'][:10]:
                                    st.success(f"✓ {skill}")
                    
                    with col3:
                        st.markdown("#### 💡 Enhancement Suggestions")
                        
                        # Generate personalized suggestions
                        suggestions = []
                        
                        # Skill-based suggestions
                        if details and details.get('missing_skills'):
                            suggestions.append({
                                'priority': 'High',
                                'category': 'Skills Gap',
                                'suggestion': f"Learn these missing skills: {', '.join(details['missing_skills'][:3])}",
                                'impact': 'Increase match score by 15-20%',
                                'action': '📚 Take online courses or tutorials'
                            })
                        
                        # Experience suggestions
                        if job.get('experience_years', 0) > candidate_profile.get('experience_years', 0):
                            exp_gap = job['experience_years'] - candidate_profile['experience_years']
                            suggestions.append({
                                'priority': 'Medium',
                                'category': 'Experience',
                                'suggestion': f'Build {exp_gap} more years of experience',
                                'impact': 'Meet experience requirements',
                                'action': '💼 Consider internships or junior positions first'
                            })
                        
                        # Match score suggestions
                        if match_percent < 60:
                            suggestions.append({
                                'priority': 'High',
                                'category': 'Profile Optimization',
                                'suggestion': 'Update your resume with relevant keywords from job description',
                                'impact': 'Improve ATS compatibility by 25%',
                                'action': '📝 Use Resume Rewriter feature'
                            })
                        
                        # Remote work suggestion
                        if not job.get('remote') and 'remote' not in job.get('title', '').lower():
                            suggestions.append({
                                'priority': 'Low',
                                'category': 'Location',
                                'suggestion': 'This is an office-based position',
                                'impact': 'Consider relocation or search remote jobs',
                                'action': '🌍 Filter by remote positions'
                            })
                        
                        # Certification suggestions based on job level
                        if job.get('level') in ['Senior', 'Lead']:
                            suggestions.append({
                                'priority': 'Medium',
                                'category': 'Certifications',
                                'suggestion': 'Get industry-recognized certifications',
                                'impact': 'Stand out among senior candidates',
                                'action': '🏆 AWS, Azure, or Google Cloud certifications'
                            })
                        
                        # Display suggestions
                        if suggestions:
                            for sug in suggestions:
                                priority_colors = {
                                    'High': '#dc3545',
                                    'Medium': '#ffc107',
                                    'Low': '#17a2b8'
                                }
                                color = priority_colors.get(sug['priority'], '#6c757d')
                                
                                st.markdown(f"""
                                <div style="border-left: 4px solid {color}; padding: 12px; margin: 10px 0; background-color: #f8f9fa; border-radius: 5px;">
                                    <div style="color: {color}; font-weight: bold; margin-bottom: 5px;">
                                        {sug['priority']} Priority - {sug['category']}
                                    </div>
                                    <div style="font-size: 0.95em; margin-bottom: 5px;">
                                        <strong>💡 {sug['suggestion']}</strong>
                                    </div>
                                    <div style="font-size: 0.85em; color: #666; margin-bottom: 3px;">
                                        📈 Impact: {sug['impact']}
                                    </div>
                                    <div style="font-size: 0.85em; color: #555;">
                                        ✅ Action: {sug['action']}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.success("🎉 Great match! No major improvements needed.")
                        
                        # Application readiness score
                        st.markdown("---")
                        readiness_score = match_percent
                        if readiness_score >= 80:
                            readiness_status = "🟢 Ready to Apply"
                            readiness_color = "#28a745"
                        elif readiness_score >= 60:
                            readiness_status = "🟡 Improve & Apply"
                            readiness_color = "#ffc107"
                        else:
                            readiness_status = "🔴 Need More Preparation"
                            readiness_color = "#dc3545"
                        
                        st.markdown(f"""
                        <div style="text-align: center; padding: 15px; background: {readiness_color}15; border: 2px solid {readiness_color}; border-radius: 10px;">
                            <div style="font-size: 1.2em; font-weight: bold; color: {readiness_color};">
                                {readiness_status}
                            </div>
                            <div style="margin-top: 8px; font-size: 0.9em; color: #666;">
                                Application Readiness: {readiness_score}%
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Direct application link
                        if has_url:
                            st.markdown("---")
                            st.markdown(f"**🔗 Apply on {job_source}:**")
                            st.link_button(
                                f"Open on {job_source}",
                                job['url'],
                                use_container_width=True
                            )
            
            # Skill development recommendations
            st.markdown("---")
            st.markdown("### 📚 Skill Development Recommendations")
            
            region_for_rec = None if selected_region == "All Regions" else selected_region
            recommendations = st.session_state.matcher.recommend_skill_development(
                candidate_profile['technical_skills'] + candidate_profile['soft_skills'],
                target_region=region_for_rec
            )
            
            if recommendations:
                st.info(f"Top {len(recommendations[:5])} skills to learn for better job matches:")
                
                for rec in recommendations[:5]:
                    priority_color = {
                        "High": COLORS['danger'],
                        "Medium": COLORS['warning'],
                        "Low": COLORS['info']
                    }.get(rec['priority'], COLORS['info'])
                    
                    st.markdown(f"""
                    <div style="border-left: 4px solid {priority_color}; padding: 0.5rem 1rem; margin: 0.5rem 0; background-color: #f8f9fa;">
                        <strong>{rec['skill']}</strong> ({rec['priority']} Priority)<br>
                        <small>{rec['reason']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Download job matches report
            st.markdown("---")
            st.markdown("### 📥 Download Job Matches Report")
            
            # Generate report
            report_text = f"""
UtopiaHire - Job Matching Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================

CANDIDATE PROFILE
-----------------
Technical Skills: {', '.join(candidate_profile['technical_skills'])}
Soft Skills: {', '.join(candidate_profile['soft_skills'])}
Experience: {candidate_profile['experience_years']} years

MATCHED JOBS ({len(matches)})
============
"""
            
            for idx, job in enumerate(matches, 1):
                # Safe access to optional fields
                region = job.get('region', job.get('source', 'N/A'))
                industry = job.get('industry', 'N/A')
                level = job.get('level', 'N/A')
                experience_years = job.get('experience_years', 'N/A')
                salary_range = job.get('salary_range', 'N/A')
                remote = job.get('remote', False)
                required_skills = job.get('required_skills', [])
                
                report_text += f"""
{idx}. {job['title']} at {job['company']}
   Match Score: {job.get('match_percentage', 'N/A')}%
   Location: {job['location']} ({region})
   Industry: {industry} | Level: {level}
   Experience Required: {experience_years} years
   Salary Range: {salary_range}
   Remote: {'Yes' if remote else 'No'}
   Apply Link: {job.get('url', 'N/A')}
   
   Required Skills: {', '.join(required_skills) if required_skills else 'See job description'}
   Skills Matched: {job['match_details'].get('required_skills_matched', 'N/A')}/{job['match_details'].get('required_skills_total', 'N/A')}
   Missing Skills: {', '.join(job['match_details'].get('missing_skills', [])) if job['match_details'].get('missing_skills') else 'None'}
   
   Description: {job.get('description', 'See job link for full description')}
   Source: {job.get('source', 'Database')}
   
"""
            
            report_text += f"""

SKILL DEVELOPMENT RECOMMENDATIONS
==================================
"""
            for rec in recommendations[:10]:
                report_text += f"""
• {rec['skill']} ({rec['priority']} Priority)
  {rec['reason']}
"""
            
            report_text += """

================================
Report generated by UtopiaHire - AI Career Architect
Next Steps: Apply to high-match jobs and develop missing skills
"""
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 Download Text Report",
                    data=report_text,
                    file_name=f"job_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    help="Download job matches as text file"
                )
            
            with col2:
                json_report = json.dumps({
                    "candidate_profile": candidate_profile,
                    "matches": matches,
                    "recommendations": recommendations
                }, indent=2, default=str)
                
                st.download_button(
                    label="📊 Download JSON Report",
                    data=json_report,
                    file_name=f"job_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    help="Download structured data for programmatic use"
                )
    
    # Regional insights
    if 'show_insights' in st.session_state and st.session_state.show_insights:
        st.markdown("---")
        st.markdown("## 📊 Regional Market Insights")
        
        insight_region = st.selectbox(
            "Select region for insights:",
            options=config.REGIONS
        )
        
        insights = st.session_state.matcher.get_regional_insights(insight_region)
        
        if "error" not in insights:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Jobs", insights['total_jobs'])
            with col2:
                st.metric("Avg Experience Required", f"{insights['avg_experience_required']} yrs")
            with col3:
                st.metric("Top Industries", len(insights['top_industries']))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top Industries**")
                for industry, count in insights['top_industries'].items():
                    st.write(f"• {industry}: {count} jobs")
            
            with col2:
                st.markdown("**Top Skills in Demand**")
                for skill, count in list(insights['top_skills'].items())[:10]:
                    st.write(f"• {skill}: {count} mentions")

if __name__ == "__main__":
    main()
