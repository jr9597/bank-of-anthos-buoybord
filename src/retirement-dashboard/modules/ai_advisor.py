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
        try:
            # Configure Google Generative AI
            api_key = os.getenv('GOOGLE_AI_API_KEY')
            if not api_key:
                logger.warning("GOOGLE_AI_API_KEY not found. AI features will be limited.")
                self.model = None
            else:
                genai.configure(api_key=api_key)
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
