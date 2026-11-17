-- =====================================================================
-- PEOPLE ANALYTICS: PAY EQUITY (COMPA-RATIO) & ATTRITION AUDIT
-- Author: Puneet Goswami
-- Description: Evaluates internal salary band alignment, promotion lag,
--              and historical voluntary attrition rates across technical roles.
-- =====================================================================

WITH active_and_termed_roster AS (
    SELECT 
        e.employee_id,
        e.department,
        e.role_family,
        e.job_level,
        e.location_hub,
        e.hire_date,
        e.termination_date,
        e.termination_reason,
        e.base_salary_usd,
        e.last_promotion_date,
        e.performance_rating, -- 1 to 5 scale
        b.band_min_usd,
        b.band_midpoint_usd,
        b.band_max_usd,
        
        -- Compa-Ratio: Employee salary relative to market band midpoint (1.00 = at market)
        ROUND(e.base_salary_usd / NULLIF(b.band_midpoint_usd, 0), 3) AS compa_ratio,
        
        -- Total tenure in months
        DATEDIFF('month', e.hire_date, COALESCE(e.termination_date, CURRENT_DATE)) AS tenure_months,
        
        -- Months elapsed since last role promotion
        DATEDIFF('month', COALESCE(e.last_promotion_date, e.hire_date), COALESCE(e.termination_date, CURRENT_DATE)) AS months_since_promotion,
        
        -- Voluntary attrition flag
        CASE 
            WHEN e.termination_date IS NOT NULL AND e.termination_reason = 'VOLUNTARY' THEN 1 
            ELSE 0 
        END AS is_voluntary_attrition
    FROM hris_dw.dim_employees e
    JOIN hris_dw.dim_compensation_bands b 
      ON e.role_family = b.role_family 
     AND e.job_level = b.job_level 
     AND e.location_hub = b.location_hub
    WHERE e.hire_date >= CURRENT_DATE - INTERVAL '4 YEARS'
),

pay_band_equity_metrics AS (
    SELECT 
        employee_id,
        department,
        role_family,
        job_level,
        base_salary_usd,
        compa_ratio,
        tenure_months,
        months_since_promotion,
        performance_rating,
        is_voluntary_attrition,
        
        -- Peer percentile rank within exact same role and level
        ROUND(PERCENT_RANK() OVER (
            PARTITION BY role_family, job_level 
            ORDER BY base_salary_usd ASC
        )::NUMERIC, 3) AS internal_pay_percentile,
        
        -- Flag pay compression risk for high performers paid below 88% of band midpoint
        CASE 
            WHEN compa_ratio < 0.88 AND performance_rating >= 4 THEN 'HIGH_COMPRESSION_RISK'
            WHEN compa_ratio < 0.92 THEN 'BELOW_BAND_MIDPOINT'
            ELSE 'MARKET_ALIGNED'
        END AS compensation_equity_status
    FROM active_and_termed_roster
)

SELECT 
    role_family,
    job_level,
    COUNT(employee_id) AS total_headcount,
    SUM(is_voluntary_attrition) AS voluntary_exits,
    ROUND((SUM(is_voluntary_attrition) * 100.0) / COUNT(employee_id), 2) AS voluntary_attrition_rate_pct,
    ROUND(AVG(compa_ratio), 3) AS avg_compa_ratio,
    ROUND(AVG(tenure_months), 1) AS avg_tenure_months,
    ROUND(AVG(months_since_promotion), 1) AS avg_months_since_promo,
    SUM(CASE WHEN compensation_equity_status = 'HIGH_COMPRESSION_RISK' THEN 1 ELSE 0 END) AS high_performer_compression_count
FROM pay_band_equity_metrics
GROUP BY role_family, job_level
ORDER BY voluntary_attrition_rate_pct DESC, high_performer_compression_count DESC;