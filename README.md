# Employee Flight Risk & Workforce Equity Analytics

A people analytics and workforce retention framework combining compa-ratio pay equity auditing, Kaplan-Meier tenure survival curves, and predictive attrition modeling for core technical roles.

## Overview
Unplanned attrition among senior engineering and analytics talent creates severe operational disruption and high replacement costs. This project audits internal compensation parity against market midpoints, tracks employee survival rates across tenure milestones, and flags flight-risk cohorts before resignation events occur.

## Project Structure
- `workforce_equity_attrition.sql`: Production HRIS SQL CTE pipeline calculating compa-ratios, internal pay percentiles, promotion lag, and high-performer pay compression alerts.
- `attrition_survival_engine.py`: Python statistical engine estimating discrete-time Kaplan-Meier survival probabilities and training a standardized logistic risk classifier.
- `requirements.txt`: Python package dependencies.

## Key Workforce Metrics
1. **Compa-Ratio Pay Equity:** Measures individual base compensation relative to role/level band midpoints (`Salary / Band_Midpoint`) to isolate pay compression among top performers.
2. **Kaplan-Meier Tenure Survival:** Tracks cumulative retention probability across 6-, 12-, 24-, and 36-month milestones to identify critical tenure cliff windows.
3. **Attrition Risk Drivers:** Quantifies the joint impact of compensation lag, promotion stagnation, and sustained overtime load on voluntary exit propensity.

## How to Run

```bash
# Clone the repository
git clone [https://github.com/puneetgoswami1/employee-flight-risk-workforce-analytics.git](https://github.com/puneetgoswami1/employee-flight-risk-workforce-analytics.git)
cd employee-flight-risk-workforce-analytics

# Install dependencies
pip install -r requirements.txt

# Run workforce analytics engine
python attrition_survival_engine.py