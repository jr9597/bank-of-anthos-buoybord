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

"""Financial Analysis Engine for Retirement Planning"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple, Any
import math

logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    """Financial analysis engine for retirement planning calculations"""
    
    def __init__(self):
        """Initialize the financial analyzer"""
        self.logger = logging.getLogger(__name__)
    
    def analyze_financial_health(self, financial_data: Dict) -> Dict:
        """Analyze overall financial health and provide metrics"""
        try:
            current_balance = financial_data.get('current_balance', 0)
            monthly_income = financial_data.get('monthly_income', 0)
            monthly_expenses = financial_data.get('monthly_expenses', 0)
            transactions = financial_data.get('transactions', [])
            
            # Calculate key metrics
            net_worth = current_balance
            monthly_savings = monthly_income - monthly_expenses
            savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
            
            # Calculate spending patterns
            spending_analysis = self._analyze_spending_patterns(transactions, financial_data.get('account_id'))
            
            # Calculate financial health score
            health_score = self._calculate_health_score(
                savings_rate, net_worth, monthly_income, spending_analysis
            )
            
            # Emergency fund assessment
            emergency_fund_months = current_balance / monthly_expenses if monthly_expenses > 0 else 0
            
            # Debt analysis (assuming negative balances or high expenses indicate debt)
            debt_to_income_ratio = max(0, (monthly_expenses - monthly_income) / monthly_income * 100) if monthly_income > 0 else 0
            
            return {
                'health_score': round(health_score, 1),
                'savings_rate': round(savings_rate, 1),
                'monthly_savings': round(monthly_savings, 2),
                'emergency_fund_months': round(emergency_fund_months, 1),
                'debt_to_income_ratio': round(debt_to_income_ratio, 1),
                'spending_analysis': spending_analysis,
                'recommendations': self._generate_health_recommendations(
                    savings_rate, emergency_fund_months, debt_to_income_ratio
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing financial health: {str(e)}")
            return self._get_default_analysis()
    
    def calculate_income_expenses(self, transactions: List[Dict], account_id: str) -> Tuple[float, float]:
        """Calculate monthly income and expenses from transaction history"""
        try:
            if not transactions:
                return 0.0, 0.0
            
            # Filter transactions from the last 3 months for better accuracy
            cutoff_date = datetime.now() - timedelta(days=90)
            recent_transactions = []
            
            for transaction in transactions:
                try:
                    # Parse transaction date
                    tx_date = datetime.fromisoformat(transaction.get('timestamp', '').replace('Z', '+00:00'))
                    if tx_date >= cutoff_date:
                        recent_transactions.append(transaction)
                except (ValueError, TypeError):
                    # Skip transactions with invalid dates
                    continue
            
            if not recent_transactions:
                return 0.0, 0.0
            
            total_income = 0.0
            total_expenses = 0.0
            
            for transaction in recent_transactions:
                amount = float(transaction.get('amount', 0)) / 100  # Convert from cents
                to_account = transaction.get('toAccountNum')
                from_account = transaction.get('fromAccountNum')
                
                if to_account == account_id:
                    # Money coming in (income)
                    total_income += amount
                elif from_account == account_id:
                    # Money going out (expense)
                    total_expenses += amount
            
            # Calculate monthly averages (assuming 3-month period)
            months = min(3, len(recent_transactions) / 10)  # Rough estimate
            monthly_income = total_income / max(months, 1)
            monthly_expenses = total_expenses / max(months, 1)
            
            return monthly_income, monthly_expenses
            
        except Exception as e:
            logger.error(f"Error calculating income/expenses: {str(e)}")
            return 0.0, 0.0
    
    def calculate_retirement_projections(self, scenario_data: Dict) -> Dict:
        """Calculate retirement projections based on scenario parameters"""
        try:
            current_age = scenario_data.get('current_age', 30)
            retirement_age = scenario_data.get('retirement_age', 65)
            monthly_savings = scenario_data.get('monthly_savings', 500)
            expected_return = scenario_data.get('expected_return', 7) / 100  # Convert to decimal
            current_savings = scenario_data.get('current_savings', 0)
            
            years_to_retirement = retirement_age - current_age
            months_to_retirement = years_to_retirement * 12
            
            # Calculate future value of current savings
            future_value_current = current_savings * ((1 + expected_return) ** years_to_retirement)
            
            # Calculate future value of monthly contributions
            monthly_return = expected_return / 12
            if monthly_return > 0:
                future_value_contributions = monthly_savings * (
                    ((1 + monthly_return) ** months_to_retirement - 1) / monthly_return
                )
            else:
                future_value_contributions = monthly_savings * months_to_retirement
            
            total_savings = future_value_current + future_value_contributions
            
            # Calculate sustainable withdrawal amount (4% rule)
            annual_withdrawal = total_savings * 0.04
            monthly_retirement_income = annual_withdrawal / 12
            
            # Calculate replacement ratio (compared to current income)
            current_annual_income = scenario_data.get('current_annual_income', monthly_savings * 12 / 0.2)  # Estimate
            replacement_ratio = (annual_withdrawal / current_annual_income * 100) if current_annual_income > 0 else 0
            
            # Calculate total contributions
            total_contributions = current_savings + (monthly_savings * months_to_retirement)
            investment_growth = total_savings - total_contributions
            
            return {
                'total_savings': round(total_savings, 2),
                'monthly_income': round(monthly_retirement_income, 2),
                'annual_income': round(annual_withdrawal, 2),
                'replacement_ratio': round(replacement_ratio, 1),
                'total_contributions': round(total_contributions, 2),
                'investment_growth': round(investment_growth, 2),
                'years_to_retirement': years_to_retirement,
                'adequacy_assessment': self._assess_retirement_adequacy(replacement_ratio, total_savings)
            }
            
        except Exception as e:
            logger.error(f"Error calculating retirement projections: {str(e)}")
            return self._get_default_projections()
    
    def _analyze_spending_patterns(self, transactions: List[Dict], account_id: str) -> Dict:
        """Analyze spending patterns from transaction history"""
        try:
            if not transactions:
                return {'categories': {}, 'trends': 'No data available'}
            
            # Simple categorization based on amount ranges
            categories = {
                'large_expenses': 0,  # > $500
                'medium_expenses': 0,  # $50 - $500
                'small_expenses': 0,  # < $50
                'total_transactions': 0
            }
            
            expense_amounts = []
            
            for transaction in transactions:
                if transaction.get('fromAccountNum') == account_id:
                    amount = float(transaction.get('amount', 0)) / 100
                    expense_amounts.append(amount)
                    categories['total_transactions'] += 1
                    
                    if amount > 500:
                        categories['large_expenses'] += 1
                    elif amount > 50:
                        categories['medium_expenses'] += 1
                    else:
                        categories['small_expenses'] += 1
            
            # Calculate average expense
            avg_expense = sum(expense_amounts) / len(expense_amounts) if expense_amounts else 0
            
            # Determine spending trend
            if avg_expense > 200:
                trend = "High spending pattern detected"
            elif avg_expense > 100:
                trend = "Moderate spending pattern"
            else:
                trend = "Conservative spending pattern"
            
            return {
                'categories': categories,
                'average_expense': round(avg_expense, 2),
                'trends': trend,
                'total_expenses': len(expense_amounts)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spending patterns: {str(e)}")
            return {'categories': {}, 'trends': 'Analysis unavailable'}
    
    def _calculate_health_score(self, savings_rate: float, net_worth: float, 
                              monthly_income: float, spending_analysis: Dict) -> float:
        """Calculate overall financial health score (0-100)"""
        score = 0.0
        
        # Savings rate component (40% of score)
        if savings_rate >= 20:
            score += 40
        elif savings_rate >= 15:
            score += 32
        elif savings_rate >= 10:
            score += 24
        elif savings_rate >= 5:
            score += 16
        else:
            score += max(0, savings_rate * 3.2)  # Proportional for very low rates
        
        # Net worth component (30% of score)
        annual_income = monthly_income * 12
        if annual_income > 0:
            net_worth_ratio = net_worth / annual_income
            if net_worth_ratio >= 2:
                score += 30
            elif net_worth_ratio >= 1:
                score += 25
            elif net_worth_ratio >= 0.5:
                score += 20
            else:
                score += max(0, net_worth_ratio * 40)
        
        # Spending pattern component (20% of score)
        avg_expense = spending_analysis.get('average_expense', 0)
        if monthly_income > 0:
            expense_ratio = avg_expense * spending_analysis.get('total_expenses', 1) / monthly_income
            if expense_ratio <= 0.7:  # Spending 70% or less of income
                score += 20
            elif expense_ratio <= 0.8:
                score += 16
            elif expense_ratio <= 0.9:
                score += 12
            else:
                score += max(0, (1 - expense_ratio) * 100)
        
        # Emergency fund component (10% of score)
        emergency_months = net_worth / monthly_income if monthly_income > 0 else 0
        if emergency_months >= 6:
            score += 10
        elif emergency_months >= 3:
            score += 7
        elif emergency_months >= 1:
            score += 4
        else:
            score += max(0, emergency_months * 4)
        
        return min(100, score)  # Cap at 100
    
    def _generate_health_recommendations(self, savings_rate: float, 
                                       emergency_fund_months: float, 
                                       debt_to_income_ratio: float) -> List[str]:
        """Generate personalized financial health recommendations"""
        recommendations = []
        
        if savings_rate < 10:
            recommendations.append("Increase your savings rate to at least 10% of income")
        elif savings_rate < 20:
            recommendations.append("Aim for a 20% savings rate for optimal financial health")
        
        if emergency_fund_months < 3:
            recommendations.append("Build an emergency fund covering 3-6 months of expenses")
        elif emergency_fund_months < 6:
            recommendations.append("Consider expanding your emergency fund to 6 months of expenses")
        
        if debt_to_income_ratio > 20:
            recommendations.append("Focus on reducing debt to improve cash flow")
        
        if not recommendations:
            recommendations.append("You're on track! Consider maximizing retirement contributions")
        
        return recommendations
    
    def _assess_retirement_adequacy(self, replacement_ratio: float, total_savings: float) -> str:
        """Assess if retirement savings will be adequate"""
        if replacement_ratio >= 80:
            return "Excellent - On track for a comfortable retirement"
        elif replacement_ratio >= 70:
            return "Good - Should maintain current lifestyle in retirement"
        elif replacement_ratio >= 60:
            return "Fair - May need to adjust spending in retirement"
        elif replacement_ratio >= 40:
            return "Below target - Consider increasing contributions"
        else:
            return "Critical - Significant improvement needed"
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis when calculation fails"""
        return {
            'health_score': 50.0,
            'savings_rate': 0.0,
            'monthly_savings': 0.0,
            'emergency_fund_months': 0.0,
            'debt_to_income_ratio': 0.0,
            'spending_analysis': {'categories': {}, 'trends': 'No data available'},
            'recommendations': ['Connect your accounts to get personalized recommendations']
        }
    
    def _get_default_projections(self) -> Dict:
        """Return default projections when calculation fails"""
        return {
            'total_savings': 0.0,
            'monthly_income': 0.0,
            'annual_income': 0.0,
            'replacement_ratio': 0.0,
            'total_contributions': 0.0,
            'investment_growth': 0.0,
            'years_to_retirement': 35,
            'adequacy_assessment': 'Unable to calculate'
        }
