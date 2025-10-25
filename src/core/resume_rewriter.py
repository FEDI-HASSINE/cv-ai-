"""
Resume Rewriter Module
AI-powered resume optimization and rewriting suggestions.
"""

import re
from typing import Dict, List, Any, Tuple
from ..config import Config
from ..utils.helpers import clean_text


class ResumeRewriter:
    """
    Resume rewriter with optimization suggestions
    """
    
    def __init__(self):
        self.config = Config()
        self.action_verbs = self._load_action_verbs()
        self.weak_phrases = self._load_weak_phrases()
    
    def _load_action_verbs(self) -> Dict[str, List[str]]:
        """Load action verbs by category"""
        return {
            "Leadership": [
                "Led", "Directed", "Managed", "Coordinated", "Supervised",
                "Orchestrated", "Spearheaded", "Championed", "Mentored", "Guided"
            ],
            "Achievement": [
                "Achieved", "Accomplished", "Delivered", "Exceeded", "Surpassed",
                "Attained", "Completed", "Earned", "Won", "Secured"
            ],
            "Innovation": [
                "Created", "Developed", "Designed", "Engineered", "Innovated",
                "Pioneered", "Invented", "Launched", "Established", "Built"
            ],
            "Improvement": [
                "Improved", "Enhanced", "Optimized", "Streamlined", "Transformed",
                "Upgraded", "Modernized", "Refined", "Strengthened", "Boosted"
            ],
            "Analysis": [
                "Analyzed", "Evaluated", "Assessed", "Researched", "Investigated",
                "Examined", "Studied", "Measured", "Calculated", "Forecasted"
            ],
            "Communication": [
                "Presented", "Communicated", "Articulated", "Conveyed", "Negotiated",
                "Collaborated", "Facilitated", "Advocated", "Promoted", "Influenced"
            ]
        }
    
    def _load_weak_phrases(self) -> Dict[str, str]:
        """Load weak phrases and their stronger alternatives"""
        return {
            "responsible for": "managed",
            "worked on": "developed",
            "helped with": "contributed to",
            "in charge of": "led",
            "did": "executed",
            "made": "created",
            "was involved in": "collaborated on",
            "assisted": "supported",
            "duties included": "delivered",
            "handled": "managed"
        }
    
    def rewrite(self, resume_text: str, analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate rewriting suggestions for resume
        
        Args:
            resume_text: Original resume text
            analysis: Optional analysis results from ResumeAnalyzer
            
        Returns:
            Rewriting suggestions and improvements
        """
        cleaned_text = clean_text(resume_text)
        
        # Detect weak phrases
        weak_phrase_suggestions = self._detect_weak_phrases(cleaned_text)
        
        # Suggest action verbs
        action_verb_suggestions = self._suggest_action_verbs(cleaned_text)
        
        # Quantification opportunities
        quantification_suggestions = self._find_quantification_opportunities(cleaned_text)
        
        # Formatting improvements
        formatting_suggestions = self._suggest_formatting_improvements(cleaned_text)
        
        # Content enhancement
        content_suggestions = self._suggest_content_enhancements(cleaned_text, analysis)
        
        # Generate optimized sections
        optimized_sections = self._generate_optimized_sections(cleaned_text)
        
        # Overall recommendations
        recommendations = self._generate_recommendations(
            weak_phrase_suggestions,
            action_verb_suggestions,
            quantification_suggestions,
            formatting_suggestions
        )
        
        return {
            "weak_phrases": weak_phrase_suggestions,
            "action_verbs": action_verb_suggestions,
            "quantification": quantification_suggestions,
            "formatting": formatting_suggestions,
            "content_enhancements": content_suggestions,
            "optimized_sections": optimized_sections,
            "recommendations": recommendations,
            "improvement_score": self._calculate_improvement_potential(
                weak_phrase_suggestions,
                quantification_suggestions
            )
        }
    
    def _detect_weak_phrases(self, text: str) -> List[Dict[str, str]]:
        """Detect weak phrases and suggest alternatives"""
        suggestions = []
        text_lower = text.lower()
        
        for weak, strong in self.weak_phrases.items():
            if weak in text_lower:
                # Find context
                pattern = re.compile(rf'(.{{0,50}}{re.escape(weak)}.{{0,50}})', re.IGNORECASE)
                matches = pattern.findall(text)
                
                for match in matches[:3]:  # Limit to 3 examples
                    suggestions.append({
                        "weak_phrase": weak,
                        "strong_alternative": strong,
                        "context": match.strip(),
                        "improved": match.lower().replace(weak, strong)
                    })
        
        return suggestions
    
    def _suggest_action_verbs(self, text: str) -> Dict[str, List[str]]:
        """Suggest action verbs by category"""
        suggestions = {}
        
        for category, verbs in self.action_verbs.items():
            # Check how many verbs from this category are already used
            used_count = sum(1 for verb in verbs if verb.lower() in text.lower())
            
            if used_count < 2:  # Suggest category if underused
                suggestions[category] = verbs[:5]  # Top 5 suggestions
        
        return suggestions
    
    def _find_quantification_opportunities(self, text: str) -> List[Dict[str, str]]:
        """Find opportunities to add quantifiable metrics"""
        opportunities = []
        
        # Patterns that could benefit from quantification
        patterns = [
            (r'improved\s+(\w+)', "Consider quantifying: 'Improved {} by X%'"),
            (r'increased\s+(\w+)', "Add metrics: 'Increased {} by X units/percent'"),
            (r'reduced\s+(\w+)', "Specify amount: 'Reduced {} by X%'"),
            (r'managed\s+(?:a\s+)?team', "Add team size: 'Managed team of X members'"),
            (r'worked\s+with\s+(\w+)', "Quantify collaboration: 'Collaborated with X {}s'"),
            (r'developed\s+(\w+)', "Add scope: 'Developed X {}(s)'"),
            (r'led\s+(\w+)', "Specify scale: 'Led {} of X people/projects'")
        ]
        
        for pattern, suggestion_template in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = text[max(0, match.start()-40):min(len(text), match.end()+40)]
                
                # Check if numbers are already present nearby
                if not re.search(r'\d+', context):
                    opportunities.append({
                        "context": context.strip(),
                        "suggestion": suggestion_template.format(match.group(1) if match.groups() else "")
                    })
        
        return opportunities[:10]  # Limit to 10 opportunities
    
    def _suggest_formatting_improvements(self, text: str) -> List[str]:
        """Suggest formatting improvements"""
        suggestions = []
        
        # Check for consistent bullet points
        if text.count('•') < 5 and text.count('-') > text.count('•'):
            suggestions.append("Use consistent bullet points (•) instead of hyphens")
        
        # Check for section headers
        if not re.search(r'[A-Z\s]{5,}', text):
            suggestions.append("Use clear section headers in UPPERCASE or bold")
        
        # Check line length (should have reasonable breaks)
        lines = text.split('\n')
        long_lines = [l for l in lines if len(l) > 100]
        if len(long_lines) > len(lines) * 0.5:
            suggestions.append("Break long sentences into multiple bullet points")
        
        # Check for dates format consistency
        date_formats = [
            r'\d{4}-\d{4}',  # 2020-2024
            r'\d{2}/\d{4}',  # 01/2020
            r'[A-Z][a-z]+\s+\d{4}'  # January 2020
        ]
        format_counts = [len(re.findall(pattern, text)) for pattern in date_formats]
        if sum(1 for c in format_counts if c > 0) > 1:
            suggestions.append("Use consistent date format throughout (e.g., MM/YYYY)")
        
        # Check for appropriate white space
        if text.count('\n\n') < 3:
            suggestions.append("Add spacing between sections for better readability")
        
        return suggestions
    
    def _suggest_content_enhancements(
        self,
        text: str,
        analysis: Dict[str, Any] = None
    ) -> List[str]:
        """Suggest content enhancements based on analysis"""
        suggestions = []
        
        if analysis:
            # Based on missing sections
            sections = analysis.get("sections_found", [])
            
            if "Summary" not in sections:
                suggestions.append(
                    "Add a professional summary at the top highlighting your key strengths"
                )
            
            if "Projects" not in sections:
                suggestions.append(
                    "Include a Projects section to showcase practical experience"
                )
            
            if "Certifications" not in sections:
                suggestions.append(
                    "Add relevant certifications to demonstrate continuous learning"
                )
            
            # Based on skills
            tech_skills = analysis.get("technical_skills", [])
            if len(tech_skills) < 8:
                suggestions.append(
                    "Expand technical skills section with programming languages, tools, and frameworks"
                )
        
        # General content suggestions
        suggestions.extend([
            "Use the STAR method (Situation, Task, Action, Result) for experience descriptions",
            "Focus on achievements rather than just responsibilities",
            "Include keywords relevant to your target industry",
            "Highlight leadership and initiative-taking examples"
        ])
        
        return suggestions[:8]
    
    def _generate_optimized_sections(self, text: str) -> Dict[str, str]:
        """Generate examples of optimized sections"""
        optimized = {}
        
        # Professional Summary example
        optimized["Professional Summary"] = (
            "Results-driven [Your Title] with X+ years of experience in [Industry]. "
            "Proven track record of [Key Achievement]. Skilled in [Top Skills]. "
            "Seeking to leverage expertise in [Specific Area] to drive [Desired Outcome]."
        )
        
        # Experience bullet point examples
        optimized["Experience Bullet Points"] = [
            "• Led team of X engineers to develop [Product], resulting in Y% increase in [Metric]",
            "• Optimized [Process/System] reducing [Cost/Time] by X%, saving $Y annually",
            "• Collaborated with cross-functional team of X members to deliver [Project] ahead of schedule",
            "• Implemented [Technology/Solution] improving [Metric] by X% and increasing [Result]"
        ]
        
        # Skills section example
        optimized["Skills Section"] = (
            "Technical Skills: [List 8-12 relevant technologies]\n"
            "Tools & Platforms: [List platforms and tools]\n"
            "Soft Skills: [List 4-6 key soft skills]"
        )
        
        return optimized
    
    def _generate_recommendations(
        self,
        weak_phrases: List[Dict[str, str]],
        action_verbs: Dict[str, List[str]],
        quantification: List[Dict[str, str]],
        formatting: List[str]
    ) -> List[Dict[str, str]]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        # High priority: Weak phrases
        if weak_phrases:
            recommendations.append({
                "priority": "High",
                "category": "Language",
                "recommendation": f"Replace {len(weak_phrases)} weak phrases with stronger action verbs",
                "impact": "Significantly improves resume impact and readability"
            })
        
        # High priority: Quantification
        if quantification:
            recommendations.append({
                "priority": "High",
                "category": "Content",
                "recommendation": "Add quantifiable metrics to achievements",
                "impact": "Demonstrates concrete results and value"
            })
        
        # Medium priority: Action verbs
        if action_verbs:
            recommendations.append({
                "priority": "Medium",
                "category": "Language",
                "recommendation": "Diversify action verbs across different categories",
                "impact": "Makes resume more engaging and professional"
            })
        
        # Medium priority: Formatting
        if formatting:
            recommendations.append({
                "priority": "Medium",
                "category": "Format",
                "recommendation": "Improve formatting consistency",
                "impact": "Enhances visual appeal and ATS compatibility"
            })
        
        # General recommendations
        recommendations.extend([
            {
                "priority": "Low",
                "category": "Content",
                "recommendation": "Tailor resume to specific job descriptions",
                "impact": "Increases relevance for target positions"
            },
            {
                "priority": "Low",
                "category": "Content",
                "recommendation": "Include keywords from job postings",
                "impact": "Improves ATS scan results"
            }
        ])
        
        return recommendations
    
    def _calculate_improvement_potential(
        self,
        weak_phrases: List[Dict[str, str]],
        quantification: List[Dict[str, str]]
    ) -> int:
        """Calculate potential improvement score"""
        potential = 0
        
        # Each weak phrase fixed adds points
        potential += min(30, len(weak_phrases) * 3)
        
        # Each quantification opportunity adds points
        potential += min(40, len(quantification) * 4)
        
        # Base improvement potential
        potential += 30
        
        return min(100, potential)
