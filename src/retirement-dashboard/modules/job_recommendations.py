# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Job Recommendations Service using Adzuna API"""

import os
import logging
import requests
from typing import Dict, List, Any
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

class JobRecommendations:
    """Job recommendations service using Adzuna API"""
    
    def __init__(self):
        """Initialize the job recommendations service"""
        self.logger = logging.getLogger(__name__)
        self.adzuna_app_id = os.getenv('ADZUNA_APP_ID')
        self.adzuna_app_key = os.getenv('ADZUNA_APP_KEY')
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        
        if not self.adzuna_app_id or not self.adzuna_app_key:
            logger.warning("Adzuna API credentials not found. Job recommendations will use mock data.")
            self.mock_mode = True
        else:
            self.mock_mode = False
            logger.info("Adzuna API initialized successfully")
    
    def get_job_recommendations(self, current_income: int, desired_income: int, location: str = "us") -> Dict:
        """Get job recommendations based on income goals"""
        try:
            if self.mock_mode:
                return self._get_mock_job_recommendations(current_income, desired_income)
            
            # Calculate salary range for search
            min_salary = max(current_income, desired_income * 0.8)  # At least 80% of desired
            max_salary = desired_income * 1.2  # Up to 120% of desired
            
            # Search for jobs in different categories
            job_categories = self._get_relevant_job_categories(current_income)
            all_jobs = []
            
            for category in job_categories:
                jobs = self._search_jobs(
                    location=location,
                    category=category,
                    min_salary=min_salary,
                    max_salary=max_salary
                )
                all_jobs.extend(jobs)
            
            # Process and rank jobs
            processed_jobs = self._process_and_rank_jobs(all_jobs, current_income, desired_income)
            
            return {
                'total_jobs': len(processed_jobs),
                'jobs': processed_jobs[:10],  # Top 10 jobs
                'income_potential': self._calculate_income_potential(processed_jobs),
                'top_skills': self._extract_top_skills(processed_jobs),
                'career_paths': self._suggest_career_paths(current_income, desired_income)
            }
            
        except Exception as e:
            logger.error(f"Error getting job recommendations: {str(e)}")
            return self._get_mock_job_recommendations(current_income, desired_income)
    
    def _search_jobs(self, location: str, category: str, min_salary: int, max_salary: int) -> List[Dict]:
        """Search for jobs using Adzuna API"""
        try:
            # Adzuna API endpoint for job search
            url = f"{self.base_url}/{location}/search/1"
            
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'category': category,
                'salary_min': min_salary,
                'salary_max': max_salary,
                'results_per_page': 20,
                'sort_by': 'salary'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])
            
        except requests.RequestException as e:
            logger.error(f"Error searching jobs: {str(e)}")
            return []
    
    def _get_relevant_job_categories(self, current_income: int) -> List[str]:
        """Get relevant job categories based on current income level"""
        if current_income < 50000:
            return ['it-jobs', 'customer-services-jobs', 'sales-jobs', 'admin-jobs']
        elif current_income < 80000:
            return ['it-jobs', 'engineering-jobs', 'finance-jobs', 'marketing-jobs']
        else:
            return ['it-jobs', 'engineering-jobs', 'finance-jobs', 'executive-jobs', 'consultancy-jobs']
    
    def _process_and_rank_jobs(self, jobs: List[Dict], current_income: int, desired_income: int) -> List[Dict]:
        """Process and rank jobs based on relevance and income potential"""
        processed_jobs = []
        
        for job in jobs:
            try:
                # Extract job details
                salary_min = job.get('salary_min', 0)
                salary_max = job.get('salary_max', 0)
                avg_salary = (salary_min + salary_max) / 2 if salary_max > 0 else salary_min
                
                # Calculate income increase potential
                income_increase = ((avg_salary - current_income) / current_income * 100) if current_income > 0 else 0
                
                # Calculate relevance score
                relevance_score = self._calculate_relevance_score(job, current_income, desired_income)
                
                processed_job = {
                    'title': job.get('title', 'Unknown'),
                    'company': job.get('company', {}).get('display_name', 'Unknown Company'),
                    'location': job.get('location', {}).get('display_name', 'Remote'),
                    'salary_min': salary_min,
                    'salary_max': salary_max,
                    'avg_salary': avg_salary,
                    'income_increase_percent': round(income_increase, 1),
                    'description': job.get('description', '')[:300] + '...',
                    'url': job.get('redirect_url', ''),
                    'relevance_score': relevance_score,
                    'category': job.get('category', {}).get('label', 'Other'),
                    'created': job.get('created', ''),
                    'contract_type': job.get('contract_type', 'Unknown')
                }
                
                processed_jobs.append(processed_job)
                
            except Exception as e:
                logger.error(f"Error processing job: {str(e)}")
                continue
        
        # Sort by relevance score (descending)
        processed_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return processed_jobs
    
    def _calculate_relevance_score(self, job: Dict, current_income: int, desired_income: int) -> float:
        """Calculate a relevance score for a job"""
        score = 0.0
        
        # Salary relevance (40% of score)
        salary_min = job.get('salary_min', 0)
        salary_max = job.get('salary_max', 0)
        avg_salary = (salary_min + salary_max) / 2 if salary_max > 0 else salary_min
        
        if avg_salary >= desired_income * 0.9:  # Within 10% of desired income
            score += 40
        elif avg_salary >= current_income * 1.1:  # At least 10% increase
            score += 30
        elif avg_salary >= current_income:  # At least current income
            score += 20
        
        # Job title relevance (30% of score)
        title = job.get('title', '').lower()
        high_value_keywords = ['senior', 'lead', 'manager', 'director', 'architect', 'principal']
        if any(keyword in title for keyword in high_value_keywords):
            score += 30
        elif any(keyword in title for keyword in ['analyst', 'specialist', 'developer']):
            score += 20
        
        # Company size/reputation (15% of score)
        company_name = job.get('company', {}).get('display_name', '').lower()
        if any(keyword in company_name for keyword in ['google', 'microsoft', 'apple', 'amazon', 'meta']):
            score += 15
        elif len(company_name) > 0:  # Has a company name
            score += 10
        
        # Freshness (15% of score)
        # For simplicity, assume all jobs are recent
        score += 15
        
        return score
    
    def _calculate_income_potential(self, jobs: List[Dict]) -> Dict:
        """Calculate income potential statistics"""
        if not jobs:
            return {'average_increase': 0, 'max_increase': 0, 'high_potential_jobs': 0}
        
        increases = [job['income_increase_percent'] for job in jobs if job['income_increase_percent'] > 0]
        
        return {
            'average_increase': round(sum(increases) / len(increases), 1) if increases else 0,
            'max_increase': round(max(increases), 1) if increases else 0,
            'high_potential_jobs': len([job for job in jobs if job['income_increase_percent'] > 20])
        }
    
    def _extract_top_skills(self, jobs: List[Dict]) -> List[str]:
        """Extract top skills from job descriptions"""
        # Simple keyword extraction for demo purposes
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 
            'Kubernetes', 'SQL', 'Git', 'Agile', 'Machine Learning', 'AI', 
            'Project Management', 'Leadership', 'Communication', 'Analytics'
        ]
        
        skill_counts = {}
        for job in jobs:
            description = job.get('description', '').lower()
            for skill in common_skills:
                if skill.lower() in description:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Return top 5 skills
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, count in sorted_skills[:5]]
    
    def _suggest_career_paths(self, current_income: int, desired_income: int) -> List[Dict]:
        """Suggest career paths for income growth"""
        paths = []
        
        if current_income < 60000:
            paths.extend([
                {
                    'title': 'Software Development Path',
                    'description': 'Learn programming languages and frameworks',
                    'potential_income': '80,000 - 120,000',
                    'timeline': '1-2 years',
                    'key_skills': ['Python', 'JavaScript', 'React', 'SQL']
                },
                {
                    'title': 'Data Analytics Path',
                    'description': 'Develop data analysis and visualization skills',
                    'potential_income': '70,000 - 100,000',
                    'timeline': '6-12 months',
                    'key_skills': ['SQL', 'Python', 'Tableau', 'Excel']
                }
            ])
        
        if current_income < 100000:
            paths.extend([
                {
                    'title': 'Cloud Engineering Path',
                    'description': 'Specialize in cloud platforms and DevOps',
                    'potential_income': '100,000 - 150,000',
                    'timeline': '1-2 years',
                    'key_skills': ['AWS', 'Docker', 'Kubernetes', 'Terraform']
                },
                {
                    'title': 'Management Path',
                    'description': 'Develop leadership and project management skills',
                    'potential_income': '90,000 - 130,000',
                    'timeline': '2-3 years',
                    'key_skills': ['Leadership', 'Project Management', 'Strategy', 'Communication']
                }
            ])
        
        return paths[:3]  # Return top 3 paths
    
    def _get_mock_job_recommendations(self, current_income: int, desired_income: int) -> Dict:
        """Provide mock job recommendations when API is unavailable"""
        mock_jobs = [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'salary_min': 120000,
                'salary_max': 150000,
                'avg_salary': 135000,
                'income_increase_percent': ((135000 - current_income) / current_income * 100) if current_income > 0 else 35.0,
                'description': 'Join our team to build scalable web applications using modern technologies...',
                'url': 'https://example.com/job1',
                'relevance_score': 85,
                'category': 'IT Jobs',
                'created': '2025-09-15',
                'contract_type': 'permanent'
            },
            {
                'title': 'Data Scientist',
                'company': 'Analytics Solutions',
                'location': 'New York, NY',
                'salary_min': 100000,
                'salary_max': 130000,
                'avg_salary': 115000,
                'income_increase_percent': ((115000 - current_income) / current_income * 100) if current_income > 0 else 25.0,
                'description': 'Analyze large datasets to drive business insights and machine learning models...',
                'url': 'https://example.com/job2',
                'relevance_score': 80,
                'category': 'IT Jobs',
                'created': '2025-09-14',
                'contract_type': 'permanent'
            },
            {
                'title': 'Cloud Architect',
                'company': 'Cloud Innovations',
                'location': 'Seattle, WA',
                'salary_min': 140000,
                'salary_max': 180000,
                'avg_salary': 160000,
                'income_increase_percent': ((160000 - current_income) / current_income * 100) if current_income > 0 else 45.0,
                'description': 'Design and implement cloud infrastructure solutions for enterprise clients...',
                'url': 'https://example.com/job3',
                'relevance_score': 90,
                'category': 'IT Jobs',
                'created': '2025-09-13',
                'contract_type': 'permanent'
            }
        ]
    
    def get_job_recommendations(self):
        """
        Get fresh job recommendations with higher income potential.
        
        Returns:
            list: List of job recommendations
        """
        try:
            if self.adzuna_app_id and self.adzuna_app_key:
                # Try to get real jobs from Adzuna API
                real_jobs = self._fetch_adzuna_jobs()
                if real_jobs:
                    return real_jobs
        except Exception as e:
            self.logger.error(f"Error fetching from Adzuna API: {str(e)}")
        
        # Fallback to enhanced mock jobs for the dashboard
        return [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc.',
                'description': 'Lead development of cloud-native applications with modern frameworks...',
                'salary': '$95,000 - $140,000',
                'location': 'San Francisco, CA (Remote Available)'
            },
            {
                'title': 'Financial Data Analyst',
                'company': 'InvestmentFirm LLC',
                'description': 'Analyze market trends and create financial models for investment decisions...',
                'salary': '$75,000 - $110,000',
                'location': 'New York, NY'
            },
            {
                'title': 'Product Marketing Manager',
                'company': 'StartupX',
                'description': 'Drive product marketing strategy and lead go-to-market initiatives...',
                'salary': '$85,000 - $120,000',
                'location': 'Austin, TX (Hybrid)'
            },
            {
                'title': 'DevOps Consultant',
                'company': 'CloudSolutions Co.',
                'description': 'Contract role helping enterprises migrate to cloud infrastructure...',
                'salary': '$90 - $150/hour',
                'location': 'Remote'
            },
            {
                'title': 'Business Intelligence Analyst',
                'company': 'DataCorp',
                'description': 'Create dashboards and analytics to drive business decision making...',
                'salary': '$70,000 - $100,000',
                'location': 'Seattle, WA'
            },
            {
                'title': 'Content Strategy Director',
                'company': 'MediaGroup',
                'description': 'Lead content strategy across multiple digital platforms and channels...',
                'salary': '$80,000 - $115,000',
                'location': 'Los Angeles, CA'
            }
        ]
    
    def _fetch_adzuna_jobs(self):
        """Fetch jobs from the real Adzuna API"""
        try:
            jobs = []
            
            # Search for high-paying tech jobs (full-time)
            tech_jobs = self._search_adzuna_api("software engineer", 80000)
            jobs.extend(tech_jobs[:3])
            
            # Search for tech contract jobs
            tech_contract = self._search_adzuna_api("software engineer", 70000, contract=True)
            jobs.extend(tech_contract[:2])
            
            # Search for finance jobs
            finance_jobs = self._search_adzuna_api("financial analyst", 70000)
            jobs.extend(finance_jobs[:2])
            
            # Search for management positions
            mgmt_jobs = self._search_adzuna_api("manager", 90000)
            jobs.extend(mgmt_jobs[:2])
            
            # Search for consulting/contract opportunities
            consulting_jobs = self._search_adzuna_api("consultant", 80000, contract=True)
            jobs.extend(consulting_jobs[:2])
            
            # Search for data science roles
            data_jobs = self._search_adzuna_api("data scientist", 85000)
            jobs.extend(data_jobs[:2])
            
            # Remove duplicates based on title and company
            seen = set()
            unique_jobs = []
            for job in jobs:
                key = (job['title'].lower(), job['company'].lower())
                if key not in seen:
                    seen.add(key)
                    unique_jobs.append(job)
            
            return unique_jobs[:15]  # Return top 15 unique jobs
            
        except Exception as e:
            self.logger.error(f"Error in _fetch_adzuna_jobs: {str(e)}")
            return []
    
    def _search_adzuna_api(self, query, min_salary=50000, contract=False):
        """Search the Adzuna API for specific job types"""
        try:
            url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
            
            # Always search for remote jobs
            remote_query = f"{query} remote"
            if contract:
                remote_query += ' contract OR consultant OR freelance'
            
            params = {
                'app_id': self.adzuna_app_id,
                'app_key': self.adzuna_app_key,
                'what': remote_query,
                'salary_min': min_salary,
                'results_per_page': 10,
                'sort_by': 'salary'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                jobs = []
                
                for job in data.get('results', []):
                    salary_min = job.get('salary_min', 0)
                    salary_max = job.get('salary_max', 0)
                    
                    if salary_max:
                        salary_display = f"${salary_min:,.0f} - ${salary_max:,.0f}"
                    elif salary_min:
                        salary_display = f"${salary_min:,.0f}+"
                    else:
                        salary_display = "Competitive"
                    
                    # Determine job type based on title/description
                    job_type = "Contract" if any(word in job.get('title', '').lower() or word in job.get('description', '').lower() 
                                               for word in ['contract', 'consultant', 'freelance', 'contractor']) else "Full-time"
                    
                    jobs.append({
                        'title': job.get('title', 'Unknown Title'),
                        'company': job.get('company', {}).get('display_name', 'Unknown Company'),
                        'description': (job.get('description', '')[:150] + '...') if job.get('description') else 'No description available',
                        'salary': salary_display,
                        'location': job.get('location', {}).get('display_name', 'Location not specified'),
                        'type': job_type,
                        'url': job.get('redirect_url', ''),  # Make jobs clickable
                        'posted': job.get('created', 'Recently posted')
                    })
                
                return jobs
            else:
                self.logger.warning(f"Adzuna API returned status {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching Adzuna API: {str(e)}")
            return []
