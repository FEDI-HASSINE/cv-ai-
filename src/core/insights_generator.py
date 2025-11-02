"""
Insights Generator
Generates personalized insights, recommendations, and 30-day action plans.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class InsightsGenerator:
    """
    Generates actionable insights and recommendations based on footprint analysis.
    """
    
    def __init__(self):
        """Initialize insights generator."""
        pass
    
    def generate_insights(
        self,
        scores: Dict[str, Any],
        github_data: Dict[str, Any] = None,
        stackoverflow_data: Dict[str, Any] = None,
        linkedin_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights and recommendations.
        
        Args:
            scores: Score data from ScoringEngine
            github_data: Raw GitHub data
            stackoverflow_data: Raw StackOverflow data
            linkedin_data: Raw LinkedIn data
            
        Returns:
            Dictionary containing insights, recommendations, and action plan
        """
        insights = {
            "strengths": [],
            "areas_for_improvement": [],
            "recommendations": [],
            "platform_insights": {},
            "30_day_plan": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # Analyze each platform
        if github_data and github_data.get("success"):
            github_insights = self._analyze_github(scores.get("breakdown", {}).get("github", {}), github_data)
            insights["platform_insights"]["github"] = github_insights
            insights["strengths"].extend(github_insights.get("strengths", []))
            insights["areas_for_improvement"].extend(github_insights.get("improvements", []))
        
        if stackoverflow_data and stackoverflow_data.get("success"):
            so_insights = self._analyze_stackoverflow(scores.get("breakdown", {}).get("stackoverflow", {}), stackoverflow_data)
            insights["platform_insights"]["stackoverflow"] = so_insights
            insights["strengths"].extend(so_insights.get("strengths", []))
            insights["areas_for_improvement"].extend(so_insights.get("improvements", []))
        
        if linkedin_data and linkedin_data.get("success"):
            linkedin_insights = self._analyze_linkedin(scores.get("breakdown", {}).get("linkedin", {}), linkedin_data)
            insights["platform_insights"]["linkedin"] = linkedin_insights
            insights["strengths"].extend(linkedin_insights.get("strengths", []))
            insights["areas_for_improvement"].extend(linkedin_insights.get("improvements", []))
        
        # Generate general recommendations
        insights["recommendations"] = self._generate_recommendations(scores, insights)
        
        # Generate 30-day action plan
        insights["30_day_plan"] = self._generate_action_plan(scores, insights)
        
        return insights
    
    def _analyze_github(self, breakdown: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze GitHub presence and generate insights."""
        strengths = []
        improvements = []
        tips = []
        
        stats = data.get("statistics", {})
        repos = data.get("repositories", {})
        languages = data.get("languages", {})
        
        # Analyze repos
        repos_score = breakdown.get("repos", {}).get("score", 0)
        public_repos = stats.get("public_repos", 0)
        
        if repos_score >= 15:
            strengths.append(f"Strong repository portfolio with {public_repos} public repositories")
        elif public_repos < 5:
            improvements.append("Limited number of public repositories")
            tips.append("Create more public repositories to showcase your work")
        
        # Analyze stars
        stars_score = breakdown.get("stars", {}).get("score", 0)
        total_stars = stats.get("total_stars", 0)
        
        if stars_score >= 20:
            strengths.append(f"Excellent community recognition with {total_stars} stars")
        elif total_stars < 10:
            improvements.append("Limited community engagement (stars)")
            tips.append("Contribute to popular projects and create useful tools to gain stars")
        
        # Analyze activity
        activity_score = breakdown.get("activity", {}).get("score", 0)
        
        if activity_score >= 15:
            strengths.append("Consistently active on GitHub")
        elif activity_score < 8:
            improvements.append("Low recent activity on GitHub")
            tips.append("Maintain regular commits and update repositories frequently")
        
        # Analyze language diversity
        lang_count = len(languages)
        
        if lang_count >= 5:
            strengths.append(f"Versatile developer with {lang_count} programming languages")
        elif lang_count < 3:
            improvements.append("Limited programming language diversity")
            tips.append("Explore new programming languages and technologies")
        
        # Analyze followers
        followers = stats.get("followers", 0)
        
        if followers < 10:
            tips.append("Engage with the community to increase your followers")
        
        return {
            "strengths": strengths,
            "improvements": improvements,
            "tips": tips,
            "key_metrics": {
                "repos": public_repos,
                "stars": total_stars,
                "followers": followers,
                "languages": lang_count
            }
        }
    
    def _analyze_stackoverflow(self, breakdown: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze StackOverflow presence and generate insights."""
        strengths = []
        improvements = []
        tips = []
        
        reputation = data.get("reputation", {})
        badges = data.get("badges", {})
        activity = data.get("activity", {})
        
        # Analyze reputation
        rep_score_value = reputation.get("score", 0)
        
        if rep_score_value >= 1000:
            strengths.append(f"Strong reputation on StackOverflow ({rep_score_value:,} points)")
        elif rep_score_value >= 100:
            strengths.append(f"Growing presence on StackOverflow ({rep_score_value} reputation)")
        else:
            improvements.append("Low StackOverflow reputation")
            tips.append("Answer more questions in your areas of expertise")
        
        # Analyze badges
        gold = badges.get("gold", 0)
        silver = badges.get("silver", 0)
        total_badges = badges.get("total", 0)
        
        if gold > 0:
            strengths.append(f"Earned {gold} gold badge(s) - recognized expert")
        
        if total_badges >= 10:
            strengths.append(f"Active contributor with {total_badges} badges")
        elif total_badges < 3:
            improvements.append("Few badges earned")
            tips.append("Work towards earning badges by consistent participation")
        
        # Analyze answers
        answers = activity.get("answers", {})
        answer_count = answers.get("count", 0)
        accepted = answers.get("accepted", 0)
        
        if answer_count >= 50:
            strengths.append(f"Prolific answerer with {answer_count} answers")
        elif answer_count < 10:
            improvements.append("Limited answer contributions")
            tips.append("Answer questions regularly to build reputation")
        
        if answer_count > 0:
            acceptance_rate = (accepted / answer_count) * 100
            if acceptance_rate >= 50:
                strengths.append(f"High answer acceptance rate ({acceptance_rate:.1f}%)")
            elif acceptance_rate < 20:
                improvements.append("Low answer acceptance rate")
                tips.append("Focus on providing comprehensive, helpful answers")
        
        # Analyze questions
        questions = activity.get("questions", {})
        question_count = questions.get("count", 0)
        
        if question_count > 20:
            tips.append("Balance asking questions with providing answers")
        
        return {
            "strengths": strengths,
            "improvements": improvements,
            "tips": tips,
            "key_metrics": {
                "reputation": rep_score_value,
                "badges": total_badges,
                "answers": answer_count,
                "questions": question_count
            }
        }
    
    def _analyze_linkedin(self, breakdown: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze LinkedIn presence and generate insights."""
        strengths = []
        improvements = []
        tips = []
        
        profile = data.get("profile", {})
        experience = data.get("experience", [])
        education = data.get("education", [])
        skills = data.get("skills", [])
        
        # Analyze profile completeness
        completeness = breakdown.get("profile_completeness", {})
        filled = completeness.get("filled_fields", 0)
        total = completeness.get("total_fields", 4)
        
        if filled == total:
            strengths.append("Complete LinkedIn profile")
        elif filled < total / 2:
            improvements.append("Incomplete LinkedIn profile")
            tips.append("Complete all profile sections (headline, summary, location)")
        
        # Analyze experience
        exp_count = len(experience)
        
        if exp_count >= 3:
            strengths.append(f"Detailed work history with {exp_count} positions")
        elif exp_count < 2:
            improvements.append("Limited work experience listed")
            tips.append("Add all relevant work experiences to your profile")
        
        # Analyze education
        edu_count = len(education)
        
        if edu_count >= 1:
            strengths.append("Education background documented")
        else:
            improvements.append("No education information")
            tips.append("Add your educational qualifications")
        
        # Analyze skills
        skill_count = len(skills)
        
        if skill_count >= 10:
            strengths.append(f"Comprehensive skills list with {skill_count} skills")
        elif skill_count < 5:
            improvements.append("Limited skills listed")
            tips.append("Add more relevant skills to your profile (aim for 10+)")
        
        # General LinkedIn tips
        if profile.get("about") and len(profile.get("about", "")) < 100:
            tips.append("Expand your About section with more details about your expertise")
        
        return {
            "strengths": strengths,
            "improvements": improvements,
            "tips": tips,
            "key_metrics": {
                "completeness": f"{filled}/{total}",
                "experience": exp_count,
                "education": edu_count,
                "skills": skill_count
            }
        }
    
    def _generate_recommendations(self, scores: Dict[str, Any], insights: Dict[str, Any]) -> List[str]:
        """Generate general recommendations based on overall analysis."""
        recommendations = []
        
        overall_score = scores.get("overall", 0)
        github_score = scores.get("github", 0)
        so_score = scores.get("stackoverflow", 0)
        linkedin_score = scores.get("linkedin", 0)
        
        # Overall recommendations
        if overall_score < 40:
            recommendations.append("🎯 Focus on building a stronger online presence across all platforms")
        elif overall_score < 70:
            recommendations.append("📈 You have a good foundation - focus on consistency and quality")
        else:
            recommendations.append("⭐ Excellent online presence - maintain your momentum!")
        
        # Platform-specific recommendations
        platform_scores = [
            ("GitHub", github_score),
            ("StackOverflow", so_score),
            ("LinkedIn", linkedin_score)
        ]
        
        # Find weakest platform
        weakest_platform = min(platform_scores, key=lambda x: x[1])
        if weakest_platform[1] < 50:
            recommendations.append(f"🔧 Priority: Improve your {weakest_platform[0]} presence (current score: {weakest_platform[1]})")
        
        # Balance recommendation
        scores_list = [github_score, so_score, linkedin_score]
        if max(scores_list) - min(scores_list) > 40:
            recommendations.append("⚖️ Work on balancing your presence across all platforms")
        
        # Activity recommendation
        improvements = insights.get("areas_for_improvement", [])
        if any("activity" in imp.lower() for imp in improvements):
            recommendations.append("📅 Increase your regular activity and contributions")
        
        # Community engagement
        if github_score < 60 or so_score < 60:
            recommendations.append("👥 Engage more with developer communities")
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    def _generate_action_plan(self, scores: Dict[str, Any], insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a 30-day action plan."""
        plan = []
        day = 1
        
        github_score = scores.get("github", 0)
        so_score = scores.get("stackoverflow", 0)
        linkedin_score = scores.get("linkedin", 0)
        
        # Week 1: Profile optimization
        plan.append({
            "day": day,
            "week": 1,
            "action": "Audit all profiles - update bios, photos, and contact information",
            "priority": "high",
            "estimated_time": "2 hours",
            "platforms": ["GitHub", "StackOverflow", "LinkedIn"]
        })
        day += 2
        
        if linkedin_score < 70:
            plan.append({
                "day": day,
                "week": 1,
                "action": "Complete LinkedIn profile - add missing experiences, skills, and summary",
                "priority": "high",
                "estimated_time": "1-2 hours",
                "platforms": ["LinkedIn"]
            })
            day += 2
        
        plan.append({
            "day": day,
            "week": 1,
            "action": "Create/update your professional README on GitHub with portfolio highlights",
            "priority": "medium",
            "estimated_time": "1 hour",
            "platforms": ["GitHub"]
        })
        day += 2
        
        # Week 2: Content creation
        plan.append({
            "day": day,
            "week": 2,
            "action": "Start a new public project or contribute to an open-source project",
            "priority": "high",
            "estimated_time": "3-5 hours",
            "platforms": ["GitHub"]
        })
        day += 3
        
        if so_score < 60:
            plan.append({
                "day": day,
                "week": 2,
                "action": "Answer 3-5 StackOverflow questions in your expertise areas",
                "priority": "medium",
                "estimated_time": "2 hours",
                "platforms": ["StackOverflow"]
            })
            day += 2
        
        plan.append({
            "day": day,
            "week": 2,
            "action": "Write and publish a technical article or blog post",
            "priority": "medium",
            "estimated_time": "3 hours",
            "platforms": ["LinkedIn", "GitHub"]
        })
        day += 3
        
        # Week 3: Engagement
        plan.append({
            "day": day,
            "week": 3,
            "action": "Star, fork, and contribute to 5 interesting GitHub repositories",
            "priority": "medium",
            "estimated_time": "2 hours",
            "platforms": ["GitHub"]
        })
        day += 2
        
        plan.append({
            "day": day,
            "week": 3,
            "action": "Engage with LinkedIn content - comment on posts and share insights",
            "priority": "low",
            "estimated_time": "30 minutes",
            "platforms": ["LinkedIn"]
        })
        day += 2
        
        if so_score > 0:
            plan.append({
                "day": day,
                "week": 3,
                "action": "Review and improve your top StackOverflow answers",
                "priority": "low",
                "estimated_time": "1 hour",
                "platforms": ["StackOverflow"]
            })
        day += 3
        
        # Week 4: Consolidation and networking
        plan.append({
            "day": day,
            "week": 4,
            "action": "Update repository documentation and README files",
            "priority": "medium",
            "estimated_time": "2 hours",
            "platforms": ["GitHub"]
        })
        day += 2
        
        plan.append({
            "day": day,
            "week": 4,
            "action": "Connect with 10-20 professionals in your field on LinkedIn",
            "priority": "medium",
            "estimated_time": "1 hour",
            "platforms": ["LinkedIn"]
        })
        day += 2
        
        plan.append({
            "day": day,
            "week": 4,
            "action": "Review progress and plan next month's goals",
            "priority": "high",
            "estimated_time": "1 hour",
            "platforms": ["All"]
        })
        
        return plan
