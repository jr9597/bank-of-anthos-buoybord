# Retirement Dashboard Microservice

An AI-powered retirement planning dashboard that extends Bank of Anthos with comprehensive financial planning capabilities.

## 🎯 Overview

The Retirement Dashboard is a modern microservice that integrates with the Bank of Anthos ecosystem to provide users with:

- **Personalized Retirement Planning**: AI-powered advice based on real financial data
- **Job Market Intelligence**: Real-time remote job opportunities for supplemental income
- **Financial Projections**: Interactive charts and goal tracking with compound growth modeling
- **Conversational AI**: Chat interface that understands user's financial context

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                Retirement Dashboard                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   AI Advisor    │  │ Job Recommender │  │  Financial  │  │
│  │  (Gemini API)   │  │  (Adzuna API)   │  │  Analyzer   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Flask Web Application                      │  │
│  │  • JWT Authentication                                  │  │
│  │  • RESTful APIs                                        │  │
│  │  • Modern UI (Tailwind CSS + Chart.js)                │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Bank of Anthos Microservices                   │
│                                                             │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ userservice │  │  balancereader  │  │transactionhistory│  │
│  │(Auth & User)│  │ (Real Balance)  │  │ (Transactions)  │  │
│  └─────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

- **`app.py`**: Main Flask application with authentication and API endpoints
- **`modules/ai_advisor.py`**: Google Gemini integration for personalized advice
- **`modules/job_recommendations.py`**: Adzuna API integration for job market data
- **`modules/financial_analyzer.py`**: Financial calculations and projections
- **`templates/`**: HTML templates with modern UI components
- **`k8s/`**: Kubernetes deployment manifests

## 🚀 Features

### 📊 Financial Analysis
- **Real-time Data**: Integrates with Bank of Anthos transaction history
- **Income/Expense Tracking**: Automated categorization from bank transactions
- **Savings Rate Calculation**: Monthly savings trends and patterns
- **Retirement Projections**: 5% CAGR compound growth modeling

### 🤖 AI-Powered Advice
- **Personalized Recommendations**: Context-aware advice using Google Gemini
- **Financial Context**: AI knows user's balance, income, expenses, and goals
- **Job Market Awareness**: AI can reference current job opportunities
- **Conversational Interface**: Natural language interaction with financial expertise

### 💼 Job Recommendations
- **Remote-First**: Focus on remote work opportunities for flexibility
- **Salary Range**: $0-$30k range for part-time supplemental income
- **Real-time Data**: Live job market data from Adzuna API
- **Retirement-Focused**: Jobs selected to boost retirement savings

### 📈 Interactive Dashboard
- **Financial Metrics**: Current balance, monthly income/expenses, savings rate
- **Retirement Goals**: Progress tracking toward $1.5M retirement target
- **Projection Charts**: Visual retirement trajectory with compound growth
- **Responsive Design**: Modern UI that works on all devices

## 🔧 Technical Implementation

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Python Flask | Web framework and API server |
| **AI** | Google Gemini 1.5-flash | Natural language processing and advice |
| **Jobs API** | Adzuna API | Real-time job market data |
| **Frontend** | HTML5 + Tailwind CSS | Modern, responsive UI |
| **Charts** | Chart.js | Interactive financial visualizations |
| **Auth** | JWT | Integration with Bank of Anthos auth |
| **Database** | Bank of Anthos PostgreSQL | Existing user and transaction data |
| **Deployment** | Kubernetes + GKE | Cloud-native deployment |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard page |
| `/api/chat` | POST | AI chat for retirement advice |
| `/api/jobs` | GET | Job recommendations from Adzuna |
| `/health` | GET | Health check for Kubernetes |
| `/version` | GET | Service version info |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_AI_API_KEY` | Google Gemini API key | Yes |
| `ADZUNA_APP_ID` | Adzuna application ID | Yes |
| `ADZUNA_APP_KEY` | Adzuna API key | Yes |
| `BANK_NAME` | Bank name for branding | No |
| `FRONTEND_URL` | Frontend service URL | No |

## 🚀 Deployment

### Prerequisites

1. **Bank of Anthos**: Must be deployed and running
2. **API Keys**: 
   - Google AI API key from [Google AI Studio](https://aistudio.google.com/)
   - Adzuna API credentials from [Adzuna Developer](https://developer.adzuna.com/)
3. **Kubernetes Cluster**: GKE or any Kubernetes cluster

### Quick Deploy

1. **Create Secrets**:
   ```bash
   kubectl create secret generic retirement-dashboard-secrets \
     --from-literal=GOOGLE_AI_API_KEY=your_gemini_key \
     --from-literal=ADZUNA_APP_ID=your_adzuna_id \
     --from-literal=ADZUNA_APP_KEY=your_adzuna_key
   ```

2. **Deploy the Service**:
   ```bash
   kubectl apply -f src/retirement-dashboard/minimal-deployment.yaml
   ```

3. **Access the Dashboard**:
   - Get the external IP: `kubectl get service retirement-dashboard`
   - Access via Bank of Anthos frontend (recommended)
   - Or directly via the service IP

### Development Setup

1. **Local Development**:
   ```bash
   cd src/retirement-dashboard
   pip install -r requirements.txt
   export GOOGLE_AI_API_KEY=your_key
   export ADZUNA_APP_ID=your_id
   export ADZUNA_APP_KEY=your_key
   python app.py
   ```

2. **Docker Build**:
   ```bash
   docker build -t retirement-dashboard .
   docker run -p 8080:8080 retirement-dashboard
   ```

## 📊 Usage Examples

### Financial Analysis
The dashboard automatically analyzes user transactions to calculate:
- **Monthly Income**: Credits to the account (salary, transfers in)
- **Monthly Expenses**: Debits from the account (purchases, transfers out)  
- **Savings Rate**: Income minus expenses
- **Retirement Trajectory**: Compound growth projections at 5% CAGR

### AI Chat Examples
- *"How much should I save monthly to retire by 65?"*
- *"What part-time jobs could help boost my retirement savings?"*
- *"Is my current savings rate sufficient for my retirement goals?"*
- *"Should I consider a career change to increase my retirement fund?"*

### Job Recommendations
- Automatically fetches remote jobs in $0-$30k salary range
- Focuses on part-time and contract opportunities
- Updates in real-time from Adzuna job market data
- Clickable links to apply directly to opportunities

## 🔐 Security

### Authentication
- Inherits JWT authentication from Bank of Anthos
- Validates tokens using Bank of Anthos public key
- Graceful fallback to demo mode for unauthenticated users

### API Key Management
- All API keys stored in Kubernetes Secrets
- No hardcoded credentials in source code
- Environment-based configuration

### Data Privacy
- No financial data stored outside Bank of Anthos
- API calls use user data only for real-time calculations
- No persistent storage of user data in retirement dashboard

## 🧪 Testing

### Health Checks
```bash
curl http://your-service-ip/health
# Returns: {"status": "healthy", "service": "retirement-dashboard"}
```

### API Testing
```bash
# Test job recommendations
curl "http://your-service-ip/api/jobs?keywords=developer"

# Test AI chat (requires authentication)
curl -X POST "http://your-service-ip/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How can I improve my retirement savings?"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **AI Not Working**: Check `GOOGLE_AI_API_KEY` in secrets
2. **No Jobs Loading**: Verify `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`
3. **Zero Financial Data**: Ensure Bank of Anthos services are accessible
4. **Authentication Errors**: Check JWT token validation and public key

### Debug Logs
```bash
kubectl logs deployment/retirement-dashboard
```

### Resource Issues
The service requires minimal resources:
- **CPU**: 50m request, 200m limit
- **Memory**: 64Mi request, 256Mi limit

## 🔮 Future Enhancements

- **Investment Advice**: Integration with investment platforms
- **Risk Assessment**: Monte Carlo simulations for retirement planning
- **Goal Tracking**: Multiple retirement scenarios and goals
- **Social Features**: Retirement planning communities
- **Advanced Analytics**: More sophisticated financial modeling

## 📄 License

Copyright 2025 Google LLC. Licensed under the Apache License, Version 2.0.

## 🤝 Contributing

This microservice demonstrates modern patterns for extending existing applications with AI capabilities. It showcases:

- **Microservice Integration**: How to add new capabilities to existing systems
- **AI Integration**: Practical use of Google Gemini in business applications  
- **External API Integration**: Real-time data from third-party services
- **Modern UI/UX**: Contemporary web development practices
- **Cloud-Native Deployment**: Kubernetes and GKE best practices

For questions or contributions, please follow the Bank of Anthos contribution guidelines.