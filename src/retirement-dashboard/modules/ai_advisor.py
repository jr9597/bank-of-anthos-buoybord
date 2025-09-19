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

"""
AI-Powered Retirement Advisor using Google Gemini

This module provides intelligent retirement planning advice by integrating:
1. Google Gemini AI for natural language processing and advice generation
2. Adzuna API for job search capabilities (tool calling)
3. Financial data analysis and personalized recommendations

Key Features:
- Personalized retirement advice based on user's financial situation
- Integration with current job market data for income optimization
- Tool calling for dynamic job searches during conversations
- Context-aware responses using financial and job market data
- Fallback to mock responses when APIs are unavailable

Architecture:
- Uses Google Gemini 1.5-flash model for speed and accuracy
- Implements tool calling pattern for job searches
- Contextual prompt engineering with financial and job data
- Error handling with graceful degradation to mock responses
"""

import os
import logging
import json
from typing import Dict, List, Any
import google.generativeai as genai
from decimal import Decimal

logger = logging.getLogger(__name__)

class AIAdvisor:
    """
    AI-powered retirement advisor using Google Gemini
    
    This class provides intelligent retirement planning advice by combining:
    - User's financial data (income, expenses, savings, goals)
    - Current job market opportunities (via Adzuna API)
    - AI-powered analysis and recommendations (via Google Gemini)
    
    The advisor can engage in conversational assistance and perform
    tool calling to search for job opportunities when relevant.
    """
    
    def __init__(self):
        """
        Initialize the AI advisor with Google Gemini and Adzuna APIs
        
        Sets up:
        - Google Gemini API connection for AI advice generation
        - Adzuna API credentials for job search tool calling
        - Proper error handling and fallback mechanisms
        """
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
    
    def get_chat_response(self, message, financial_data=None, current_jobs=None):
        """
        Get AI chat response for retirement planning questions with personalized context.
        
        Args:
            message (str): User's question or message
            financial_data (dict): User's financial data for personalized advice
            current_jobs (list): Current available jobs for context
            
        Returns:
            str: AI-generated response
        """
        try:
            if not self.google_ai_api_key:
                return self._get_mock_chat_response(message, financial_data, current_jobs)
            
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
            
            # Add job context if available
            jobs_context = ""
            if current_jobs and len(current_jobs) > 0:
                jobs_context = f"""
                
                Current Available Part-time Job Opportunities (up to $30k):
                """
                for i, job in enumerate(current_jobs[:5], 1):  # Show top 5 jobs in context
                    salary_range = ""
                    if job.get('salary_max', 0) > 0:
                        salary_range = f"${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}"
                    elif job.get('salary_min', 0) > 0:
                        salary_range = f"${job.get('salary_min', 0):,}+"
                    else:
                        salary_range = "Competitive"
                    
                    jobs_context += f"""
                {i}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown Company')}
                   - Salary: {salary_range}
                   - Location: {job.get('location', 'Various')}
                   - Description: {job.get('description', 'No description')[:100]}...
                """
            
            system_prompt = f"""You are a professional financial advisor specializing in retirement planning. 
            You provide helpful, accurate, and personalized advice about retirement savings, investment strategies, 
            and financial planning. Always be encouraging and provide actionable advice. Keep responses concise 
            but informative and specific to the user's situation.{context}{jobs_context}
            
            Base your advice on their actual financial situation when available. Provide specific numbers and actionable steps."""
            
            full_prompt = f"{system_prompt}\n\nUser question: {message}\n\nResponse:"
            
            # Generate AI response
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(full_prompt)
            
            return response.text.strip()
            
        except Exception as e:
            self.logger.error(f"Error getting AI chat response: {str(e)}")
            return self._get_mock_chat_response(message, financial_data)
    
    def search_jobs_with_ai(self, message, financial_data=None, current_jobs=None):
        """
        Enhanced chat response with Gemini function calling for job search.
        
        Uses Gemini's function calling capability to dynamically search for jobs
        when the user asks about employment opportunities. The AI will decide
        when to call the job search function and what parameters to use.
        
        Args:
            message (str): User's message potentially requesting job search
            financial_data (dict): User's financial data for context
            current_jobs (list): Unused in function calling approach
            
        Returns:
            dict: Response with text and optionally job results from function calling
        """
        try:
            if not self.google_ai_api_key:
                return {
                    'response': self.get_chat_response(message, financial_data),
                    'jobs': None
                }
            
            # Configure Gemini with function calling for job search
            genai.configure(api_key=self.google_ai_api_key)
            
            # Define the job search function for Gemini - using correct API format
            search_remote_jobs_declaration = {
                "name": "search_remote_jobs",
                "description": "Search for remote part-time job opportunities using specific keywords and salary range. Use this when users ask about jobs, work, employment, or additional income opportunities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "string",
                            "description": "Job search keywords (e.g., 'software engineer', 'data analyst', 'marketing'). Ask user for specific role preferences if not clear."
                        },
                        "salary_min": {
                            "type": "integer", 
                            "description": "Minimum salary range in USD (default: 0 for part-time work)"
                        },
                        "salary_max": {
                            "type": "integer",
                            "description": "Maximum salary range in USD (default: 30000 for part-time supplemental income)"
                        }
                    },
                    "required": ["keywords"]
                }
            }
            
            # Create context for the AI
            context = ""
            if financial_data:
                monthly_savings = financial_data.get('monthly_income', 0) - financial_data.get('monthly_expenses', 0)
                context = f"""
                User's Financial Context:
                - Current Balance: ${financial_data.get('current_balance', 0):,.2f}
                - Monthly Income: ${financial_data.get('monthly_income', 0):,.2f}
                - Monthly Expenses: ${financial_data.get('monthly_expenses', 0):,.2f}
                - Monthly Savings: ${monthly_savings:,.2f}
                - Additional Monthly Savings Needed: ${financial_data.get('savings_gap', 0):,.2f}
                """
            
            system_prompt = f"""You are a professional retirement planning advisor who helps users find part-time remote work to boost their retirement savings.{context}

When users ask about jobs, work, employment, or additional income opportunities:
1. If they provide specific job keywords/roles, use search_remote_jobs function immediately
2. If they're vague, ask clarifying questions about their preferred job type before searching
3. After getting job results, provide personalized advice based on their financial situation
4. Focus on how additional income can accelerate their retirement goals

For non-job related questions, provide general retirement planning advice based on their financial context.

Be encouraging, specific, and actionable in your responses."""
            
            # Use the exact format from Gemini API documentation
            from google.ai import generativelanguage as glm
            
            # Create the function declaration in the correct format
            function_declaration = glm.FunctionDeclaration(
                name="search_remote_jobs",
                description="Search for remote part-time job opportunities using specific keywords and salary range. Use this when users ask about jobs, work, employment, or additional income opportunities.",
                parameters=glm.Schema(
                    type=glm.Type.OBJECT,
                    properties={
                        "keywords": glm.Schema(
                            type=glm.Type.STRING,
                            description="Job search keywords (e.g., 'software engineer', 'data analyst', 'marketing'). Ask user for specific role preferences if not clear."
                        ),
                        "salary_min": glm.Schema(
                            type=glm.Type.INTEGER,
                            description="Minimum salary range in USD (default: 0 for part-time work)"
                        ),
                        "salary_max": glm.Schema(
                            type=glm.Type.INTEGER,
                            description="Maximum salary range in USD (default: 30000 for part-time supplemental income)"
                        )
                    },
                    required=["keywords"]
                )
            )
            
            # Create tool with the function declaration
            tool = glm.Tool(function_declarations=[function_declaration])
            
            # Create model with tools
            model = genai.GenerativeModel('gemini-1.5-flash', tools=[tool])
            
            # Send message and check for function calls
            response = model.generate_content(f"{system_prompt}\n\nUser: {message}")
            
            # Check if AI decided to call the job search function
            jobs_found = []
            final_response = ""
            
            # First check if there's regular text response
            try:
                final_response = response.text
            except:
                # If no text, it means there might be function calls
                final_response = "Let me search for job opportunities for you..."
            
            # Check for function calls in the response  
            self.logger.info(f"Response candidates: {len(response.candidates) if response.candidates else 0}")
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    self.logger.info(f"Response parts: {len(candidate.content.parts)}")
                    for i, part in enumerate(candidate.content.parts):
                        self.logger.info(f"Part {i}: has function_call = {hasattr(part, 'function_call')}")
                        if hasattr(part, 'function_call') and part.function_call:
                            function_call = part.function_call
                            self.logger.info(f"Function call detected: {function_call.name}")
                            if function_call.name == "search_remote_jobs":
                                # Extract parameters from function call
                                args = dict(function_call.args)
                                keywords = args.get('keywords', 'remote work')
                                salary_min = args.get('salary_min', 0)
                                salary_max = args.get('salary_max', 30000)
                                
                                self.logger.info(f"AI triggered job search: keywords='{keywords}', salary_min={salary_min}, salary_max={salary_max}")
                                
                                # Execute the job search using existing method
                                search_criteria = {
                                    'query': keywords,
                                    'salary_min': salary_min,
                                    'salary_max': salary_max
                                }
                                jobs_found = self._search_adzuna_jobs(search_criteria)
                                
                                # Create function response for AI and get final response
                                job_summaries = []
                                for job in jobs_found[:5]:  # Limit to top 5 for AI context
                                    job_summaries.append({
                                        'title': job.get('title', 'Unknown'),
                                        'company': job.get('company', 'Unknown'),
                                        'salary': job.get('salary', 'Competitive'),
                                        'location': job.get('location', 'Remote')
                                    })
                                
                                # Generate final response with job results
                                job_context = f"I found {len(jobs_found)} job opportunities matching your criteria."
                                if job_summaries:
                                    job_list = ". ".join([f"{job['title']} at {job['company']} ({job['salary']})" for job in job_summaries[:3]])
                                    job_context += f" Here are some examples: {job_list}."
                                
                                final_response = f"Great! I can help you find part-time remote jobs to boost your retirement savings. {job_context} These opportunities can help you reach your additional income goals while maintaining flexibility for your retirement planning."
                                
                                break  # Exit loop after processing first function call
            
            return {
                'response': final_response,
                'jobs': jobs_found if jobs_found else None
            }
            
        except Exception as e:
            self.logger.error(f"Error in function calling job search: {e}")
            # Fallback to regular chat without function calling
            return {
                'response': self.get_chat_response(message, financial_data),
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
                'what': 'remote',       # Search for remote jobs specifically
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
    
    def _get_mock_chat_response(self, message, financial_data=None, current_jobs=None):
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
