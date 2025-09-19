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

"""AI-Powered Retirement Advisor using Google Gemini"""

import os
import logging
import json
from typing import Dict, List, Any
import google.generativeai as genai
from decimal import Decimal

logger = logging.getLogger(__name__)

class AIAdvisor:
    """AI-powered retirement advisor using Google Gemini"""
    
    def __init__(self):
        """Initialize the AI advisor with Google Gemini"""
        self.logger = logging.getLogger(__name__)
        try:
            # Configure Google Generative AI
            self.google_ai_api_key = os.getenv('GOOGLE_AI_API_KEY')
            # Configure Adzuna API for job search tool
            self.adzuna_app_id = os.getenv('ADZUNA_APP_ID')
            self.adzuna_app_key = os.getenv('ADZUNA_APP_KEY')
            
            if not self.google_ai_api_key:
                logger.warning("GOOGLE_AI_API_KEY not found. AI features will be limited.")
                self.model = None
            else:
                genai.configure(api_key=self.google_ai_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("Google Gemini initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Google Gemini: {str(e)}")
            self.model = None
    
    def get_retirement_advice(self, financial_data: Dict, analysis: Dict) -> Dict:
        """Get personalized retirement advice based on financial data"""
        try:
            if not self.model:
                return self._get_fallback_advice(financial_data, analysis)
            
            # Prepare the prompt for Gemini
            prompt = self._create_retirement_advice_prompt(financial_data, analysis)
            
            # Generate advice using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            advice = self._parse_ai_response(response.text)
            
            return {
                'summary': advice.get('summary', 'Focus on consistent saving and smart investing.'),
                'recommendations': advice.get('recommendations', []),
                'risk_assessment': advice.get('risk_assessment', 'Moderate'),
                'action_items': advice.get('action_items', []),
                'confidence_score': advice.get('confidence_score', 75)
            }
            
        except Exception as e:
            logger.error(f"Error getting AI advice: {str(e)}")
            return self._get_fallback_advice(financial_data, analysis)
    
    def analyze_scenario(self, scenario_data: Dict, projections: Dict) -> Dict:
        """Analyze a retirement scenario and provide AI insights"""
        try:
            if not self.model:
                return self._get_fallback_scenario_analysis(scenario_data, projections)
            
            prompt = self._create_scenario_analysis_prompt(scenario_data, projections)
            response = self.model.generate_content(prompt)
            
            insights = self._parse_ai_response(response.text)
            
            return {
                'viability': insights.get('viability', 'Moderate'),
                'suggestions': insights.get('suggestions', []),
                'risks': insights.get('risks', []),
                'opportunities': insights.get('opportunities', [])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing scenario: {str(e)}")
            return self._get_fallback_scenario_analysis(scenario_data, projections)
    
    def get_goal_recommendations(self, goal_data: Dict) -> List[Dict]:
        """Get AI recommendations for achieving retirement goals"""
        try:
            if not self.model:
                return self._get_fallback_goal_recommendations(goal_data)
            
            prompt = self._create_goal_recommendations_prompt(goal_data)
            response = self.model.generate_content(prompt)
            
            recommendations = self._parse_recommendations(response.text)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting goal recommendations: {str(e)}")
            return self._get_fallback_goal_recommendations(goal_data)
    
    def _create_retirement_advice_prompt(self, financial_data: Dict, analysis: Dict) -> str:
        """Create a comprehensive prompt for retirement advice"""
        current_balance = financial_data.get('current_balance', 0)
        monthly_income = financial_data.get('monthly_income', 0)
        monthly_expenses = financial_data.get('monthly_expenses', 0)
        savings_rate = analysis.get('savings_rate', 0)
        
        prompt = f"""
        As a financial advisor specializing in retirement planning, analyze the following financial profile and provide personalized advice:

        Financial Profile:
        - Current Balance: ${current_balance:,.2f}
        - Monthly Income: ${monthly_income:,.2f}
        - Monthly Expenses: ${monthly_expenses:,.2f}
        - Savings Rate: {savings_rate:.1f}%
        - Financial Health Score: {analysis.get('health_score', 'N/A')}

        Please provide a JSON response with the following structure:
        {{
            "summary": "Brief overall assessment and key recommendation",
            "recommendations": [
                "Specific actionable recommendation 1",
                "Specific actionable recommendation 2",
                "Specific actionable recommendation 3"
            ],
            "risk_assessment": "Low/Moderate/High",
            "action_items": [
                "Immediate action 1",
                "Immediate action 2"
            ],
            "confidence_score": 85
        }}

        Focus on practical, actionable advice. Consider factors like emergency funds, debt management, investment diversification, and retirement timeline optimization.
        """
        
        return prompt
    
    def _create_scenario_analysis_prompt(self, scenario_data: Dict, projections: Dict) -> str:
        """Create prompt for scenario analysis"""
        prompt = f"""
        Analyze this retirement scenario and provide insights:

        Scenario Details:
        - Current Age: {scenario_data.get('current_age')}
        - Planned Retirement Age: {scenario_data.get('retirement_age')}
        - Monthly Savings: ${scenario_data.get('monthly_savings', 0):,.2f}
        - Expected Annual Return: {scenario_data.get('expected_return', 7)}%
        
        Projections:
        - Projected Retirement Fund: ${projections.get('total_savings', 0):,.2f}
        - Monthly Retirement Income: ${projections.get('monthly_income', 0):,.2f}

        Provide JSON response:
        {{
            "viability": "High/Moderate/Low",
            "suggestions": ["suggestion1", "suggestion2"],
            "risks": ["risk1", "risk2"],
            "opportunities": ["opportunity1", "opportunity2"]
        }}
        """
        
        return prompt
    
    def _create_goal_recommendations_prompt(self, goal_data: Dict) -> str:
        """Create prompt for goal recommendations"""
        prompt = f"""
        Provide recommendations for achieving this retirement goal:

        Goal: ${goal_data.get('target_amount', 0):,.2f} by age {goal_data.get('target_age', 65)}
        Current Progress: ${goal_data.get('current_savings', 0):,.2f}
        Time Remaining: {goal_data.get('years_remaining', 0)} years

        Return a JSON array of recommendation objects:
        [
            {{
                "title": "Recommendation Title",
                "description": "Detailed explanation",
                "priority": "High/Medium/Low",
                "timeframe": "Immediate/Short-term/Long-term"
            }}
        ]
        """
        
        return prompt
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response and extract structured data"""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: parse manually
                return self._manual_parse_response(response_text)
                
        except json.JSONDecodeError:
            return self._manual_parse_response(response_text)
    
    def _parse_recommendations(self, response_text: str) -> List[Dict]:
        """Parse recommendations from AI response"""
        try:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return self._get_fallback_goal_recommendations({})
                
        except json.JSONDecodeError:
            return self._get_fallback_goal_recommendations({})
    
    def _manual_parse_response(self, response_text: str) -> Dict:
        """Manually parse response when JSON parsing fails"""
        # Simple keyword-based parsing for fallback
        return {
            'summary': 'Focus on increasing your savings rate and diversifying investments.',
            'recommendations': [
                'Increase monthly savings by 10%',
                'Review and optimize investment portfolio',
                'Consider additional income sources'
            ],
            'risk_assessment': 'Moderate',
            'action_items': [
                'Set up automatic savings transfers',
                'Schedule financial review meeting'
            ],
            'confidence_score': 70
        }
    
    def _get_fallback_advice(self, financial_data: Dict, analysis: Dict) -> Dict:
        """Provide fallback advice when AI is unavailable"""
        savings_rate = analysis.get('savings_rate', 0)
        
        recommendations = []
        if savings_rate < 10:
            recommendations.append("Increase your savings rate to at least 10% of income")
        if savings_rate < 20:
            recommendations.append("Aim for a 20% savings rate for optimal retirement preparation")
        
        recommendations.extend([
            "Diversify your investment portfolio across stocks, bonds, and other assets",
            "Consider maximizing contributions to tax-advantaged retirement accounts",
            "Build an emergency fund covering 3-6 months of expenses"
        ])
        
        return {
            'summary': f"With a {savings_rate:.1f}% savings rate, focus on increasing savings and smart investing.",
            'recommendations': recommendations,
            'risk_assessment': 'Moderate',
            'action_items': [
                'Review monthly budget and identify savings opportunities',
                'Research low-cost index funds for investment'
            ],
            'confidence_score': 75
        }
    
    def _get_fallback_scenario_analysis(self, scenario_data: Dict, projections: Dict) -> Dict:
        """Fallback scenario analysis"""
        projected_savings = projections.get('total_savings', 0)
        
        viability = 'High' if projected_savings > 1000000 else 'Moderate' if projected_savings > 500000 else 'Low'
        
        return {
            'viability': viability,
            'suggestions': [
                'Consider increasing monthly contributions',
                'Review investment allocation for optimal returns',
                'Explore additional income opportunities'
            ],
            'risks': [
                'Market volatility could affect returns',
                'Inflation may erode purchasing power'
            ],
            'opportunities': [
                'Take advantage of compound growth over time',
                'Consider employer match programs'
            ]
        }
    
    def _get_fallback_goal_recommendations(self, goal_data: Dict) -> List[Dict]:
        """Fallback goal recommendations"""
        return [
            {
                'title': 'Increase Savings Rate',
                'description': 'Gradually increase your monthly savings by 1% each year',
                'priority': 'High',
                'timeframe': 'Immediate'
            },
            {
                'title': 'Optimize Investment Mix',
                'description': 'Review and rebalance your portfolio quarterly',
                'priority': 'Medium',
                'timeframe': 'Short-term'
            },
            {
                'title': 'Explore Side Income',
                'description': 'Consider part-time work or freelancing to boost savings',
                'priority': 'Medium',
                'timeframe': 'Long-term'
            }
        ]
    
    def get_chat_response(self, message, financial_data=None):
        """
        Get AI chat response for retirement planning questions with personalized context.
        
        Args:
            message (str): User's question or message
            financial_data (dict): User's financial data for personalized advice
            
        Returns:
            str: AI-generated response
        """
        try:
            if not self.google_ai_api_key:
                return self._get_mock_chat_response(message, financial_data)
            
            # Configure the Gemini API
            genai.configure(api_key=self.google_ai_api_key)
            
            # Create a personalized retirement-focused prompt
            context = ""
            if financial_data:
                context = f"""
                
                User's Financial Context:
                - Current Balance: ${financial_data.get('current_balance', 0):,.2f}
                - Monthly Income: ${financial_data.get('monthly_income', 0):,.2f}
                - Monthly Expenses: ${financial_data.get('monthly_expenses', 0):,.2f}
                - Net Monthly Savings: ${(financial_data.get('monthly_income', 0) - financial_data.get('monthly_expenses', 0)):,.2f}
                - Annual Income: ${financial_data.get('current_income', 0):,.2f}
                """
            
            system_prompt = f"""You are a professional financial advisor specializing in retirement planning. 
            You provide helpful, accurate, and personalized advice about retirement savings, investment strategies, 
            and financial planning. Always be encouraging and provide actionable advice. Keep responses concise 
            but informative and specific to the user's situation.{context}
            
            Base your advice on their actual financial situation when available. Provide specific numbers and actionable steps."""
            
            full_prompt = f"{system_prompt}\n\nUser question: {message}\n\nResponse:"
            
            # Generate AI response
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(full_prompt)
            
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"Error getting AI chat response: {str(e)}")
            return self._get_mock_chat_response(message, financial_data)
    
    def search_jobs_with_ai(self, message, financial_data=None):
        """
        Enhanced chat response that can search for jobs using Adzuna API as a tool.
        
        Args:
            message (str): User's message potentially requesting job search
            financial_data (dict): User's financial data for context
            
        Returns:
            dict: Response with text and optionally job results
        """
        try:
            # Check if user is asking about jobs
            job_keywords = ['job', 'career', 'work', 'salary', 'employment', 'hiring', 'position', 'opportunity']
            is_job_request = any(keyword in message.lower() for keyword in job_keywords)
            
            if not is_job_request:
                # Regular chat response
                return {
                    'response': self.get_chat_response(message, financial_data),
                    'jobs': None
                }
            
            # Extract job search criteria from the message
            search_criteria = self._extract_job_criteria(message, financial_data)
            
            # Search for jobs
            jobs = self._search_adzuna_jobs(search_criteria)
            
            # Generate AI response with job context
            job_context = f"\n\nI found {len(jobs)} relevant job opportunities for you:" if jobs else "\n\nI couldn't find specific jobs matching your criteria, but here's some advice:"
            
            if not self.google_ai_api_key:
                response_text = self._get_mock_job_response(message, financial_data, jobs)
            else:
                # Create enhanced prompt with job search context
                context = ""
                if financial_data:
                    context = f"""
                    User's Financial Context:
                    - Current Balance: ${financial_data.get('current_balance', 0):,.2f}
                    - Monthly Income: ${financial_data.get('monthly_income', 0):,.2f}
                    - Monthly Expenses: ${financial_data.get('monthly_expenses', 0):,.2f}
                    """
                
                job_info = ""
                if jobs:
                    job_info = f"\n\nI searched for jobs and found {len(jobs)} opportunities. The jobs include positions like: " + ", ".join([job['title'] for job in jobs[:3]])
                
                system_prompt = f"""You are a professional financial advisor and career counselor. 
                The user asked about jobs/career opportunities for retirement planning.{context}{job_info}
                
                Provide helpful advice about career growth, salary negotiations, and how career changes can impact retirement planning.
                If jobs were found, reference them and provide specific advice. Be encouraging and actionable."""
                
                full_prompt = f"{system_prompt}\n\nUser question: {message}\n\nResponse:"
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(full_prompt)
                response_text = response.text.strip()
            
            return {
                'response': response_text + job_context,
                'jobs': jobs
            }
            
        except Exception as e:
            self.logger.error(f"Error in AI job search: {str(e)}")
            return {
                'response': "I'd be happy to help you explore career opportunities! Could you tell me more about what type of jobs you're interested in?",
                'jobs': None
            }
    
    def _extract_job_criteria(self, message, financial_data):
        """Extract job search criteria from user message"""
        message_lower = message.lower()
        
        # Default criteria
        criteria = {
            'query': 'remote',
            'salary_min': 50000,
            'location': 'remote'
        }
        
        # Extract job types from message
        if 'software' in message_lower or 'developer' in message_lower or 'engineer' in message_lower:
            criteria['query'] = 'remote software engineer developer'
        elif 'finance' in message_lower or 'analyst' in message_lower:
            criteria['query'] = 'remote financial analyst finance'
        elif 'data' in message_lower or 'scientist' in message_lower:
            criteria['query'] = 'remote data scientist analytics'
        elif 'manager' in message_lower or 'management' in message_lower:
            criteria['query'] = 'remote manager management'
        elif 'consultant' in message_lower or 'consulting' in message_lower:
            criteria['query'] = 'remote consultant consulting'
        
        # Extract salary expectations from financial data
        if financial_data:
            current_income = financial_data.get('current_income', 0)
            if current_income > 0:
                criteria['salary_min'] = max(current_income, 50000)
        
        return criteria
    
    def _search_adzuna_jobs(self, criteria):
        """Search Adzuna API for jobs"""
        try:
            if not self.adzuna_app_id or not self.adzuna_app_key:
                self.logger.warning("Adzuna credentials not available for job search")
                return []
            
            import requests
            
            url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                'app_id': self.adzuna_app_id,
                'app_key': self.adzuna_app_key,
                'what': f"remote part-time contract {criteria.get('query', 'software engineer developer')}",  # Focus on part-time/contract
                'salary_min': 0,        # Start from $0 for part-time work
                'salary_max': 30000,    # Cap at $30k for part-time jobs
                'results_per_page': 8,
                'sort_by': 'salary'
            }
            
            response = requests.get(url, params=params, timeout=10)
            self.logger.info(f"Adzuna job search response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                adzuna_jobs = data.get('results', [])
                
                jobs = []
                for job in adzuna_jobs[:5]:
                    salary_min = job.get('salary_min', 0)
                    salary_max = job.get('salary_max', 0)
                    
                    if salary_max:
                        salary_display = f"${salary_min:,.0f} - ${salary_max:,.0f}"
                    elif salary_min:
                        salary_display = f"${salary_min:,.0f}+"
                    else:
                        salary_display = "Competitive"
                    
                    jobs.append({
                        'title': job.get('title', 'Unknown Title'),
                        'company': job.get('company', {}).get('display_name', 'Unknown Company'),
                        'description': (job.get('description', '')[:150] + '...') if job.get('description') else 'No description available',
                        'salary': salary_display,
                        'location': job.get('location', {}).get('display_name', 'Remote'),
                        'type': 'Remote',
                        'url': job.get('redirect_url', ''),
                        'posted': job.get('created', 'Recently posted')
                    })
                
                self.logger.info(f"Found {len(jobs)} jobs via AI tool calling")
                return jobs
            else:
                self.logger.warning(f"Adzuna API returned {response.status_code}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching jobs: {str(e)}")
            return []
    
    def _get_mock_job_response(self, message, financial_data, jobs):
        """Generate mock response for job-related queries"""
        if jobs:
            return f"I found some great opportunities for you! Based on your request about jobs, I've identified {len(jobs)} positions that could help boost your retirement savings. These roles offer competitive salaries that could significantly accelerate your retirement timeline."
        else:
            return "I'd love to help you find career opportunities to boost your retirement savings! Try asking me about specific job types like 'software engineer jobs' or 'remote analyst positions' and I'll search for opportunities that match your income goals."
    
    def _get_mock_chat_response(self, message, financial_data=None):
        """Get mock chat response when AI is not available"""
        # Simple keyword-based responses with financial context
        message_lower = message.lower()
        
        # Use financial data for more personalized mock responses
        monthly_savings = 0
        if financial_data:
            monthly_savings = financial_data.get('monthly_income', 0) - financial_data.get('monthly_expenses', 0)
        if 'savings' in message_lower or 'save' in message_lower:
            return "Consistent savings are the foundation of retirement planning. I recommend automating your savings and gradually increasing your contribution rate as your income grows."
        elif 'investment' in message_lower or 'invest' in message_lower:
            return "Diversified investing is key for retirement. Consider a mix of stocks, bonds, and other assets appropriate for your age and risk tolerance. The earlier you start, the more time compound interest has to work for you."
        elif 'goal' in message_lower or 'target' in message_lower:
            return "Setting clear retirement goals is crucial! A common rule of thumb is to aim for 10-12 times your annual income by retirement age. Break this down into smaller, achievable milestones."
        elif 'age' in message_lower or 'when' in message_lower:
            return "The best time to start retirement planning is now! Whether you're 25 or 55, there are strategies that can help improve your retirement outlook. The key is to start where you are and build momentum."
        else:
            return "Great question! Retirement planning is personal and depends on your unique situation. Focus on building good financial habits: save consistently, invest wisely, and review your plan regularly."
