/*
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// Dashboard JavaScript functionality
class RetirementDashboard {
    constructor() {
        this.projectionChart = null;
        this.init();
    }

    init() {
        console.log('Initializing Retirement Dashboard...');
        this.bindEvents();
        this.initializeTooltips();
        this.animateCounters();
    }

    bindEvents() {
        // Scenario calculator form
        const scenarioForm = document.getElementById('scenarioForm');
        if (scenarioForm) {
            scenarioForm.addEventListener('submit', this.handleScenarioCalculation.bind(this));
        }

        // Goal setting form
        const goalForm = document.getElementById('goalForm');
        if (goalForm) {
            goalForm.addEventListener('submit', this.handleGoalSetting.bind(this));
        }

        // Job refresh button
        const refreshJobsBtn = document.getElementById('refreshJobs');
        if (refreshJobsBtn) {
            refreshJobsBtn.addEventListener('click', this.refreshJobRecommendations.bind(this));
        }

        // Input validation
        this.setupInputValidation();
    }

    async handleScenarioCalculation(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.innerHTML = '<i class="material-icons me-1">hourglass_empty</i>Calculating...';
        submitBtn.disabled = true;
        
        try {
            const formData = new FormData(form);
            const data = {
                current_age: parseInt(formData.get('currentAge') || document.getElementById('currentAge').value),
                retirement_age: parseInt(formData.get('retirementAge') || document.getElementById('retirementAge').value),
                monthly_savings: parseFloat(formData.get('monthlySavings') || document.getElementById('monthlySavings').value),
                expected_return: parseFloat(formData.get('expectedReturn') || document.getElementById('expectedReturn').value),
                current_savings: this.getCurrentSavings()
            };

            const response = await fetch('/api/scenario', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.displayProjectionResults(result.projections, result.ai_insights);
            this.showSuccess('Projections calculated successfully!');
            
        } catch (error) {
            console.error('Error calculating scenario:', error);
            this.showError('Failed to calculate retirement scenario. Please try again.');
        } finally {
            // Restore button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    async handleGoalSetting(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.innerHTML = '<i class="material-icons me-1">hourglass_empty</i>Setting Goal...';
        submitBtn.disabled = true;
        
        try {
            const formData = new FormData(form);
            const currentAge = parseInt(document.getElementById('currentAge')?.value || 30);
            const targetAge = parseInt(formData.get('targetAge') || document.getElementById('targetAge').value);
            
            const data = {
                target_amount: parseFloat(formData.get('targetAmount') || document.getElementById('targetAmount').value),
                target_age: targetAge,
                current_savings: this.getCurrentSavings(),
                years_remaining: Math.max(0, targetAge - currentAge)
            };

            const response = await fetch('/api/goals', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.displayGoalRecommendations(result.recommendations);
            this.showSuccess('Retirement goal set successfully!');
            
        } catch (error) {
            console.error('Error setting goal:', error);
            this.showError('Failed to set retirement goal. Please try again.');
        } finally {
            // Restore button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }

    displayProjectionResults(projections, aiInsights) {
        // Update result values
        const totalSavings = document.getElementById('totalSavings');
        const monthlyIncome = document.getElementById('monthlyIncome');
        const replacementRatio = document.getElementById('replacementRatio');

        if (totalSavings) {
            this.animateValue(totalSavings, 0, projections.total_savings, 1000, (value) => 
                '$' + this.formatCurrency(value));
        }

        if (monthlyIncome) {
            this.animateValue(monthlyIncome, 0, projections.monthly_income, 1000, (value) => 
                '$' + this.formatCurrency(value));
        }

        if (replacementRatio) {
            this.animateValue(replacementRatio, 0, projections.replacement_ratio, 1000, (value) => 
                Math.round(value) + '%');
        }

        // Show results section
        const resultsSection = document.getElementById('projectionResults');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Create or update chart
        this.createProjectionChart(projections);

        // Display AI insights if available
        if (aiInsights) {
            this.displayAIInsights(aiInsights);
        }
    }

    createProjectionChart(projections) {
        const canvas = document.getElementById('projectionChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        // Destroy existing chart if it exists
        if (this.projectionChart) {
            this.projectionChart.destroy();
        }

        const data = {
            labels: ['Total Contributions', 'Investment Growth'],
            datasets: [{
                data: [
                    projections.total_contributions || 0,
                    projections.investment_growth || 0
                ],
                backgroundColor: [
                    '#007bff',
                    '#28a745'
                ],
                borderWidth: 0,
                hoverBackgroundColor: [
                    '#0056b3',
                    '#1e7e34'
                ]
            }]
        };

        this.projectionChart = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const percentage = ((value / (projections.total_savings || 1)) * 100).toFixed(1);
                                return `${label}: $${value.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    displayGoalRecommendations(recommendations) {
        // Create a toast or modal to show recommendations
        const toast = this.createToast('Goal Recommendations', this.formatRecommendations(recommendations));
        document.body.appendChild(toast);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 10000);
    }

    formatRecommendations(recommendations) {
        if (!recommendations || !Array.isArray(recommendations)) {
            return 'No specific recommendations available.';
        }

        return recommendations.map(rec => 
            `<strong>${rec.title}</strong>: ${rec.description} (${rec.priority} priority)`
        ).join('<br>');
    }

    async refreshJobRecommendations() {
        try {
            const currentIncome = this.getCurrentIncome();
            const desiredIncome = currentIncome * 1.3; // 30% increase

            const response = await fetch(`/api/jobs?current_income=${currentIncome}&desired_income=${desiredIncome}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const jobs = await response.json();
            this.updateJobsDisplay(jobs);
            this.showSuccess('Job recommendations refreshed!');
            
        } catch (error) {
            console.error('Error refreshing jobs:', error);
            this.showError('Failed to refresh job recommendations.');
        }
    }

    updateJobsDisplay(jobData) {
        // Update job cards in the modal
        const jobsContainer = document.querySelector('#jobsModal .modal-body .row');
        if (!jobsContainer) return;

        // Clear existing jobs
        jobsContainer.innerHTML = '';

        // Add new jobs
        jobData.jobs.forEach(job => {
            const jobCard = this.createJobCard(job);
            jobsContainer.appendChild(jobCard);
        });
    }

    createJobCard(job) {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-3';
        
        col.innerHTML = `
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="card-title">${job.title}</h6>
                    <p class="card-text">
                        <strong>${job.company}</strong><br>
                        <small class="text-muted">${job.location}</small>
                    </p>
                    <p class="card-text">
                        <strong class="text-success">$${this.formatCurrency(job.avg_salary)}</strong>
                        ${job.income_increase_percent > 0 ? 
                            `<span class="badge bg-success">+${job.income_increase_percent}%</span>` : ''}
                    </p>
                    <p class="card-text small">${job.description.substring(0, 100)}...</p>
                    ${job.url ? 
                        `<a href="${job.url}" target="_blank" class="btn btn-sm btn-outline-primary">View Job</a>` : ''}
                </div>
            </div>
        `;
        
        return col;
    }

    setupInputValidation() {
        // Add real-time validation for number inputs
        const numberInputs = document.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('input', this.validateNumberInput.bind(this));
        });
    }

    validateNumberInput(event) {
        const input = event.target;
        const value = parseFloat(input.value);
        const min = parseFloat(input.min) || 0;
        const max = parseFloat(input.max) || Infinity;

        if (isNaN(value) || value < min || value > max) {
            input.setCustomValidity('Please enter a valid number within the allowed range.');
        } else {
            input.setCustomValidity('');
        }
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips if available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    }

    animateCounters() {
        // Animate numeric values on page load
        const counters = document.querySelectorAll('.metric-card h4');
        counters.forEach(counter => {
            const text = counter.textContent;
            const match = text.match(/[\d,]+/);
            if (match) {
                const value = parseFloat(match[0].replace(/,/g, ''));
                this.animateValue(counter, 0, value, 1500, (val) => text.replace(match[0], this.formatCurrency(val)));
            }
        });
    }

    animateValue(element, start, end, duration, formatter) {
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const current = progress * (end - start) + start;
            element.textContent = formatter ? formatter(current) : Math.round(current);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }

    getCurrentSavings() {
        // Extract current savings from the page
        const balanceElement = document.querySelector('.text-success h4');
        if (balanceElement) {
            const text = balanceElement.textContent;
            const match = text.match(/\$([\d,]+)/);
            if (match) {
                return parseFloat(match[1].replace(/,/g, ''));
            }
        }
        return 0;
    }

    getCurrentIncome() {
        // Extract current income estimate
        const incomeElement = document.querySelector('[data-income]');
        if (incomeElement) {
            return parseFloat(incomeElement.dataset.income);
        }
        return 50000; // Default estimate
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        const toast = this.createToast(type === 'error' ? 'Error' : 'Success', message, type);
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    createToast(title, message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'success'} border-0`;
        toast.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        return toast;
    }

    displayAIInsights(insights) {
        if (!insights) return;
        
        // Create insights section if it doesn't exist
        let insightsSection = document.getElementById('aiInsights');
        if (!insightsSection) {
            insightsSection = document.createElement('div');
            insightsSection.id = 'aiInsights';
            insightsSection.className = 'mt-4';
            
            const resultsSection = document.getElementById('projectionResults');
            if (resultsSection) {
                resultsSection.appendChild(insightsSection);
            }
        }
        
        insightsSection.innerHTML = `
            <div class="alert alert-info">
                <h6><i class="material-icons me-2">psychology</i>AI Insights</h6>
                <p><strong>Viability:</strong> ${insights.viability}</p>
                ${insights.suggestions ? `<p><strong>Suggestions:</strong> ${insights.suggestions.join(', ')}</p>` : ''}
                ${insights.risks ? `<p><strong>Risks:</strong> ${insights.risks.join(', ')}</p>` : ''}
            </div>
        `;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new RetirementDashboard();
});
