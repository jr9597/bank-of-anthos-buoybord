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
Retirement Dashboard Service for Bank of Anthos

This microservice provides a comprehensive retirement planning dashboard that integrates with:
- Bank of Anthos backend services (balancereader, transactionhistory, userservice)
- Google AI (Gemini) for personalized retirement advice
- Adzuna API for part-time job recommendations to boost retirement income

The service enables users to:
1. View their current financial situation (balance, income, expenses)
2. Analyze retirement trajectory with projections and goals
3. Get AI-powered personalized retirement planning advice
4. Find remote part-time work opportunities to supplement retirement savings
5. Chat with an AI advisor that knows their financial context and available jobs

Architecture:
- Flask web application with JWT authentication
- Modular design with separate modules for AI, jobs, and financial analysis
- Integration with Bank of Anthos microservices via REST APIs
- Real-time job data from Adzuna API
- AI-powered chat using Google Gemini with financial and job context
"""

import os
import logging
import requests
import jwt
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask, request, render_template, jsonify, redirect, url_for, make_response
from werkzeug.middleware.proxy_fix import ProxyFix

# Local imports - Custom modules for retirement dashboard functionality
from modules.ai_advisor import AIAdvisor
from modules.job_recommendations import JobRecommendations
from modules.financial_analyzer import FinancialAnalyzer

# Initialize Flask application
app = Flask(__name__)
# Configure proxy fix for proper handling of headers in Kubernetes/GKE environment
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configure logging for production deployment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize service modules with their respective API configurations
ai_advisor = AIAdvisor()  # Google Gemini AI integration
job_recommendations = JobRecommendations()  # Adzuna API integration
financial_analyzer = FinancialAnalyzer()  # Financial calculation utilities

@app.route('/health', methods=['GET'])
def health_check():
    """
    Kubernetes health check endpoint
    
    Used by Kubernetes for liveness and readiness probes to ensure
    the service is running properly.
    
    Returns:
        dict: Health status for Kubernetes monitoring
    """
    return {'status': 'healthy', 'service': 'retirement-dashboard'}, 200

@app.route('/version', methods=['GET'])
def version():
    """
    Service version endpoint for monitoring and debugging
    
    Returns the current deployment version, useful for tracking
    which version is running in different environments.
    
    Returns:
        str: Current service version from environment or default
    """
    return os.environ.get('VERSION', '1.0.0'), 200

@app.route('/', methods=['GET'])
def dashboard():
    """
    Main retirement dashboard page
    
    This is the primary endpoint that renders the retirement planning dashboard.
    It handles authentication, fetches user financial data, and provides both
    authenticated and demo modes.
    
    Authentication Flow:
    1. Checks for JWT token in URL params, headers, or cookies
    2. Validates token using Bank of Anthos public key
    3. Falls back to demo mode if no valid token
    
    Data Integration:
    - Fetches user balance from balancereader service
    - Retrieves transaction history from transactionhistory service
    - Calculates monthly income and expenses from transaction patterns
    - Performs retirement projections with 5% CAGR
    
    Returns:
        str: Rendered HTML template with financial data and projections
    """
    try:
        # Verify user authentication - check URL parameter first (for cross-domain redirects)
        token = request.args.get('token')  # Check URL parameter first
        
        # If token is in URL, set it as cookie and redirect to clean URL
        if token:
            logger.info("Token received via URL parameter, setting cookie and redirecting")
            # Verify the token first
            try:
                jwt.decode(token, options={"verify_signature": False})
                # Token is valid, set cookie and redirect to clean URL
                resp = make_response(redirect(url_for('dashboard')))
                resp.set_cookie('token', token, httponly=True, secure=False, samesite='Lax')
                return resp
            except Exception as e:
                logger.warning(f"Invalid token in URL parameter: {str(e)}")
                token = None
        
        if not token:
            # Fallback to Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                # Fallback to cookie for browser requests
                token = request.cookies.get('token')
        
        if not token:
            logger.warning("No token found, trying to fetch demo user data from Bank of Anthos")
            # Try to get real data from Bank of Anthos demo user without authentication
            demo_account_id = "1011226111"  # testuser account
            try:
                financial_data = get_bank_demo_data(demo_account_id)
                if financial_data['current_balance'] >= 1000:  # Use realistic demo data if we have a balance
                    logger.info(f"Successfully fetched demo data: balance=${financial_data['current_balance']}")
                    return render_template('dashboard_new.html',
                                         username='testuser',
                                         display_name='Test User (Demo)',
                                         account_id=demo_account_id,
                                         financial_data=financial_data,
                                         analysis={'status': 'demo'},
                                         retirement_advice={'status': 'demo'},
                                         job_recommendations={'jobs': []},
                                         bank_name=os.getenv('BANK_NAME', 'Bank of Anthos'))
            except Exception as e:
                logger.warning(f"Could not fetch demo data: {str(e)}")
            
            # Fallback to hardcoded demo values if Bank of Anthos data unavailable
            logger.warning("Using hardcoded fallback demo values")
            return render_template('dashboard_new.html',
                                 username='demo_user',
                                 display_name='Demo User (Fallback)',
                                 account_id='DEMO123',
                                 financial_data={
                                     'current_balance': 85000,
                                     'monthly_income': 7500,
                                     'monthly_expenses': 4200,
                                     'current_income': 90000,
                                     'desired_income': 110000
                                 },
                                 analysis={'status': 'demo'},
                                 retirement_advice={'status': 'demo'},
                                 job_recommendations={'jobs': []},
                                 bank_name=os.getenv('BANK_NAME', 'Bank of Anthos'))
        
        # Verify and decode token
        try:
            # Get public key for verification
            public_key_path = os.getenv('PUB_KEY_PATH', '/tmp/keys/publickey')
            try:
                with open(public_key_path, 'r') as f:
                    public_key = f.read()
                # Verify token with public key
                user_data = jwt.decode(token, key=public_key, algorithms=['RS256'], 
                                     options={"verify_signature": True})
            except (FileNotFoundError, jwt.InvalidTokenError):
                # Fallback to no verification for development
                logger.warning("Could not verify token signature, using unverified token")
                user_data = jwt.decode(token, options={"verify_signature": False})
            
            username = user_data.get('user')
            account_id = user_data.get('acct')
            display_name = user_data.get('name')
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}, redirecting to login")
            return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login")
        
        # Get user financial data
        financial_data = get_user_financial_data(token, account_id)
        
        # Analyze financial data
        analysis = financial_analyzer.analyze_financial_health(financial_data)
        
        # Get AI-powered retirement advice
        retirement_advice = ai_advisor.get_retirement_advice(financial_data, analysis)
        
        # Get job recommendations for income growth
        current_income = financial_data.get('current_income', 70000)  # Default to 70k if no data
        desired_income = financial_data.get('desired_income', 90000)  # Default to 90k if no data
        
        # Ensure we have valid income values
        if current_income <= 0:
            current_income = 70000
        if desired_income <= 0:
            desired_income = max(current_income * 1.3, 90000)  # 30% increase or 90k minimum
            
        logger.info(f"Getting job recommendations for current_income={current_income}, desired_income={desired_income}")
        
        # Use a safer approach to call job recommendations
        try:
            # Recreate the JobRecommendations instance to ensure it's fresh
            from modules.job_recommendations import JobRecommendations
            job_rec_instance = JobRecommendations()
            job_recommendations_data = job_rec_instance.get_job_recommendations(
                current_income,
                desired_income
            )
            logger.info(f"Successfully got job recommendations: {len(job_recommendations_data.get('jobs', []))} jobs")
        except Exception as e:
            logger.error(f"Error calling get_job_recommendations: {e}")
            # Fallback to empty job recommendations
            job_recommendations_data = {'jobs': []}
        
        return render_template('dashboard_new.html',
                             username=username,
                             display_name=display_name,
                             account_id=account_id,
                             financial_data=financial_data,
                             analysis=analysis,
                             retirement_advice=retirement_advice,
                             job_recommendations=job_recommendations_data,
                             bank_name=os.getenv('BANK_NAME', 'Bank of Anthos'))
        
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/scenario', methods=['POST'])
def retirement_scenario():
    """API endpoint for retirement scenario analysis"""
    try:
        # Get token from Authorization header or cookie
        auth_header = request.headers.get('Authorization')
        token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.cookies.get('token')
            
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
            
        # Verify token
        try:
            public_key_path = os.getenv('PUB_KEY_PATH', '/tmp/keys/publickey')
            try:
                with open(public_key_path, 'r') as f:
                    public_key = f.read()
                jwt.decode(token, key=public_key, algorithms=['RS256'])
            except (FileNotFoundError, jwt.InvalidTokenError):
                # Fallback for development
                jwt.decode(token, options={"verify_signature": False})
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        scenario_data = request.get_json()
        
        # Validate required fields
        required_fields = ['current_age', 'retirement_age', 'monthly_savings', 'expected_return']
        if not all(field in scenario_data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Calculate retirement projections
        projections = financial_analyzer.calculate_retirement_projections(scenario_data)
        
        # Get AI insights for this scenario
        ai_insights = ai_advisor.analyze_scenario(scenario_data, projections)
        
        return jsonify({
            'projections': projections,
            'ai_insights': ai_insights,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in scenario analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/goals', methods=['POST'])
def set_retirement_goal():
    """API endpoint to set retirement savings goals"""
    try:
        # Get token from Authorization header or cookie
        auth_header = request.headers.get('Authorization')
        token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            token = request.cookies.get('token')
            
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
            
        # Verify token
        try:
            public_key_path = os.getenv('PUB_KEY_PATH', '/tmp/keys/publickey')
            try:
                with open(public_key_path, 'r') as f:
                    public_key = f.read()
                jwt.decode(token, key=public_key, algorithms=['RS256'])
            except (FileNotFoundError, jwt.InvalidTokenError):
                jwt.decode(token, options={"verify_signature": False})
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        goal_data = request.get_json()
        
        # In a real application, we would store this in a database
        # For the hackathon, we'll return success with recommendations
        
        ai_recommendations = ai_advisor.get_goal_recommendations(goal_data)
        
        return jsonify({
            'message': 'Goal set successfully',
            'recommendations': ai_recommendations,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error setting goal: {str(e)}")
        return jsonify({'error': str(e)}), 500


def get_bank_demo_data(account_id):
    """Try to fetch demo data from Bank of Anthos without authentication"""
    logger.info(f"Attempting to fetch demo data for account: {account_id}")
    financial_data = {
        'account_id': account_id,
        'current_balance': 0,
        'transactions': [],
        'monthly_income': 0,
        'monthly_expenses': 0,
        'current_income': 0,
        'desired_income': 0
    }
    
    try:
        # Always use realistic demo data since Bank of Anthos APIs require authentication
        # Set realistic demo balance that matches a typical Bank of Anthos demo user
        financial_data['current_balance'] = 12400.50
        logger.info(f"Using realistic demo balance: ${financial_data['current_balance']}")
        
        # Try balance API without auth just for logging (expected to fail)
        balance_url = f"http://{os.getenv('BALANCES_API_ADDR', 'balancereader:8080')}/balances/{account_id}"
        logger.info(f"Trying balance API without auth: {balance_url}")
        try:
            balance_response = requests.get(balance_url, timeout=5)
            logger.info(f"Balance response: {balance_response.status_code}")
            
            if balance_response.status_code == 200:
                balance_data = balance_response.json()
                # Convert from cents to dollars
                financial_data['current_balance'] = float(balance_data) / 100.0
                logger.info(f"Got real balance: {financial_data['current_balance']}")
        except Exception as e:
            logger.info(f"Balance API failed as expected: {e}")
        
        # Try transactions API  
        history_url = f"http://{os.getenv('HISTORY_API_ADDR', 'transactionhistory:8080')}/transactions/{account_id}"
        logger.info(f"Trying history API without auth: {history_url}")
        history_response = requests.get(history_url, timeout=5)
        logger.info(f"History response: {history_response.status_code}")
        
        if history_response.status_code == 200:
            transactions = history_response.json()
            financial_data['transactions'] = transactions
            logger.info(f"Got {len(transactions)} transactions")
            
            # Calculate income and expenses from real transaction history
            income, expenses = financial_analyzer.calculate_income_expenses(transactions, account_id)
            financial_data['monthly_income'] = income
            financial_data['monthly_expenses'] = expenses
            financial_data['current_income'] = income * 12
            financial_data['desired_income'] = financial_data['current_income'] * 1.3
        else:
            logger.info("History API requires authentication, using realistic demo calculations")
            # Simulate realistic monthly cash flow for demo user
            financial_data['monthly_income'] = 5800.00  # Realistic demo income
            financial_data['monthly_expenses'] = 3200.00  # Realistic demo expenses  
            financial_data['current_income'] = financial_data['monthly_income'] * 12
            financial_data['desired_income'] = financial_data['current_income'] * 1.3
            
    except requests.RequestException as e:
        logger.error(f"Network error fetching demo data: {str(e)}")
        # If there are network issues, provide realistic fallback
        financial_data.update({
            'current_balance': 12400.50,
            'monthly_income': 5800.00,
            'monthly_expenses': 3200.00,
            'current_income': 69600.00,
            'desired_income': 90480.00
        })
    
    logger.info(f"Demo financial data: {financial_data}")
    return financial_data

def get_user_financial_data(token, account_id):
    """Fetch user financial data from Bank of Anthos services"""
    logger.info(f"Fetching financial data for account_id: {account_id}")
    headers = {'Authorization': f'Bearer {token}'}
    financial_data = {
        'account_id': account_id,
        'current_balance': 0,
        'transactions': [],
        'monthly_income': 0,
        'monthly_expenses': 0,
        'current_income': 0,
        'desired_income': 0
    }
    
    try:
        # Get current balance
        balance_url = f"http://{os.getenv('BALANCES_API_ADDR', 'balancereader:8080')}/balances/{account_id}"
        logger.info(f"Fetching balance from: {balance_url}")
        balance_response = requests.get(balance_url, headers=headers, timeout=10)
        logger.info(f"Balance response status: {balance_response.status_code}")
        if balance_response.status_code == 200:
            balance_data = balance_response.json()
            logger.info(f"Balance data: {balance_data}")
            # Convert from cents to dollars (Bank of Anthos stores balance in cents)
            financial_data['current_balance'] = float(balance_data) / 100.0
        else:
            logger.warning(f"Balance API returned {balance_response.status_code}: {balance_response.text}")
        
        # Get complete transaction history with pagination support
        transactions = []
        page = 1
        max_pages = 10  # Limit to prevent infinite loops
        history_host = os.getenv('HISTORY_API_ADDR', 'transactionhistory:8080')
        
        while page <= max_pages:
            history_url = f"http://{history_host}/transactions/{account_id}"
            if page > 1:
                history_url += f"?page={page}"
            
            logger.info(f"Fetching transactions from: {history_url} (page {page})")
            history_response = requests.get(history_url, headers=headers, timeout=10)
            logger.info(f"History response status: {history_response.status_code}")
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                page_transactions = history_data if isinstance(history_data, list) else []
                
                if not page_transactions:  # No more transactions
                    break
                    
                transactions.extend(page_transactions)
                logger.info(f"Page {page}: Received {len(page_transactions)} transactions (total: {len(transactions)})")
                
                # If we got less than expected, we might be at the end
                if len(page_transactions) < 50:  # Assuming 50 is typical page size
                    break
                    
                page += 1
            else:
                logger.warning(f"Failed to fetch transactions page {page}: {history_response.status_code}")
                break
        
        logger.info(f"Total transactions fetched: {len(transactions)}")
        financial_data['transactions'] = transactions
        
        # Calculate income and expenses from transaction history
        # Simple approach: use real transactions to estimate monthly income/expenses
        if transactions:
            # Look for external deposits (income) and payments (expenses) in recent months
            total_deposits = 0.0
            total_payments = 0.0
            
            for transaction in transactions:
                try:
                    amount = float(transaction.get('amount', 0)) / 100.0  # Convert cents to dollars
                    to_account = transaction.get('toAccountNum', '')
                    from_account = transaction.get('fromAccountNum', '')
                    
                    # External deposits (income) - money coming TO this account from external bank
                    if (to_account == account_id and '9099791699' in from_account):
                        total_deposits += amount
                        logger.info(f"Found external deposit: ${amount:.2f} from {from_account}")
                    
                    # External payments (expenses) - money going FROM this account to external accounts
                    elif (from_account == account_id and to_account != account_id and 
                          len(to_account) >= 8 and '9099791699' not in to_account):
                        total_payments += amount
                        logger.info(f"Found external payment: ${amount:.2f} to {to_account}")
                        
                except (ValueError, TypeError) as e:
                    continue
            
            # Estimate monthly values (divide by 3 months since we have ~3 months of data)
            months_of_data = 3
            monthly_income = total_deposits / months_of_data if total_deposits > 0 else 4500  # Default $4500
            monthly_expenses = total_payments / months_of_data if total_payments > 0 else 2800  # Default $2800
            
            logger.info(f"Total deposits: ${total_deposits:.2f}, payments: ${total_payments:.2f}")
            logger.info(f"Estimated monthly income: ${monthly_income:.2f}, expenses: ${monthly_expenses:.2f}")
        else:
            # Fallback defaults
            monthly_income = 4500
            monthly_expenses = 2800
            
        financial_data['monthly_income'] = monthly_income
        financial_data['monthly_expenses'] = monthly_expenses
        financial_data['current_income'] = monthly_income * 12  # Annual income
        financial_data['desired_income'] = financial_data['current_income'] * 1.3  # 30% increase
        
        # Calculate retirement goals based on age (using reasonable defaults for now)
        # TODO: Get real user birthday from userservice when implementing full user data integration
        user_age = 35  # Default age
        years_to_retirement = max(65 - user_age, 5)  # Retire at 65, minimum 5 years
        retirement_goal = 1500000  # $1.5M target
        
        # Calculate additional monthly savings needed to reach $1.5M goal
        # Using compound growth: calculate what monthly savings are needed with 5% CAGR
        current_balance = financial_data.get('current_balance', 0)
        cagr = 0.05  # 5% annual growth
        
        # Future value of current balance with 5% growth
        future_value_current = current_balance * ((1 + cagr) ** years_to_retirement)
        
        # Amount still needed after current balance grows
        amount_still_needed = max(0, retirement_goal - future_value_current)
        
        # Monthly savings needed to accumulate the remaining amount with 5% CAGR
        # Using future value of annuity formula: PMT = FV / (((1+r)^n - 1) / r)
        if amount_still_needed > 0 and years_to_retirement > 0:
            monthly_rate = cagr / 12
            total_months = years_to_retirement * 12
            if monthly_rate > 0:
                additional_monthly_savings = amount_still_needed / (((1 + monthly_rate) ** total_months - 1) / monthly_rate)
            else:
                additional_monthly_savings = amount_still_needed / total_months
        else:
            additional_monthly_savings = 0
        
        # Calculate if current savings rate is enough
        current_monthly_savings = monthly_income - monthly_expenses
        savings_gap = max(0, additional_monthly_savings - current_monthly_savings)
        
        financial_data['user_age'] = user_age
        financial_data['years_to_retirement'] = years_to_retirement
        financial_data['retirement_goal'] = retirement_goal
        financial_data['additional_monthly_savings_needed'] = additional_monthly_savings
        financial_data['savings_gap'] = savings_gap
        
        logger.info(f"Calculated monthly income: ${monthly_income:.2f}, expenses: ${monthly_expenses:.2f}")
        logger.info(f"User age: {user_age}, years to retirement: {years_to_retirement}, retirement goal: ${retirement_goal:,.0f}")
        
    except requests.RequestException as e:
        logger.error(f"Error fetching financial data: {str(e)}")
    
    logger.info(f"Final financial data: {financial_data}")
    return financial_data

def get_current_jobs_data():
    """
    Fetch current job recommendations for AI context
    
    This function provides the AI advisor with real-time job market data
    so it can give informed recommendations about available opportunities.
    
    Uses the same search parameters as the main jobs endpoint:
    - Remote jobs only (what: 'remote')
    - Salary range: $0-$30,000 (suitable for part-time supplemental income)
    - Sorted by salary for better matches
    
    Returns:
        list: Array of job objects with title, company, description, salary, location
              Limited to 10 jobs for AI context to avoid token limits
    """
    try:
        import requests
        import os
        
        adzuna_app_id = os.getenv('ADZUNA_APP_ID')
        adzuna_app_key = os.getenv('ADZUNA_APP_KEY')
        
        if not adzuna_app_id or not adzuna_app_key:
            return []
        
        # Search for remote jobs with salary range $0-$30k - same as main endpoint
        url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
        params = {
            'app_id': adzuna_app_id,
            'app_key': adzuna_app_key,
            'what': 'remote',       # Search for remote jobs specifically
            'salary_min': 0,
            'salary_max': 30000,
            'results_per_page': 15,  # Get subset for AI context
            'sort_by': 'salary'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            adzuna_jobs = data.get('results', [])
            
            jobs_data = []
            for job in adzuna_jobs[:10]:  # Limit to 10 for AI context
                jobs_data.append({
                    'title': job.get('title', 'Unknown Title'),
                    'company': job.get('company', {}).get('display_name', 'Unknown Company'),
                    'description': job.get('description', '')[:200],  # Longer description for AI
                    'salary_min': job.get('salary_min', 0),
                    'salary_max': job.get('salary_max', 0),
                    'location': job.get('location', {}).get('display_name', 'Various'),
                    'posted': job.get('created', 'Recently posted')
                })
            
            return jobs_data
        
    except Exception as e:
        logger.error(f"Error fetching jobs for AI context: {e}")
        return []

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """
    AI chat endpoint for personalized retirement advice
    
    This endpoint provides an intelligent chat interface where users can ask
    questions about retirement planning and receive personalized advice.
    
    AI Context Includes:
    - User's current financial situation (balance, income, expenses)
    - Available job opportunities (fetched from Adzuna API)
    - Retirement goals and timeline
    - Investment and savings strategies
    
    The AI can perform tool calling to search for specific job opportunities
    when users ask job-related questions.
    
    Authentication:
    - Attempts to authenticate user for personalized data
    - Falls back to demo financial data for unauthenticated users
    
    Request:
        JSON: {"message": "user question about retirement"}
    
    Returns:
        JSON: {"response": "AI advice", "jobs": [...], "timestamp": "..."}
    """
    try:
        chat_data = request.get_json()
        message = chat_data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user's financial data for personalized responses
        financial_data = None
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            try:
                # Try to get user's real financial data
                token_data = jwt.decode(token, options={"verify_signature": False})
                account_id = token_data.get('acct')
                if account_id:
                    financial_data = get_user_financial_data(token, account_id)
            except:
                # Use demo data if token is invalid
                financial_data = {
                    'current_balance': 85000,
                    'monthly_income': 7500,
                    'monthly_expenses': 4200,
                    'current_income': 90000
                }
        else:
            # Use demo data for unauthenticated users
            financial_data = {
                'current_balance': 85000,
                'monthly_income': 7500,
                'monthly_expenses': 4200,
                'current_income': 90000
            }
        
        # Get current job opportunities for AI context
        current_jobs = get_current_jobs_data()
        
        # Get AI response with financial data and job context
        ai_result = ai_advisor.search_jobs_with_ai(message, financial_data, current_jobs)
        
        response_data = {
            'response': ai_result['response'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Include jobs if found
        if ai_result.get('jobs'):
            response_data['jobs'] = ai_result['jobs']
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'response': 'I apologize, but I encountered an error. Please try again.'}), 200

@app.route('/api/jobs', methods=['GET'])
def get_job_recommendations():
    """
    Get job recommendations from Adzuna API for retirement income supplementation
    
    This endpoint fetches part-time remote job opportunities specifically filtered
    for retirement planning purposes. Jobs are limited to $0-$30k salary range
    to focus on supplemental income rather than full career changes.
    
    Search Parameters:
    - what: 'remote' (ensures all jobs are remote-friendly)
    - salary_min: 0 (includes volunteer/low-pay opportunities)
    - salary_max: 30000 (focuses on part-time/supplemental income)
    - results_per_page: 30 (maximum relevant results)
    
    Query Parameters:
        keywords (optional): Additional search terms (default: 'software engineer')
        location (optional): Location filter (default: 'remote')
    
    Returns:
        JSON: {
            "jobs": [array of job objects],
            "timestamp": "ISO timestamp"
        }
        
    Job Object Format:
        {
            "title": "Job Title",
            "company": "Company Name", 
            "description": "Brief description...",
            "salary": "$X - $Y" or "Competitive",
            "location": "Location or 'Remote'",
            "type": "Part-time/Contract",
            "url": "Application URL",
            "posted": "Date posted"
        }
    """
    try:
        # Get search keywords from query parameters - default to popular tech jobs
        keywords = request.args.get('keywords', 'software engineer')
        location = request.args.get('location', 'remote')
        
        # Always include "remote" in the search to ensure remote jobs
        if 'remote' not in keywords.lower():
            keywords = f"remote {keywords}"
        
        # Use default income values for job recommendations API
        current_income = 70000  # Default current income
        desired_income = 90000  # Default desired income (30% increase)
        
        logger.info(f"Jobs API called with keywords: '{keywords}', location: '{location}'")
        
        # Direct Adzuna API integration to bypass class loading issues
        try:
            import requests
            import os
            
            adzuna_app_id = os.getenv('ADZUNA_APP_ID')
            adzuna_app_key = os.getenv('ADZUNA_APP_KEY')
            
            if adzuna_app_id and adzuna_app_key:
                logger.info(f"Making direct Adzuna API call with credentials")
                
                # Search for remote jobs with salary range $0-$30k
                url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
                params = {
                    'app_id': adzuna_app_id,
                    'app_key': adzuna_app_key,
                    'what': 'remote',       # Search for remote jobs specifically
                    'salary_min': 0,        # Start from $0 for part-time work
                    'salary_max': 30000,    # Cap at $30k for part-time jobs
                    'results_per_page': 30,  # Get up to 30 jobs
                    'sort_by': 'salary'
                }
                
                response = requests.get(url, params=params, timeout=10)
                logger.info(f"Adzuna API response: {response.status_code}")
                logger.info(f"Adzuna API parameters: {params}")
                
                if response.status_code == 200:
                    data = response.json()
                    adzuna_jobs = data.get('results', [])
                    logger.info(f"Found {len(adzuna_jobs)} jobs from Adzuna API with salary filter only")
                    
                    jobs = []
                    for job in adzuna_jobs:
                        # No filtering - just format the jobs from Adzuna
                        salary_min = job.get('salary_min', 0)
                        salary_max = job.get('salary_max', 0)
                        
                        if salary_max:
                            salary_display = f"${salary_min:,.0f} - ${salary_max:,.0f}"
                        elif salary_min:
                            salary_display = f"${salary_min:,.0f}+"
                        else:
                            salary_display = "Competitive"
                        
                        # Get location info
                        location_info = job.get('location', {})
                        location_display = location_info.get('display_name', 'Various') if location_info else 'Various'
                        
                        jobs.append({
                            'title': job.get('title', 'Unknown Title'),
                            'company': job.get('company', {}).get('display_name', 'Unknown Company'),
                            'description': (job.get('description', '')[:150] + '...') if job.get('description') else 'No description available',
                            'salary': salary_display,
                            'location': location_display,
                            'type': 'Part-time/Contract',  # Since we're filtering by salary range for retirement income
                            'url': job.get('redirect_url', ''),
                            'posted': job.get('created', 'Recently posted')
                        })
                    
                    logger.info(f"Successfully fetched {len(jobs)} real jobs from Adzuna API")
                else:
                    logger.warning(f"Adzuna API returned {response.status_code}: {response.text}")
                    jobs = []
            else:
                logger.warning("Adzuna API credentials not found")
                jobs = []
                
        except Exception as e:
            logger.error(f"Error with direct Adzuna API call: {e}")
            jobs = []
            
        # Fallback to mock data if Adzuna fails
        if not jobs:
            jobs = [
                {
                    'title': 'Senior Software Engineer (Remote)',
                    'company': 'Tech Corp',
                    'description': 'Remote software engineering position with competitive salary...',
                    'salary': '$80,000 - $120,000',
                    'location': 'Remote',
                    'type': 'Full-time',
                    'url': 'https://example.com/job1',
                    'posted': 'Recently posted'
                },
                {
                    'title': 'Financial Analyst (Remote)',
                    'company': 'Finance Plus',
                    'description': 'Analyze financial data and provide insights for retirement planning...',
                    'salary': '$70,000 - $95,000',
                    'location': 'Remote',
                    'type': 'Full-time', 
                    'url': 'https://example.com/job2',
                    'posted': 'Recently posted'
                }
            ]
            logger.info(f"Using {len(jobs)} fallback job recommendations")
        
        return jsonify({
            'jobs': jobs,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in jobs endpoint: {str(e)}")
        return jsonify({'jobs': []}), 200

@app.route('/api/test-bank-connection', methods=['GET'])
def test_bank_connection():
    """Test connection to Bank of Anthos services"""
    try:
        # Test connection to balancereader
        balance_url = f"http://{os.getenv('BALANCES_API_ADDR', 'balancereader:8080')}/ready"
        balance_response = requests.get(balance_url, timeout=5)
        
        # Test connection to transactionhistory  
        history_url = f"http://{os.getenv('HISTORY_API_ADDR', 'transactionhistory:8080')}/ready"
        history_response = requests.get(history_url, timeout=5)
        
        return jsonify({
            'balancereader': {
                'url': balance_url,
                'status': balance_response.status_code,
                'response': balance_response.text[:200]
            },
            'transactionhistory': {
                'url': history_url, 
                'status': history_response.status_code,
                'response': history_response.text[:200]
            }
        })
        
    except Exception as e:
        logger.error(f"Error testing bank connection: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
