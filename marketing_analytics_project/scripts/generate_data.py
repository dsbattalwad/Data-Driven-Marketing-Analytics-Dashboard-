"""
Marketing Analytics Data Generator
Generates simulated marketing campaign data for analysis
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

np.random.seed(42)
random.seed(42)

# ─── Config ───────────────────────────────────────────────────────────────────
CHANNELS = ["Google Ads", "Facebook Ads", "Instagram Ads", "Email", "SEO Organic"]
CAMPAIGN_TYPES = ["Brand Awareness", "Lead Generation", "Retargeting", "Seasonal Promo", "Product Launch"]
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 12, 31)
N_CAMPAIGNS = 50

# Channel-level performance profiles (mean CTR, conv rate, CPC, ROAS)
CHANNEL_PROFILES = {
    "Google Ads":    dict(ctr_mu=0.045, ctr_sig=0.015, conv_mu=0.035, conv_sig=0.010, cpc_mu=1.80, cpc_sig=0.50, roas_mu=4.2, roas_sig=0.8),
    "Facebook Ads":  dict(ctr_mu=0.025, ctr_sig=0.010, conv_mu=0.020, conv_sig=0.008, cpc_mu=1.20, cpc_sig=0.40, roas_mu=3.1, roas_sig=0.7),
    "Instagram Ads": dict(ctr_mu=0.030, ctr_sig=0.012, conv_mu=0.018, conv_sig=0.007, cpc_mu=1.10, cpc_sig=0.35, roas_mu=2.8, roas_sig=0.6),
    "Email":         dict(ctr_mu=0.180, ctr_sig=0.040, conv_mu=0.055, conv_sig=0.015, cpc_mu=0.05, cpc_sig=0.02, roas_mu=8.5, roas_sig=1.5),
    "SEO Organic":   dict(ctr_mu=0.060, ctr_sig=0.020, conv_mu=0.028, conv_sig=0.009, cpc_mu=0.00, cpc_sig=0.00, roas_mu=6.0, roas_sig=1.2),
}

def random_date_range():
    total_days = (END_DATE - START_DATE).days
    start_offset = random.randint(0, total_days - 30)
    duration = random.randint(14, 90)
    s = START_DATE + timedelta(days=start_offset)
    e = min(s + timedelta(days=duration), END_DATE)
    return s.date(), e.date()

def clip_pos(val, minimum=0.0001):
    return max(val, minimum)

# ─── Campaign-Level Data ──────────────────────────────────────────────────────
records = []
for i in range(1, N_CAMPAIGNS + 1):
    channel = random.choice(CHANNELS)
    p = CHANNEL_PROFILES[channel]
    ctype = random.choice(CAMPAIGN_TYPES)
    budget = round(random.uniform(2000, 25000), 2)
    start_d, end_d = random_date_range()

    impressions = int(random.uniform(50000, 500000))
    ctr         = clip_pos(np.random.normal(p["ctr_mu"], p["ctr_sig"]))
    clicks      = int(impressions * ctr)
    conv_rate   = clip_pos(np.random.normal(p["conv_mu"], p["conv_sig"]))
    conversions = int(clicks * conv_rate)
    cpc         = clip_pos(np.random.normal(p["cpc_mu"], p["cpc_sig"]))
    cost        = round(clicks * cpc, 2)
    roas        = clip_pos(np.random.normal(p["roas_mu"], p["roas_sig"]))
    revenue     = round(cost * roas, 2)
    cpa         = round(cost / max(conversions, 1), 2)

    records.append({
        "Campaign_ID":    f"CAMP_{i:03d}",
        "Campaign_Name":  f"{channel.split()[0]}_{ctype.replace(' ', '_')}_{i:03d}",
        "Channel":        channel,
        "Campaign_Type":  ctype,
        "Start_Date":     start_d,
        "End_Date":       end_d,
        "Budget":         budget,
        "Impressions":    impressions,
        "Clicks":         clicks,
        "Conversions":    conversions,
        "Cost":           cost,
        "Revenue":        revenue,
        "CTR":            round(ctr, 4),
        "Conversion_Rate": round(conv_rate, 4),
        "CPC":            round(cpc, 4),
        "CPA":            cpa,
        "ROAS":           round(roas, 4),
        "Profit":         round(revenue - cost, 2),
    })

df_campaigns = pd.DataFrame(records)

# ─── Daily Time-Series Data ───────────────────────────────────────────────────
daily_records = []
for _, row in df_campaigns.iterrows():
    start = datetime.combine(row["Start_Date"], datetime.min.time())
    end   = datetime.combine(row["End_Date"],   datetime.min.time())
    days  = max((end - start).days, 1)
    for d in range(days):
        day = start + timedelta(days=d)
        noise  = np.random.uniform(0.7, 1.3)
        imps   = int(row["Impressions"] / days * noise)
        clks   = int(row["Clicks"] / days * noise)
        convs  = int(row["Conversions"] / days * noise)
        cost_d = round(row["Cost"] / days * noise, 2)
        rev_d  = round(row["Revenue"] / days * noise, 2)
        daily_records.append({
            "Date":         day.date(),
            "Campaign_ID":  row["Campaign_ID"],
            "Channel":      row["Channel"],
            "Impressions":  imps,
            "Clicks":       clks,
            "Conversions":  convs,
            "Cost":         cost_d,
            "Revenue":      rev_d,
        })

df_daily = pd.DataFrame(daily_records)
df_daily["Month"] = pd.to_datetime(df_daily["Date"]).dt.month_name()
df_daily["Week"]  = pd.to_datetime(df_daily["Date"]).dt.isocalendar().week.astype(int)

# ─── KPI Summary ─────────────────────────────────────────────────────────────
df_kpi = df_campaigns.groupby("Channel").agg(
    Total_Campaigns=("Campaign_ID", "count"),
    Total_Impressions=("Impressions", "sum"),
    Total_Clicks=("Clicks", "sum"),
    Total_Conversions=("Conversions", "sum"),
    Total_Cost=("Cost", "sum"),
    Total_Revenue=("Revenue", "sum"),
    Avg_CTR=("CTR", "mean"),
    Avg_Conv_Rate=("Conversion_Rate", "mean"),
    Avg_CPC=("CPC", "mean"),
    Avg_CPA=("CPA", "mean"),
    Avg_ROAS=("ROAS", "mean"),
).reset_index()
df_kpi["Total_Profit"] = df_kpi["Total_Revenue"] - df_kpi["Total_Cost"]
df_kpi["Overall_ROAS"] = df_kpi["Total_Revenue"] / df_kpi["Total_Cost"].replace(0, np.nan)

# ─── Save ─────────────────────────────────────────────────────────────────────
out = os.path.join(os.path.dirname(__file__), "..", "data")
df_campaigns.to_csv(f"{out}/campaigns.csv", index=False)
df_daily.to_csv(f"{out}/daily_performance.csv", index=False)
df_kpi.to_csv(f"{out}/kpi_summary.csv", index=False)

print(f"✅ Generated {len(df_campaigns)} campaigns, {len(df_daily)} daily rows.")
print(f"   Saved to: {os.path.abspath(out)}")
