"""
Run all SQL queries against the generated data using SQLite
Exports query results to data/sql_results/
"""

import pandas as pd
import sqlite3
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data")
OUT  = os.path.join(DATA, "sql_results")
os.makedirs(OUT, exist_ok=True)

# Load CSVs into SQLite in-memory DB
conn = sqlite3.connect(":memory:")
pd.read_csv(f"{DATA}/campaigns.csv").to_sql("campaigns", conn, index=False, if_exists="replace")
pd.read_csv(f"{DATA}/daily_performance.csv").to_sql("daily_performance", conn, index=False, if_exists="replace")

QUERIES = {
    "01_overall_kpi": """
        SELECT
            COUNT(DISTINCT Campaign_ID)  AS Total_Campaigns,
            SUM(Impressions)             AS Total_Impressions,
            SUM(Clicks)                  AS Total_Clicks,
            SUM(Conversions)             AS Total_Conversions,
            ROUND(SUM(Cost),2)           AS Total_Cost,
            ROUND(SUM(Revenue),2)        AS Total_Revenue,
            ROUND(SUM(Profit),2)         AS Total_Profit,
            ROUND(CAST(SUM(Clicks) AS REAL)/SUM(Impressions)*100,2) AS Overall_CTR_Pct,
            ROUND(CAST(SUM(Conversions) AS REAL)/SUM(Clicks)*100,2) AS Overall_Conv_Rate_Pct,
            ROUND(SUM(Revenue)/SUM(Cost),2) AS Overall_ROAS
        FROM campaigns
    """,
    "02_channel_kpis": """
        SELECT Channel,
            COUNT(*) AS Campaigns,
            SUM(Impressions) AS Impressions,
            SUM(Clicks) AS Clicks,
            SUM(Conversions) AS Conversions,
            ROUND(SUM(Cost),2) AS Total_Cost,
            ROUND(SUM(Revenue),2) AS Total_Revenue,
            ROUND(SUM(Revenue)-SUM(Cost),2) AS Total_Profit,
            ROUND(AVG(CTR)*100,2) AS Avg_CTR_Pct,
            ROUND(AVG(Conversion_Rate)*100,2) AS Avg_Conv_Rate_Pct,
            ROUND(AVG(CPC),2) AS Avg_CPC,
            ROUND(AVG(CPA),2) AS Avg_CPA,
            ROUND(SUM(Revenue)/SUM(Cost),2) AS Channel_ROAS
        FROM campaigns GROUP BY Channel ORDER BY Channel_ROAS DESC
    """,
    "03_top10_campaigns": """
        SELECT Campaign_ID, Campaign_Name, Channel, Campaign_Type,
            ROUND(Cost,2) AS Cost, ROUND(Revenue,2) AS Revenue,
            ROUND(Profit,2) AS Profit, ROUND(ROAS,2) AS ROAS
        FROM campaigns ORDER BY Revenue DESC LIMIT 10
    """,
    "04_campaign_type_perf": """
        SELECT Campaign_Type, COUNT(*) AS Campaigns,
            ROUND(AVG(CTR)*100,2) AS Avg_CTR_Pct,
            ROUND(AVG(Conversion_Rate)*100,2) AS Avg_Conv_Rate_Pct,
            ROUND(AVG(ROAS),2) AS Avg_ROAS,
            ROUND(SUM(Revenue),2) AS Total_Revenue
        FROM campaigns GROUP BY Campaign_Type ORDER BY Avg_ROAS DESC
    """,
    "05_monthly_trend": """
        SELECT substr(Date,1,7) AS Month,
            SUM(Impressions) AS Impressions, SUM(Clicks) AS Clicks,
            SUM(Conversions) AS Conversions,
            ROUND(SUM(Cost),2) AS Total_Cost,
            ROUND(SUM(Revenue),2) AS Total_Revenue,
            ROUND(SUM(Revenue)/SUM(Cost),2) AS Monthly_ROAS
        FROM daily_performance
        GROUP BY Month ORDER BY Month
    """,
    "06_budget_recommendation": """
        SELECT Channel,
            ROUND(SUM(Cost),2) AS Current_Spend,
            ROUND(SUM(Revenue)/SUM(Cost),2) AS ROAS,
            CASE WHEN SUM(Revenue)/SUM(Cost) >= 5 THEN 'INCREASE budget'
                 WHEN SUM(Revenue)/SUM(Cost) BETWEEN 3 AND 5 THEN 'MAINTAIN budget'
                 ELSE 'REVIEW / REDUCE budget' END AS Recommendation
        FROM campaigns GROUP BY Channel ORDER BY ROAS DESC
    """,
}

for name, query in QUERIES.items():
    df_result = pd.read_sql_query(query, conn)
    df_result.to_csv(f"{OUT}/{name}.csv", index=False)
    print(f"  ✅ {name}.csv ({len(df_result)} rows)")

conn.close()
print("\nAll SQL results exported to data/sql_results/")
