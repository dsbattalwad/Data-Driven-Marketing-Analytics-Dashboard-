-- ============================================================
-- Marketing Analytics Dashboard — SQL Query Library
-- Database: marketing_analytics
-- Tables: campaigns, daily_performance
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- TABLE SCHEMAS (for reference / SQLite / PostgreSQL)
-- ─────────────────────────────────────────────────────────────

/*
CREATE TABLE campaigns (
    Campaign_ID      TEXT PRIMARY KEY,
    Campaign_Name    TEXT,
    Channel          TEXT,
    Campaign_Type    TEXT,
    Start_Date       DATE,
    End_Date         DATE,
    Budget           NUMERIC,
    Impressions      INTEGER,
    Clicks           INTEGER,
    Conversions      INTEGER,
    Cost             NUMERIC,
    Revenue          NUMERIC,
    CTR              NUMERIC,
    Conversion_Rate  NUMERIC,
    CPC              NUMERIC,
    CPA              NUMERIC,
    ROAS             NUMERIC,
    Profit           NUMERIC
);

CREATE TABLE daily_performance (
    Date         DATE,
    Campaign_ID  TEXT,
    Channel      TEXT,
    Impressions  INTEGER,
    Clicks       INTEGER,
    Conversions  INTEGER,
    Cost         NUMERIC,
    Revenue      NUMERIC,
    Month        TEXT,
    Week         INTEGER
);
*/

-- ============================================================
-- SECTION 1: OVERALL KPI SUMMARY
-- ============================================================

-- Q1: High-level marketing performance snapshot
SELECT
    COUNT(DISTINCT Campaign_ID)                     AS Total_Campaigns,
    SUM(Impressions)                                AS Total_Impressions,
    SUM(Clicks)                                     AS Total_Clicks,
    SUM(Conversions)                                AS Total_Conversions,
    ROUND(SUM(Cost), 2)                             AS Total_Cost,
    ROUND(SUM(Revenue), 2)                          AS Total_Revenue,
    ROUND(SUM(Profit), 2)                           AS Total_Profit,
    ROUND(CAST(SUM(Clicks) AS REAL) / NULLIF(SUM(Impressions), 0) * 100, 2) AS Overall_CTR_Pct,
    ROUND(CAST(SUM(Conversions) AS REAL) / NULLIF(SUM(Clicks), 0) * 100, 2) AS Overall_Conv_Rate_Pct,
    ROUND(SUM(Revenue) / NULLIF(SUM(Cost), 0), 2)  AS Overall_ROAS
FROM campaigns;


-- ============================================================
-- SECTION 2: CHANNEL-WISE PERFORMANCE
-- ============================================================

-- Q2: KPIs grouped by channel
SELECT
    Channel,
    COUNT(*)                                         AS Campaigns,
    SUM(Impressions)                                 AS Impressions,
    SUM(Clicks)                                      AS Clicks,
    SUM(Conversions)                                 AS Conversions,
    ROUND(SUM(Cost), 2)                              AS Total_Cost,
    ROUND(SUM(Revenue), 2)                           AS Total_Revenue,
    ROUND(SUM(Revenue) - SUM(Cost), 2)               AS Total_Profit,
    ROUND(AVG(CTR) * 100, 2)                         AS Avg_CTR_Pct,
    ROUND(AVG(Conversion_Rate) * 100, 2)             AS Avg_Conv_Rate_Pct,
    ROUND(AVG(CPC), 2)                               AS Avg_CPC,
    ROUND(AVG(CPA), 2)                               AS Avg_CPA,
    ROUND(SUM(Revenue) / NULLIF(SUM(Cost), 0), 2)    AS Channel_ROAS
FROM campaigns
GROUP BY Channel
ORDER BY Channel_ROAS DESC;


-- Q3: Channel share of total spend (%)
SELECT
    Channel,
    ROUND(SUM(Cost), 2)                                                           AS Channel_Cost,
    ROUND(SUM(Cost) * 100.0 / (SELECT SUM(Cost) FROM campaigns), 2)               AS Cost_Share_Pct,
    ROUND(SUM(Revenue) * 100.0 / (SELECT SUM(Revenue) FROM campaigns), 2)         AS Revenue_Share_Pct
FROM campaigns
GROUP BY Channel
ORDER BY Cost_Share_Pct DESC;


-- ============================================================
-- SECTION 3: CAMPAIGN-LEVEL PERFORMANCE
-- ============================================================

-- Q4: Top 10 campaigns by revenue
SELECT
    Campaign_ID,
    Campaign_Name,
    Channel,
    Campaign_Type,
    ROUND(Cost, 2)     AS Cost,
    ROUND(Revenue, 2)  AS Revenue,
    ROUND(Profit, 2)   AS Profit,
    ROUND(ROAS, 2)     AS ROAS
FROM campaigns
ORDER BY Revenue DESC
LIMIT 10;


-- Q5: Bottom 10 campaigns by ROAS (underperformers)
SELECT
    Campaign_ID,
    Campaign_Name,
    Channel,
    ROUND(Cost, 2)    AS Cost,
    ROUND(Revenue, 2) AS Revenue,
    ROUND(ROAS, 2)    AS ROAS,
    ROUND(Profit, 2)  AS Profit
FROM campaigns
ORDER BY ROAS ASC
LIMIT 10;


-- Q6: Campaigns exceeding budget (cost > budget)
SELECT
    Campaign_ID,
    Campaign_Name,
    Channel,
    ROUND(Budget, 2)                AS Allocated_Budget,
    ROUND(Cost, 2)                  AS Actual_Cost,
    ROUND(Cost - Budget, 2)         AS Overspend,
    ROUND((Cost - Budget) / Budget * 100, 2) AS Overspend_Pct
FROM campaigns
WHERE Cost > Budget
ORDER BY Overspend DESC;


-- ============================================================
-- SECTION 4: CAMPAIGN TYPE ANALYSIS
-- ============================================================

-- Q7: Performance by campaign type
SELECT
    Campaign_Type,
    COUNT(*)                                       AS Campaigns,
    ROUND(AVG(CTR) * 100, 2)                       AS Avg_CTR_Pct,
    ROUND(AVG(Conversion_Rate) * 100, 2)           AS Avg_Conv_Rate_Pct,
    ROUND(AVG(ROAS), 2)                            AS Avg_ROAS,
    ROUND(SUM(Revenue), 2)                         AS Total_Revenue,
    ROUND(SUM(Cost), 2)                            AS Total_Cost
FROM campaigns
GROUP BY Campaign_Type
ORDER BY Avg_ROAS DESC;


-- Q8: Channel + Campaign Type cross performance
SELECT
    Channel,
    Campaign_Type,
    COUNT(*)                            AS Campaigns,
    ROUND(AVG(ROAS), 2)                 AS Avg_ROAS,
    ROUND(AVG(CTR) * 100, 2)            AS Avg_CTR_Pct,
    ROUND(SUM(Revenue), 2)              AS Total_Revenue
FROM campaigns
GROUP BY Channel, Campaign_Type
ORDER BY Channel, Avg_ROAS DESC;


-- ============================================================
-- SECTION 5: TIME-SERIES TREND ANALYSIS
-- ============================================================

-- Q9: Monthly revenue and spend trend
SELECT
    strftime('%Y-%m', Date)   AS Month,
    SUM(Impressions)          AS Impressions,
    SUM(Clicks)               AS Clicks,
    SUM(Conversions)          AS Conversions,
    ROUND(SUM(Cost), 2)       AS Total_Cost,
    ROUND(SUM(Revenue), 2)    AS Total_Revenue,
    ROUND(SUM(Revenue) / NULLIF(SUM(Cost), 0), 2) AS Monthly_ROAS
FROM daily_performance
GROUP BY Month
ORDER BY Month;


-- Q10: Weekly channel performance (last quarter)
SELECT
    Week,
    Channel,
    ROUND(SUM(Cost), 2)      AS Weekly_Cost,
    ROUND(SUM(Revenue), 2)   AS Weekly_Revenue,
    SUM(Conversions)         AS Weekly_Conversions
FROM daily_performance
WHERE Date >= date('now', '-90 days')
GROUP BY Week, Channel
ORDER BY Week, Channel;


-- Q11: Day-of-week performance pattern
SELECT
    CASE strftime('%w', Date)
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END                                AS Day_Of_Week,
    ROUND(AVG(Cost), 2)                AS Avg_Daily_Cost,
    ROUND(AVG(Revenue), 2)             AS Avg_Daily_Revenue,
    ROUND(AVG(Revenue / NULLIF(Cost, 0)), 2) AS Avg_ROAS
FROM daily_performance
GROUP BY strftime('%w', Date)
ORDER BY strftime('%w', Date);


-- ============================================================
-- SECTION 6: PARETO / 80-20 ANALYSIS
-- ============================================================

-- Q12: Pareto — cumulative revenue contribution
WITH ranked AS (
    SELECT
        Campaign_ID,
        Channel,
        ROUND(Revenue, 2)  AS Revenue,
        ROW_NUMBER() OVER (ORDER BY Revenue DESC) AS rn
    FROM campaigns
),
total AS (SELECT SUM(Revenue) AS total_rev FROM campaigns)
SELECT
    r.rn,
    r.Campaign_ID,
    r.Channel,
    r.Revenue,
    ROUND(SUM(r.Revenue) OVER (ORDER BY r.Revenue DESC) / t.total_rev * 100, 2) AS Cumulative_Pct
FROM ranked r, total t
ORDER BY r.Revenue DESC;


-- Q13: How many campaigns drive 80% of revenue?
WITH ranked AS (
    SELECT
        Campaign_ID,
        Revenue,
        SUM(Revenue) OVER (ORDER BY Revenue DESC) AS running_total,
        SUM(Revenue) OVER ()                       AS grand_total
    FROM campaigns
)
SELECT COUNT(*) AS Campaigns_Driving_80pct_Revenue
FROM ranked
WHERE running_total <= 0.8 * grand_total;


-- ============================================================
-- SECTION 7: ROI & BUDGET OPTIMISATION
-- ============================================================

-- Q14: Recommend budget reallocation — increase budget for high ROAS channels
SELECT
    Channel,
    ROUND(SUM(Cost), 2)                            AS Current_Spend,
    ROUND(SUM(Revenue) / NULLIF(SUM(Cost), 0), 2)  AS ROAS,
    CASE
        WHEN SUM(Revenue) / NULLIF(SUM(Cost), 0) >= 5 THEN 'INCREASE budget'
        WHEN SUM(Revenue) / NULLIF(SUM(Cost), 0) BETWEEN 3 AND 5 THEN 'MAINTAIN budget'
        ELSE 'REVIEW / REDUCE budget'
    END AS Recommendation
FROM campaigns
GROUP BY Channel
ORDER BY ROAS DESC;


-- Q15: Efficiency score — conversions per $100 spent
SELECT
    Channel,
    SUM(Conversions)                                     AS Total_Conversions,
    ROUND(SUM(Cost), 2)                                  AS Total_Cost,
    ROUND(SUM(Conversions) * 100.0 / NULLIF(SUM(Cost), 0), 2) AS Conv_Per_100_Dollars
FROM campaigns
GROUP BY Channel
ORDER BY Conv_Per_100_Dollars DESC;
