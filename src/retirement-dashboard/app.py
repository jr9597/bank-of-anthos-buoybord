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

"""Retirement Dashboard Service for Bank of Anthos"""

import os
import logging
import requests
import jwt
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask, request, render_template, jsonify, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

# Local imports
from modules.ai_advisor import AIAdvisor
from modules.job_recommendations import JobRecommendations
from modules.financial_analyzer import FinancialAnalyzer

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize service modules
ai_advisor = AIAdvisor()
job_recommendations = JobRecommendations()
financial_analyzer = FinancialAnalyzer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes"""
    return {'status': 'healthy', 'service': 'retirement-dashboard'}, 200

@app.route('/version', methods=['GET'])
def version():
    """Service version endpoint"""
    return os.environ.get('VERSION', '1.0.0'), 200

@app.route('/', methods=['GET'])
def dashboard():
    """Main retirement dashboard page"""
    try:
        # Verify user authentication
        auth_header = request.headers.get('Authorization')
        token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # Fallback to cookie for browser requests
            token = request.cookies.get('token')
        
        if not token:
            logger.warning("No token found, redirecting to login")
            return redirect(f"{os.getenv('FRONTEND_URL', 'http://localhost:8080')}/login")
        
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
        job_recommendations_data = job_recommendations.get_job_recommendations(
            financial_data.get('current_income', 0),
            financial_data.get('desired_income', 0)
        )
        
        return render_template('dashboard.html',
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

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """API endpoint to get fresh job recommendations"""
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
        
        # Get query parameters
        current_income = request.args.get('current_income', 0, type=int)
        desired_income = request.args.get('desired_income', 0, type=int)
        location = request.args.get('location', 'United States')
        
        jobs = job_recommendations.get_job_recommendations(
            current_income, desired_income, location
        )
        
        return jsonify(jobs)
        
    except Exception as e:
        logger.error(f"Error getting jobs: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_user_financial_data(token, account_id):
    """Fetch user financial data from Bank of Anthos services"""
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
        balance_response = requests.get(balance_url, headers=headers, timeout=5)
        if balance_response.status_code == 200:
            financial_data['current_balance'] = balance_response.json()
        
        # Get transaction history
        history_url = f"http://{os.getenv('HISTORY_API_ADDR', 'transactionhistory:8080')}/transactions/{account_id}"
        history_response = requests.get(history_url, headers=headers, timeout=5)
        if history_response.status_code == 200:
            transactions = history_response.json()
            financial_data['transactions'] = transactions
            
            # Calculate income and expenses from transaction history
            income, expenses = financial_analyzer.calculate_income_expenses(transactions, account_id)
            financial_data['monthly_income'] = income
            financial_data['monthly_expenses'] = expenses
            financial_data['current_income'] = income * 12  # Annual income
            financial_data['desired_income'] = financial_data['current_income'] * 1.3  # 30% increase
        
    except requests.RequestException as e:
        logger.error(f"Error fetching financial data: {str(e)}")
    
    return financial_data

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
