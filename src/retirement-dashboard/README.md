# Retirement Dashboard

An AI-powered retirement planning microservice for Bank of Anthos, built for the GKE Turns 10 Hackathon.

## Overview

The Retirement Dashboard is a modern microservice that enhances the Bank of Anthos application with intelligent retirement planning capabilities. It analyzes user financial data and provides personalized advice using Google AI models, while also offering job recommendations to help users increase their income potential.

## Features

### 🤖 AI-Powered Financial Advisor
- **Google Gemini Integration**: Leverages Google's advanced AI models for personalized retirement advice
- **Financial Health Analysis**: Comprehensive assessment of savings rate, emergency funds, and spending patterns
- **Scenario Planning**: Interactive retirement projections with different savings and investment scenarios
- **Goal Setting**: AI-driven recommendations for achieving specific retirement targets

### 💼 Career Growth Opportunities
- **Adzuna API Integration**: Real-time job recommendations based on income goals
- **Skill Gap Analysis**: Identification of in-demand skills for career advancement
- **Career Path Suggestions**: Structured paths for income growth with timelines and requirements
- **Income Potential Calculator**: Analysis of salary increase opportunities

### 📊 Interactive Dashboard
- **Modern UI**: Responsive design with Bootstrap 5 and Material Icons
- **Real-time Charts**: Dynamic visualizations using Chart.js
- **Financial Metrics**: Key performance indicators for retirement readiness
- **Mobile-Friendly**: Optimized for desktop, tablet, and mobile devices

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Retirement Dashboard                      │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Flask + Jinja2)                                 │
│  ├── Dashboard UI                                          │
│  ├── Scenario Calculator                                   │
│  └── Goal Setting Interface                                │
├─────────────────────────────────────────────────────────────┤
│  Backend Services                                          │
│  ├── AI Advisor (Google Gemini)                           │
│  ├── Job Recommendations (Adzuna API)                     │
│  └── Financial Analyzer                                   │
├─────────────────────────────────────────────────────────────┤
│  External Integrations                                     │
│  ├── Bank of Anthos APIs                                  │
│  │   ├── Balance Reader                                   │
│  │   └── Transaction History                              │
│  ├── Google AI Models                                     │
│  └── Adzuna Job Search API                                │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Framework**: Flask (Python 3.11)
- **AI Integration**: Google Generative AI (Gemini)
- **Job API**: Adzuna API
- **Frontend**: Bootstrap 5, Material Icons, Chart.js
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **Development**: Skaffold
- **Authentication**: JWT tokens from Bank of Anthos

## Development Setup

### Prerequisites
- Docker
- kubectl
- Skaffold
- Google Cloud Project with APIs enabled
- API Keys (Google AI, Adzuna)

### Local Development

1. **Clone the repository**:
   ```bash
   cd src/retirement-dashboard
   ```

2. **Set up environment variables**:
   ```bash
   export GOOGLE_AI_API_KEY="your-google-ai-api-key"
   export ADZUNA_APP_ID="your-adzuna-app-id"
   export ADZUNA_APP_KEY="your-adzuna-app-key"
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run locally**:
   ```bash
   python app.py
   ```

### Skaffold Development

1. **Start development mode**:
   ```bash
   skaffold dev --profile development
   ```

2. **Access the dashboard**:
   - Navigate to Bank of Anthos frontend
   - Click the "Retirement Dashboard" button (after integration)
   - Or access directly at `http://localhost:8000`

## Deployment

### Kubernetes Secrets

1. **Create secrets for API keys**:
   ```bash
   kubectl create secret generic retirement-dashboard-secrets \
     --from-literal=google-ai-api-key="your-google-ai-api-key" \
     --from-literal=adzuna-app-id="your-adzuna-app-id" \
     --from-literal=adzuna-app-key="your-adzuna-app-key"
   ```

### Production Deployment

1. **Deploy to staging**:
   ```bash
   skaffold run --profile staging
   ```

2. **Deploy to production**:
   ```bash
   skaffold run --profile production
   ```

## API Endpoints

### Web Routes
- `GET /` - Main dashboard page
- `GET /health` - Health check endpoint
- `GET /version` - Service version

### API Routes
- `POST /api/scenario` - Calculate retirement projections
- `POST /api/goals` - Set retirement goals
- `GET /api/jobs` - Get job recommendations

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_AI_API_KEY` | Google AI API key for Gemini | Optional* |
| `ADZUNA_APP_ID` | Adzuna API application ID | Optional* |
| `ADZUNA_APP_KEY` | Adzuna API key | Optional* |
| `BALANCES_API_ADDR` | Balance reader service address | Yes |
| `HISTORY_API_ADDR` | Transaction history service address | Yes |
| `FRONTEND_URL` | Bank of Anthos frontend URL | Yes |
| `PORT` | Service port | No (default: 8000) |

*If not provided, the service will use mock data for demonstrations.

## Integration with Bank of Anthos

The retirement dashboard integrates seamlessly with the existing Bank of Anthos architecture:

1. **Authentication**: Uses existing JWT tokens from the userservice
2. **Data Access**: Connects to balance-reader and transaction-history services
3. **Frontend Integration**: Accessible via a button on the main Bank of Anthos homepage

## AI Features

### Google Gemini Integration
- **Retirement Advice**: Analyzes financial patterns and provides personalized recommendations
- **Scenario Analysis**: Evaluates different retirement scenarios with risk assessments
- **Goal Recommendations**: Suggests actionable steps for achieving retirement targets

### Adzuna Job Recommendations
- **Income-Based Search**: Finds jobs matching current and desired income levels
- **Skill Analysis**: Identifies high-value skills in the job market
- **Career Progression**: Maps potential career paths for income growth

## Monitoring and Observability

- **Health Checks**: Kubernetes readiness and liveness probes
- **Logging**: Structured logging with correlation IDs
- **Metrics**: Resource usage and performance monitoring
- **Tracing**: Request tracing for debugging

## Security

- **Authentication**: JWT token validation
- **Authorization**: User-specific data access
- **Security Context**: Non-root container execution
- **Secrets Management**: Kubernetes secrets for API keys
- **Input Validation**: Comprehensive input sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

Copyright 2025 Google LLC. Licensed under the Apache License, Version 2.0.

## Hackathon Submission

This microservice was created for the **GKE Turns 10 Hackathon** with the following objectives:

- ✅ **Enhanced Bank of Anthos** with AI-powered retirement planning
- ✅ **Google AI Integration** using Gemini models
- ✅ **External API Integration** with Adzuna for job recommendations
- ✅ **Kubernetes Deployment** on GKE
- ✅ **Modern UI/UX** with responsive design
- ✅ **Production Ready** with proper monitoring and security

### Demo Features
- Real-time financial health analysis
- AI-powered retirement advice
- Interactive scenario planning
- Job market insights
- Career growth recommendations
