"""
Dynamic Job Search Engine
Searches for real job opportunities from multiple sources
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
from urllib.parse import quote_plus
import re


class JobScraper:
    """
    Dynamically search for job opportunities from various sources
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
    
    def search_jobs(
        self,
        keywords: List[str],
        location: str = "",
        experience_level: str = "",
        max_results: int = 20
    ) -> List[Dict]:
        """
        Enhanced job search from multiple sources with better error handling
        
        Args:
            keywords: List of search keywords (skills, job titles, etc.)
            location: Location/region to search
            experience_level: Entry, Mid, Senior level
            max_results: Maximum number of results to return
            
        Returns:
            List of job dictionaries with details and links
        """
        all_jobs = []
        
        # Increase search depth - get more results from each source
        results_per_source = max(max_results // 2, 10)
        
        # Search from multiple sources with retries
        # Added Africa and MENA job boards
        sources = [
            ('LinkedIn', self._search_linkedin),
            ('Indeed', self._search_indeed),
            ('Glassdoor', self._search_glassdoor),
            ('Bayt (MENA)', self._search_bayt),
            ('Tanqeeb (Gulf)', self._search_tanqeeb),
            ('BrighterMonday (Africa)', self._search_brightermonday),
            ('JobsInAfrica', self._search_jobsinafrica),
        ]
        
        for source_name, search_func in sources:
            try:
                print(f"Searching {source_name}...")
                jobs = search_func(keywords, location, results_per_source)
                all_jobs.extend(jobs)
                print(f"Found {len(jobs)} jobs from {source_name}")
                time.sleep(1)  # Rate limiting between sources
            except Exception as e:
                print(f"{source_name} search error: {e}")
                continue
        
        print(f"Total jobs before filtering: {len(all_jobs)}")
        
        # Remove duplicates based on title and company
        unique_jobs = self._remove_duplicates(all_jobs)
        print(f"Unique jobs after deduplication: {len(unique_jobs)}")
        
        # Enrich job details
        enriched_jobs = [self._enrich_job_details(job) for job in unique_jobs]
        
        # Filter by experience level if specified
        if experience_level:
            enriched_jobs = self._filter_by_experience(enriched_jobs, experience_level)
            print(f"Jobs after experience filtering: {len(enriched_jobs)}")
        
        # Sort by relevance (based on keyword matches)
        enriched_jobs = self._sort_by_relevance(enriched_jobs, keywords)
        
        return enriched_jobs[:max_results]
    
    def _search_linkedin(self, keywords: List[str], location: str, max_results: int) -> List[Dict]:
        """
        Search LinkedIn Jobs (public job board)
        Enhanced with better parsing and more details
        """
        jobs = []
        query = " ".join(keywords)
        
        # LinkedIn Jobs public search URL with more filters
        url = f"https://www.linkedin.com/jobs/search?keywords={quote_plus(query)}&location={quote_plus(location)}&f_TPR=r2592000&sortBy=R"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards - Try multiple selectors for better results
                job_cards = soup.find_all('div', class_='base-card', limit=max_results)
                if not job_cards:
                    job_cards = soup.find_all('li', class_='jobs-search-results__list-item', limit=max_results)
                
                for card in job_cards:
                    try:
                        # Extract title
                        title_elem = card.find('h3', class_='base-search-card__title')
                        if not title_elem:
                            title_elem = card.find('a', class_='job-card-list__title')
                        
                        # Extract company
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        if not company_elem:
                            company_elem = card.find('a', class_='job-card-container__company-name')
                        
                        # Extract location
                        location_elem = card.find('span', class_='job-search-card__location')
                        if not location_elem:
                            location_elem = card.find('li', class_='job-card-container__metadata-item')
                        
                        # Extract link
                        link_elem = card.find('a', class_='base-card__full-link')
                        if not link_elem:
                            link_elem = card.find('a', {'data-tracking-control-name': 'public_jobs_jserp-result_search-card'})
                        
                        # Extract posted date
                        date_elem = card.find('time', class_='job-search-card__listdate')
                        posted_date = date_elem.get('datetime', 'Recent') if date_elem else 'Recent'
                        
                        if title_elem and company_elem and link_elem:
                            job_url = link_elem.get('href', '')
                            
                            # Try to extract job description snippet
                            desc_elem = card.find('p', class_='job-card-list__snippet')
                            description = desc_elem.text.strip() if desc_elem else ''
                            
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'url': job_url,
                                'source': 'LinkedIn',
                                'description': description,
                                'posted_date': posted_date
                            }
                            jobs.append(job)
                            
                            # Add small delay to avoid rate limiting
                            if len(jobs) % 5 == 0:
                                time.sleep(0.5)
                                
                    except Exception as e:
                        continue
            
        except Exception as e:
            print(f"LinkedIn scraping error: {e}")
        
        return jobs
    
    def _search_indeed(self, keywords: List[str], location: str, max_results: int) -> List[Dict]:
        """
        Search Indeed jobs with enhanced parsing
        """
        jobs = []
        query = " ".join(keywords)
        
        # Indeed search URL with better parameters
        url = f"https://www.indeed.com/jobs?q={quote_plus(query)}&l={quote_plus(location)}&sort=date&fromage=30"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job cards - Try multiple selectors
                job_cards = soup.find_all('div', class_='job_seen_beacon', limit=max_results)
                if not job_cards:
                    job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard', limit=max_results)
                if not job_cards:
                    job_cards = soup.find_all('a', class_='jcs-JobTitle', limit=max_results)
                
                for card in job_cards:
                    try:
                        # Extract title
                        title_elem = card.find('h2', class_='jobTitle')
                        if not title_elem:
                            title_elem = card.find('a', class_='jcs-JobTitle')
                        if not title_elem:
                            title_elem = card.find('span', {'title': True})
                        
                        # Extract company
                        company_elem = card.find('span', class_='companyName')
                        if not company_elem:
                            company_elem = card.find('span', class_='company')
                        
                        # Extract location
                        location_elem = card.find('div', class_='companyLocation')
                        if not location_elem:
                            location_elem = card.find('span', class_='location')
                        
                        # Get job link
                        link_elem = card.find('a', class_='jcs-JobTitle')
                        if not link_elem:
                            link_elem = card.find('a', {'data-jk': True})
                        
                        job_id = link_elem.get('data-jk', '') if link_elem else ''
                        if not job_id and link_elem:
                            href = link_elem.get('href', '')
                            if '/rc/clk?jk=' in href:
                                job_id = href.split('jk=')[1].split('&')[0]
                        
                        # Extract salary if available
                        salary_elem = card.find('span', class_='salary-snippet')
                        if not salary_elem:
                            salary_elem = card.find('div', class_='metadata salary-snippet-container')
                        salary = salary_elem.text.strip() if salary_elem else ''
                        
                        # Extract job snippet/description
                        snippet_elem = card.find('div', class_='job-snippet')
                        if not snippet_elem:
                            snippet_elem = card.find('div', class_='summary')
                        description = snippet_elem.text.strip() if snippet_elem else ''
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.text.strip() if hasattr(title_elem, 'text') else str(title_elem),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'url': f"https://www.indeed.com/viewjob?jk={job_id}" if job_id else url,
                                'source': 'Indeed',
                                'description': description,
                                'posted_date': 'Recent',
                                'salary_range': salary if salary else 'Not specified'
                            }
                            jobs.append(job)
                            
                            # Add delay to avoid rate limiting
                            if len(jobs) % 5 == 0:
                                time.sleep(0.5)
                                
                    except Exception as e:
                        continue
            
        except Exception as e:
            print(f"Indeed scraping error: {e}")
        
        return jobs
    
    def _search_glassdoor(self, keywords: List[str], location: str, max_results: int) -> List[Dict]:
        """
        Search Glassdoor jobs
        Note: Glassdoor heavily protects against scraping. Consider using their API.
        """
        jobs = []
        query = " ".join(keywords)
        
        # Glassdoor search URL
        base_url = "https://www.glassdoor.com/Job/jobs.htm"
        url = f"{base_url}?sc.keyword={quote_plus(query)}&locT=&locId=&jobType="
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Glassdoor structure changes frequently
                # This is a simplified version
                job_cards = soup.find_all('li', class_='react-job-listing', limit=max_results)
                
                for card in job_cards:
                    try:
                        # Extract job details (structure may vary)
                        title_elem = card.find('a', class_='job-search-key-')
                        
                        if title_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': 'Various Companies',
                                'location': location,
                                'url': f"https://www.glassdoor.com{title_elem.get('href', '')}",
                                'source': 'Glassdoor',
                                'description': '',
                                'posted_date': 'Recent'
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
            
        except Exception as e:
            print(f"Glassdoor scraping error: {e}")
        
        return jobs
    
    def _search_bayt(self, keywords: List[str], location: str, max_results: int) -> List[Dict]:
        """
        Search Bayt.com - Leading job site in MENA region
        """
        jobs = []
        query = " ".join(keywords)
        
        # Bayt.com search URL
        url = f"https://www.bayt.com/en/international/jobs/{quote_plus(query)}-jobs/"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Bayt job listings
                job_cards = soup.find_all('li', class_='has-pointer-d', limit=max_results)
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h2', class_='t-default')
                        company_elem = card.find('b', class_='t-default')
                        location_elem = card.find('span', class_='t-mute')
                        link_elem = card.find('a', href=True)
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip(),
                                'location': location_elem.text.strip() if location_elem else location,
                                'url': f"https://www.bayt.com{link_elem['href']}" if link_elem else url,
                                'source': 'Bayt (MENA)',
                                'description': 'Leading MENA job opportunity',
                                'posted_date': 'Recent'
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Bayt scraping error: {e}")
        
        return jobs
    
    def _search_tanqeeb(self, keywords: List[str], location: str, max_results: int) -> List[Dict]:
        """
        Search Tanqeeb - Gulf region job portal
        """
        jobs = []
        query = " ".join(keywords)
        
        # Tanqeeb search URL
        url = f"https://www.tanqeeb.com/jobs/search?q={quote_plus(query)}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('div', class_='job-item', limit=max_results)
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h3') or card.find('h2')
                        company_elem = card.find('span', class_='company')
                        link_elem = card.find('a', href=True)
                        
                        if title_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'Gulf Company',
                                'location': location or 'Gulf Region',
                                'url': f"https://www.tanqeeb.com{link_elem['href']}" if link_elem else url,
                                'source': 'Tanqeeb (Gulf)',
                                'description': 'Gulf region opportunity',
                                'posted_date': 'Recent'
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Tanqeeb scraping error: {e}")
        
        return jobs
    
    def _search_brightermonday(self, keywords: List[str], location: str, max_results: int) -> List[Dict]:
        """
        Search BrighterMonday - Leading job site in East Africa
        """
        jobs = []
        query = " ".join(keywords)
        
        # BrighterMonday search URL (Kenya as default, also covers Uganda, Tanzania)
        url = f"https://www.brightermonday.co.ke/jobs?q={quote_plus(query)}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('article', class_='search-result', limit=max_results)
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h2', class_='search-result__job-title')
                        company_elem = card.find('p', class_='search-result__company-name')
                        link_elem = card.find('a', class_='search-result__job-title-link')
                        
                        if title_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'East African Company',
                                'location': location or 'East Africa',
                                'url': link_elem['href'] if link_elem and link_elem.get('href') else url,
                                'source': 'BrighterMonday (Africa)',
                                'description': 'East African opportunity',
                                'posted_date': 'Recent'
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"BrighterMonday scraping error: {e}")
        
        return jobs
    
    def _search_jobsinafrica(self, keywords: List[str], location: str, max_results: int) -> List[Dict]:
        """
        Search JobsInAfrica - Pan-African job portal
        """
        jobs = []
        query = " ".join(keywords)
        
        # JobsInAfrica search URL
        url = f"https://www.jobsinafrica.com/search?q={quote_plus(query)}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                job_cards = soup.find_all('div', class_='job-listing', limit=max_results)
                
                for card in job_cards[:max_results]:
                    try:
                        title_elem = card.find('h3') or card.find('h2')
                        company_elem = card.find('div', class_='company-name')
                        location_elem = card.find('div', class_='location')
                        link_elem = card.find('a', href=True)
                        
                        if title_elem:
                            job = {
                                'title': title_elem.text.strip(),
                                'company': company_elem.text.strip() if company_elem else 'African Company',
                                'location': location_elem.text.strip() if location_elem else location or 'Africa',
                                'url': link_elem['href'] if link_elem else url,
                                'source': 'JobsInAfrica',
                                'description': 'Pan-African opportunity',
                                'posted_date': 'Recent'
                            }
                            jobs.append(job)
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"JobsInAfrica scraping error: {e}")
        
        return jobs
    
    def search_regional_jobs(
        self,
        keywords: List[str],
        region: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Enhanced regional job search with multiple locations per region
        """
        all_jobs = []
        
        # Expanded regional job boards with more locations
        regional_boards = {
            'MENA': ['Dubai', 'Abu Dhabi', 'Riyadh', 'Cairo', 'Beirut', 'Doha', 'Kuwait City'],
            'Sub-Saharan Africa': ['Lagos', 'Nairobi', 'Johannesburg', 'Accra', 'Kigali', 'Dar es Salaam', 'Cape Town'],
            'North Africa': ['Cairo', 'Casablanca', 'Tunis', 'Algiers', 'Rabat'],
            'Global': ['Remote', 'United States', 'United Kingdom', 'Germany', 'Canada', 'Singapore']
        }
        
        locations = regional_boards.get(region, ['Remote'])
        results_per_location = max(max_results // len(locations), 5)
        
        # Search in multiple locations with better distribution
        for idx, location in enumerate(locations[:4]):  # Limit to 4 locations max
            try:
                print(f"Searching in {location} ({idx+1}/{min(4, len(locations))})...")
                jobs = self.search_jobs(keywords, location, max_results=results_per_location)
                all_jobs.extend(jobs)
                print(f"Found {len(jobs)} jobs in {location}")
                time.sleep(2)  # Increased rate limiting
            except Exception as e:
                print(f"Error searching in {location}: {e}")
                continue
        
        # Remove duplicates and sort
        unique_jobs = self._remove_duplicates(all_jobs)
        unique_jobs = self._sort_by_relevance(unique_jobs, keywords)
        
        return unique_jobs[:max_results]
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate jobs based on title and company
        """
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _filter_by_experience(self, jobs: List[Dict], level: str) -> List[Dict]:
        """
        Filter jobs by experience level
        """
        level_keywords = {
            'Entry': ['junior', 'entry', 'graduate', 'intern', 'associate'],
            'Mid': ['mid', 'intermediate', 'experienced', 'senior'],
            'Senior': ['senior', 'lead', 'principal', 'staff', 'architect', 'director']
        }
        
        keywords = level_keywords.get(level, [])
        if not keywords:
            return jobs
        
        filtered = []
        for job in jobs:
            title_lower = job['title'].lower()
            if any(kw in title_lower for kw in keywords):
                filtered.append(job)
        
        # If no matches, return all (better than nothing)
        return filtered if filtered else jobs
    
    def _sort_by_relevance(self, jobs: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        Enhanced sort by relevance with description and multiple factors
        """
        def relevance_score(job):
            score = 0
            title_lower = job['title'].lower()
            company_lower = job['company'].lower()
            desc_lower = job.get('description', '').lower()
            location_lower = job.get('location', '').lower()
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Title matches worth most
                if keyword_lower in title_lower:
                    score += 5
                # Description matches
                if keyword_lower in desc_lower:
                    score += 2
                # Company matches
                if keyword_lower in company_lower:
                    score += 1
                # Location matches
                if keyword_lower in location_lower:
                    score += 1
            
            # Bonus for remote jobs
            if 'remote' in title_lower or 'remote' in desc_lower:
                score += 2
            
            # Bonus for recent postings
            if 'today' in job.get('posted_date', '').lower() or 'new' in job.get('posted_date', '').lower():
                score += 3
            
            return score
        
        return sorted(jobs, key=relevance_score, reverse=True)
    
    def _enrich_job_details(self, job: Dict) -> Dict:
        """
        Enrich job with additional inferred details
        """
        title_lower = job['title'].lower()
        desc_lower = job.get('description', '').lower()
        
        # Infer experience level
        if any(word in title_lower for word in ['senior', 'lead', 'principal', 'staff', 'architect']):
            job['inferred_level'] = 'Senior'
            job['inferred_experience'] = '5+ years'
        elif any(word in title_lower for word in ['junior', 'entry', 'graduate', 'intern']):
            job['inferred_level'] = 'Entry'
            job['inferred_experience'] = '0-2 years'
        else:
            job['inferred_level'] = 'Mid-Level'
            job['inferred_experience'] = '2-5 years'
        
        # Detect remote work
        job['is_remote'] = ('remote' in title_lower or 'remote' in desc_lower or 
                           'work from home' in desc_lower or 'wfh' in desc_lower)
        
        # Extract skills mentioned
        common_skills = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node', 'django', 'flask', 'spring', 'sql', 'nosql', 'mongodb', 'postgresql',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'git', 'agile',
            'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch'
        ]
        
        job['mentioned_skills'] = [skill for skill in common_skills 
                                   if skill in title_lower or skill in desc_lower]
        
        return job
        
        return sorted(jobs, key=relevance_score, reverse=True)
    
    def get_fallback_jobs(self, keywords: List[str], region: str) -> List[Dict]:
        """
        Return fallback job search URLs when scraping fails
        """
        query = " ".join(keywords)
        
        fallback_jobs = [
            {
                'title': f'Search "{query}" on LinkedIn',
                'company': 'LinkedIn Jobs',
                'location': region,
                'url': f'https://www.linkedin.com/jobs/search?keywords={quote_plus(query)}&location={quote_plus(region)}',
                'source': 'LinkedIn',
                'description': f'Click to search for {query} jobs on LinkedIn',
                'posted_date': 'Search Now'
            },
            {
                'title': f'Search "{query}" on Indeed',
                'company': 'Indeed',
                'location': region,
                'url': f'https://www.indeed.com/jobs?q={quote_plus(query)}&l={quote_plus(region)}',
                'source': 'Indeed',
                'description': f'Click to search for {query} jobs on Indeed',
                'posted_date': 'Search Now'
            },
            {
                'title': f'Search "{query}" on Glassdoor',
                'company': 'Glassdoor',
                'location': region,
                'url': f'https://www.glassdoor.com/Job/jobs.htm?sc.keyword={quote_plus(query)}',
                'source': 'Glassdoor',
                'description': f'Click to search for {query} jobs on Glassdoor',
                'posted_date': 'Search Now'
            },
            {
                'title': f'Search "{query}" on Google Jobs',
                'company': 'Google',
                'location': region,
                'url': f'https://www.google.com/search?q={quote_plus(query + " jobs " + region)}&ibp=htl;jobs',
                'source': 'Google Jobs',
                'description': f'Click to search for {query} jobs on Google',
                'posted_date': 'Search Now'
            },
            {
                'title': f'Search "{query}" on Bayt (MENA)',
                'company': 'Bayt',
                'location': region,
                'url': f'https://www.bayt.com/en/international/jobs/{quote_plus(query)}-jobs/',
                'source': 'Bayt (MENA)',
                'description': f'Search for {query} jobs on leading MENA job site',
                'posted_date': 'Search Now'
            },
            {
                'title': f'Search "{query}" on BrighterMonday (Africa)',
                'company': 'BrighterMonday',
                'location': region,
                'url': f'https://www.brightermonday.co.ke/jobs?q={quote_plus(query)}',
                'source': 'BrighterMonday (Africa)',
                'description': f'Search for {query} jobs in East Africa',
                'posted_date': 'Search Now'
            },
            {
                'title': f'Search "{query}" on Tanqeeb (Gulf)',
                'company': 'Tanqeeb',
                'location': region,
                'url': f'https://www.tanqeeb.com/jobs/search?q={quote_plus(query)}',
                'source': 'Tanqeeb (Gulf)',
                'description': f'Search for {query} jobs in Gulf region',
                'posted_date': 'Search Now'
            },
            {
                'title': f'Search "{query}" on JobsInAfrica',
                'company': 'JobsInAfrica',
                'location': region,
                'url': f'https://www.jobsinafrica.com/search?q={quote_plus(query)}',
                'source': 'JobsInAfrica',
                'description': f'Search for {query} jobs across Africa',
                'posted_date': 'Search Now'
            }
        ]
        
        return fallback_jobs
