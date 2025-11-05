"""
LinkedIn Profile Scraper
Uses Playwright (Python) for best-effort scraping of public LinkedIn profiles.

⚠️ IMPORTANT: This scraper should only be used with explicit user consent
and respects LinkedIn's Terms of Service for public profile access.
It attempts to access only publicly visible information and avoids login-only
content. Real-world reliability may vary due to LinkedIn anti-bot measures.
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


class LinkedInScraper:
    """
    Scrapes public LinkedIn profiles using Playwright (no third-party crawler).
    
    ETHICAL USAGE:
    - Only scrape public profiles with user consent
    - Respect robots.txt and LinkedIn ToS
    - Rate limit requests appropriately
    - Do not use for unauthorized data collection
    """
    
    def __init__(self, headless: bool = True, enable_scraping: bool = False):
        """
        Initialize LinkedIn scraper.
        
        Args:
            headless: Run browser in headless mode
            enable_scraping: Must be explicitly enabled (default: False)
        """
        self.headless = headless
        self.enable_scraping = enable_scraping or os.getenv("ENABLE_SCRAPING", "false").lower() == "true"
        self.require_consent = os.getenv("REQUIRE_CONSENT", "true").lower() == "true"
        self.scraped_data = {}
        
    def collect(self, linkedin_url: str, user_consent: bool = False) -> Dict[str, Any]:
        """
        Collect data from a public LinkedIn profile.
        
        Args:
            linkedin_url: Full LinkedIn profile URL
            user_consent: Explicit user consent flag
            
        Returns:
            Dictionary containing LinkedIn profile data
        """
        # Check consent
        if self.require_consent and not user_consent:
            logger.warning("LinkedIn scraping requires explicit user consent")
            return {
                "success": False,
                "error": "User consent required for LinkedIn scraping",
                "url": linkedin_url,
                "note": "Set user_consent=True or REQUIRE_CONSENT=false"
            }
        
        # Check if scraping is enabled
        if not self.enable_scraping:
            logger.warning("LinkedIn scraping is disabled")
            return {
                "success": False,
                "error": "Scraping is disabled",
                "url": linkedin_url,
                "note": "Enable scraping with ENABLE_SCRAPING=true or use LinkedIn export"
            }
        
        # Validate URL
        if not self._is_valid_linkedin_url(linkedin_url):
            return {
                "success": False,
                "error": "Invalid LinkedIn URL",
                "url": linkedin_url
            }
        
        try:
            logger.info(f"Scraping LinkedIn profile: {linkedin_url}")
            
            # Run async scraping
            result = asyncio.run(self._scrape_profile(linkedin_url))
            
            logger.info(f"Successfully scraped LinkedIn profile")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn profile: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "url": linkedin_url
            }
    
    async def _scrape_profile(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Async method to scrape LinkedIn profile using Playwright directly.
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Scraped profile data
        """
        self.scraped_data = {
            "success": False,
            "url": linkedin_url,
            "profile": {},
            "experience": [],
            "education": [],
            "skills": [],
            "collected_at": datetime.now().isoformat()
        }
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    user_agent=os.getenv(
                        "USER_AGENT",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36"
                    )
                )
                page = await context.new_page()
                await page.goto(linkedin_url, timeout=30000, wait_until="load")
                # Allow network to settle
                try:
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass

                # Check login wall
                if await self._is_login_required(page):
                    logger.warning("LinkedIn requires login - cannot scrape without authentication")
                    self.scraped_data["error"] = "Login required - public profile not accessible"
                else:
                    # Extract sections
                    self.scraped_data["profile"] = await self._extract_profile_info(page)
                    self.scraped_data["experience"] = await self._extract_experience(page)
                    self.scraped_data["education"] = await self._extract_education(page)
                    self.scraped_data["skills"] = await self._extract_skills(page)

                await context.close()
                await browser.close()

            if self.scraped_data.get("profile"):
                self.scraped_data["success"] = True
        except Exception as e:
            logger.error(f"Error scraping LinkedIn profile: {str(e)}")
            self.scraped_data["error"] = str(e)

        return self.scraped_data
    
    async def _is_login_required(self, page) -> bool:
        """Check if LinkedIn is requiring login."""
        try:
            # Check for common login indicators
            login_selectors = [
                'form[data-id="sign-in-form"]',
                '.join-form',
                'button[data-tracking-control-name="guest_homepage-basic_nav-header-signin"]'
            ]
            
            for selector in login_selectors:
                element = await page.query_selector(selector)
                if element:
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _extract_profile_info(self, page) -> Dict[str, Any]:
        """Extract basic profile information."""
        profile = {}
        
        try:
            # Name
            name_element = await page.query_selector('h1.text-heading-xlarge, h1.inline')
            if name_element:
                profile["name"] = await name_element.inner_text()
            
            # Headline/Title
            headline_element = await page.query_selector('.text-body-medium, .top-card-layout__headline')
            if headline_element:
                profile["headline"] = await headline_element.inner_text()
            
            # Location
            location_element = await page.query_selector('.text-body-small.inline.t-black--light, .top-card__subline-item')
            if location_element:
                profile["location"] = await location_element.inner_text()
            
            # About/Summary (if visible without login)
            about_element = await page.query_selector('.core-section-container__content .inline-show-more-text')
            if about_element:
                profile["about"] = await about_element.inner_text()
            
            # Connections count (if visible)
            connections_element = await page.query_selector('.top-card-layout__first-subline')
            if connections_element:
                connections_text = await connections_element.inner_text()
                profile["connections_text"] = connections_text
            
        except Exception as e:
            logger.error(f"Error extracting profile info: {str(e)}")
        
        return profile
    
    async def _extract_experience(self, page) -> list:
        """Extract work experience."""
        experiences = []
        
        try:
            # Find experience section
            experience_section = await page.query_selector('#experience')
            if not experience_section:
                return experiences
            
            # Get experience items
            experience_items = await page.query_selector_all('.artdeco-list__item .pvs-entity')
            
            for item in experience_items[:10]:  # Limit to 10 most recent
                exp = {}
                
                try:
                    # Title
                    title_element = await item.query_selector('.mr1.t-bold span[aria-hidden="true"]')
                    if title_element:
                        exp["title"] = await title_element.inner_text()
                    
                    # Company
                    company_element = await item.query_selector('.t-14.t-normal span[aria-hidden="true"]')
                    if company_element:
                        exp["company"] = await company_element.inner_text()
                    
                    # Duration
                    duration_element = await item.query_selector('.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                    if duration_element:
                        exp["duration"] = await duration_element.inner_text()
                    
                    if exp:
                        experiences.append(exp)
                        
                except Exception as e:
                    logger.debug(f"Error extracting experience item: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting experience: {str(e)}")
        
        return experiences
    
    async def _extract_education(self, page) -> list:
        """Extract education information."""
        education_list = []
        
        try:
            # Find education section
            education_section = await page.query_selector('#education')
            if not education_section:
                return education_list
            
            # Get education items
            education_items = await page.query_selector_all('.artdeco-list__item .pvs-entity')
            
            for item in education_items[:5]:  # Limit to 5 most recent
                edu = {}
                
                try:
                    # School name
                    school_element = await item.query_selector('.mr1.hoverable-link-text.t-bold span[aria-hidden="true"]')
                    if school_element:
                        edu["school"] = await school_element.inner_text()
                    
                    # Degree
                    degree_element = await item.query_selector('.t-14.t-normal span[aria-hidden="true"]')
                    if degree_element:
                        edu["degree"] = await degree_element.inner_text()
                    
                    # Years
                    years_element = await item.query_selector('.t-14.t-normal.t-black--light span[aria-hidden="true"]')
                    if years_element:
                        edu["years"] = await years_element.inner_text()
                    
                    if edu:
                        education_list.append(edu)
                        
                except Exception as e:
                    logger.debug(f"Error extracting education item: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting education: {str(e)}")
        
        return education_list
    
    async def _extract_skills(self, page) -> list:
        """Extract skills list."""
        skills = []
        
        try:
            # Find skills section
            skills_section = await page.query_selector('#skills')
            if not skills_section:
                return skills
            
            # Get skill items
            skill_elements = await page.query_selector_all('.hoverable-link-text.t-bold span[aria-hidden="true"]')
            
            for element in skill_elements[:20]:  # Limit to 20 skills
                try:
                    skill_name = await element.inner_text()
                    if skill_name and skill_name not in skills:
                        skills.append(skill_name)
                except Exception:
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting skills: {str(e)}")
        
        return skills
    
    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn URL format."""
        return url.startswith("https://www.linkedin.com/in/") or \
               url.startswith("https://linkedin.com/in/")
    
    @staticmethod
    def get_mock_data(linkedin_url: str) -> Dict[str, Any]:
        """
        Return mock LinkedIn data for testing without actual scraping.
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            Mock profile data
        """
        return {
            "success": True,
            "url": linkedin_url,
            "note": "MOCK DATA - Enable scraping for real data",
            "profile": {
                "name": "John Doe",
                "headline": "Senior Software Engineer | Python | AI/ML",
                "location": "San Francisco Bay Area",
                "about": "Experienced software engineer with 10+ years in the industry...",
                "connections_text": "500+ connections"
            },
            "experience": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Company Inc",
                    "duration": "2020 - Present · 4 yrs"
                },
                {
                    "title": "Software Engineer",
                    "company": "Startup XYZ",
                    "duration": "2018 - 2020 · 2 yrs"
                }
            ],
            "education": [
                {
                    "school": "University of Technology",
                    "degree": "Bachelor of Science - BS, Computer Science",
                    "years": "2014 - 2018"
                }
            ],
            "skills": [
                "Python", "JavaScript", "Machine Learning", "AWS",
                "Docker", "React", "Node.js", "SQL", "Git"
            ],
            "collected_at": datetime.now().isoformat()
        }
