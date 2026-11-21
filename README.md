# Employee Attrition Survival & Pay Equity Analytics

A people analytics pipeline combining compa-ratio compensation audits, Kaplan-Meier tenure survival curves, and attrition risk scoring for technical teams.

## Problem Context
Replacing senior engineers and analysts is expensive, yet compensation compression and promotion delays often go unnoticed until resignations happen. This project audits pay parity against band midpoints and models retention across tenure milestones.

## Files
- `workforce_equity_attrition.sql`: HRIS SQL query calculating compa-ratios, internal pay percentiles, and promotion lag alerts.
- `attrition_survival_engine.py`: Estimates Kaplan-Meier survival probabilities across tenure windows and scores voluntary exit risk.
- `requirements.txt`: Python dependencies.

## How It Works
1. **Compa-Ratio Audit:** Compares base salary against role/level band midpoints (`Salary / Band_Midpoint`) to flag underpaid high performers.
2. **Tenure Survival Curves:** Tracks cumulative retention rates at 6, 12, 24, and 36 months to spot tenure cliff drop-offs.
3. **Risk Drivers:** Evaluates how pay lag, time since last promotion, and sustained overtime correlate with exits.

## Run Locally

    git clone https://github.com/puneetgoswami1/employee-flight-risk-workforce-analytics.git
    cd employee-flight-risk-workforce-analytics
    pip install -r requirements.txt
    python attrition_survival_engine.py
