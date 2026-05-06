"""
Marketing Analytics - Exploratory Data Analysis & Visualizations
Generates all charts saved to reports/figures/
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os

# ─── Setup ────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data")
FIG  = os.path.join(BASE, "..", "reports", "figures")
os.makedirs(FIG, exist_ok=True)

df   = pd.read_csv(f"{DATA}/campaigns.csv")
dd   = pd.read_csv(f"{DATA}/daily_performance.csv", parse_dates=["Date"])
kpi  = pd.read_csv(f"{DATA}/kpi_summary.csv")

PALETTE = ["#2D6A9F","#E8763A","#27AE60","#9B59B6","#E74C3C"]
sns.set_theme(style="whitegrid", font_scale=1.1)

def save(name):
    plt.tight_layout()
    plt.savefig(f"{FIG}/{name}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  saved {name}.png")

# ─── 1. Channel ROI Bar Chart ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(kpi["Channel"], kpi["Overall_ROAS"], color=PALETTE, edgecolor="white", width=0.6)
ax.set_title("Return on Ad Spend (ROAS) by Channel", fontsize=14, fontweight="bold")
ax.set_ylabel("ROAS (Revenue / Cost)")
ax.set_xlabel("")
for b in bars:
    ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.1,
            f"{b.get_height():.1f}x", ha="center", va="bottom", fontsize=11, fontweight="bold")
ax.set_ylim(0, kpi["Overall_ROAS"].max() * 1.2)
save("01_channel_roas")

# ─── 2. Revenue vs Cost by Channel ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(kpi))
w = 0.35
ax.bar(x - w/2, kpi["Total_Revenue"]/1000, w, label="Revenue ($K)", color="#2D6A9F")
ax.bar(x + w/2, kpi["Total_Cost"]/1000,    w, label="Cost ($K)",    color="#E8763A")
ax.set_xticks(x); ax.set_xticklabels(kpi["Channel"], rotation=15, ha="right")
ax.set_title("Total Revenue vs Cost by Channel", fontsize=14, fontweight="bold")
ax.set_ylabel("Amount ($K)")
ax.legend()
save("02_revenue_vs_cost")

# ─── 3. CTR by Channel (Box Plot) ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
order = df.groupby("Channel")["CTR"].median().sort_values(ascending=False).index.tolist()
sns.boxplot(data=df, x="Channel", y="CTR", order=order, palette=PALETTE, ax=ax)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
ax.set_title("Click-Through Rate (CTR) Distribution by Channel", fontsize=14, fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("CTR (%)")
save("03_ctr_boxplot")

# ─── 4. Monthly Spend Trend ───────────────────────────────────────────────────
monthly = dd.groupby([dd["Date"].dt.to_period("M"), "Channel"])["Cost"].sum().reset_index()
monthly["Date"] = monthly["Date"].dt.to_timestamp()
fig, ax = plt.subplots(figsize=(12, 5))
for i, ch in enumerate(monthly["Channel"].unique()):
    sub = monthly[monthly["Channel"]==ch].sort_values("Date")
    ax.plot(sub["Date"], sub["Cost"]/1000, marker="o", markersize=4, label=ch, color=PALETTE[i])
ax.set_title("Monthly Marketing Spend by Channel", fontsize=14, fontweight="bold")
ax.set_ylabel("Cost ($K)"); ax.legend(loc="upper right", fontsize=9)
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b %Y"))
fig.autofmt_xdate()
save("04_monthly_spend_trend")

# ─── 5. Conversion Funnel ────────────────────────────────────────────────────
funnel = {
    "Impressions": df["Impressions"].sum(),
    "Clicks":      df["Clicks"].sum(),
    "Conversions": df["Conversions"].sum(),
}
colors_f = ["#2D6A9F","#5BA3D6","#A8D1F0"]
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(list(funnel.keys())[::-1], list(funnel.values())[::-1], color=colors_f, edgecolor="white")
for b, v in zip(bars, list(funnel.values())[::-1]):
    ax.text(b.get_width()*1.01, b.get_y()+b.get_height()/2,
            f"{v:,.0f}", va="center", fontsize=11)
ax.set_title("Overall Marketing Funnel", fontsize=14, fontweight="bold")
ax.set_xlabel("Volume"); ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e6:.1f}M" if x>=1e6 else f"{x/1e3:.0f}K"))
save("05_conversion_funnel")

# ─── 6. CPA by Channel ────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
order2 = kpi.sort_values("Avg_CPA")["Channel"].tolist()
colors_c = [PALETTE[i] for i in range(len(order2))]
ax.barh(order2, kpi.set_index("Channel").loc[order2,"Avg_CPA"], color=colors_c, edgecolor="white")
ax.set_title("Average Cost Per Acquisition (CPA) by Channel", fontsize=14, fontweight="bold")
ax.set_xlabel("CPA ($)")
for i, v in enumerate(kpi.set_index("Channel").loc[order2,"Avg_CPA"]):
    ax.text(v+0.2, i, f"${v:.2f}", va="center")
save("06_cpa_by_channel")

# ─── 7. Campaign Scatter: Cost vs Revenue ────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
channel_list = df["Channel"].unique()
for i, ch in enumerate(channel_list):
    sub = df[df["Channel"]==ch]
    ax.scatter(sub["Cost"]/1000, sub["Revenue"]/1000, label=ch, color=PALETTE[i], alpha=0.7, s=60)
lims = [0, max(df["Revenue"].max(), df["Cost"].max())/1000 * 1.1]
ax.plot(lims, lims, "k--", linewidth=1, label="Break-even")
ax.set_xlim(0); ax.set_ylim(0)
ax.set_title("Campaign Cost vs Revenue", fontsize=14, fontweight="bold")
ax.set_xlabel("Cost ($K)"); ax.set_ylabel("Revenue ($K)")
ax.legend(fontsize=9)
save("07_cost_vs_revenue_scatter")

# ─── 8. Heatmap: Channel × Campaign Type ROAS ────────────────────────────────
pivot = df.pivot_table(values="ROAS", index="Channel", columns="Campaign_Type", aggfunc="mean")
fig, ax = plt.subplots(figsize=(11, 5))
sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu", linewidths=0.5, ax=ax,
            cbar_kws={"label":"Avg ROAS"})
ax.set_title("Average ROAS — Channel × Campaign Type", fontsize=14, fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("")
save("08_heatmap_roas")

# ─── 9. Pareto: Top Campaigns by Revenue ─────────────────────────────────────
top = df.nlargest(20, "Revenue").sort_values("Revenue", ascending=False)
top["Cumulative_%"] = top["Revenue"].cumsum() / top["Revenue"].sum() * 100
fig, ax1 = plt.subplots(figsize=(12, 5))
ax2 = ax1.twinx()
ax1.bar(range(len(top)), top["Revenue"]/1000, color="#2D6A9F", alpha=0.8)
ax2.plot(range(len(top)), top["Cumulative_%"], "r-o", markersize=5)
ax1.set_xticks(range(len(top)))
ax1.set_xticklabels(top["Campaign_ID"], rotation=45, ha="right", fontsize=8)
ax1.set_ylabel("Revenue ($K)"); ax2.set_ylabel("Cumulative %", color="red")
ax2.tick_params(colors="red"); ax2.set_ylim(0, 110)
ax1.set_title("Pareto: Top 20 Campaigns by Revenue", fontsize=14, fontweight="bold")
save("09_pareto_campaigns")

# ─── 10. Weekly Revenue Trend ────────────────────────────────────────────────
weekly = dd.groupby(dd["Date"].dt.to_period("W"))["Revenue"].sum().reset_index()
weekly["Date"] = weekly["Date"].dt.to_timestamp()
fig, ax = plt.subplots(figsize=(13, 5))
ax.fill_between(weekly["Date"], weekly["Revenue"]/1000, alpha=0.3, color="#2D6A9F")
ax.plot(weekly["Date"], weekly["Revenue"]/1000, color="#2D6A9F", linewidth=2)
ax.set_title("Weekly Revenue Trend (2024)", fontsize=14, fontweight="bold")
ax.set_ylabel("Revenue ($K)"); ax.set_xlabel("")
ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b"))
fig.autofmt_xdate()
save("10_weekly_revenue_trend")

print("\n✅ All 10 figures saved to reports/figures/")
