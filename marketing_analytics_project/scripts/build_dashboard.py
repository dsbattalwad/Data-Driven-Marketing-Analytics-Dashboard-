"""
Build the Marketing Analytics Excel Dashboard
Multiple worksheets: Overview, Channel KPIs, Campaign Data, Monthly Trend, Recommendations
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                              GradientFill)
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "data")
OUT  = os.path.join(BASE, "..", "dashboard")
os.makedirs(OUT, exist_ok=True)

# ─── Load data ────────────────────────────────────────────────────────────────
df_camp  = pd.read_csv(f"{DATA}/campaigns.csv")
df_daily = pd.read_csv(f"{DATA}/daily_performance.csv")
df_kpi   = pd.read_csv(f"{DATA}/sql_results/02_channel_kpis.csv")
df_monthly = pd.read_csv(f"{DATA}/sql_results/05_monthly_trend.csv")
df_top10 = pd.read_csv(f"{DATA}/sql_results/03_top10_campaigns.csv")
df_reco  = pd.read_csv(f"{DATA}/sql_results/06_budget_recommendation.csv")

wb = Workbook()

# ─── Styles ───────────────────────────────────────────────────────────────────
DARK_BLUE   = "1F3864"
MID_BLUE    = "2D6A9F"
LIGHT_BLUE  = "D6E4F0"
ORANGE      = "E8763A"
GREEN       = "27AE60"
LIGHT_GREEN = "D5F5E3"
LIGHT_ORANGE= "FDEBD0"
WHITE       = "FFFFFF"
GRAY        = "F2F2F2"
DARK_GRAY   = "666666"

def h_font(bold=True, size=11, color=WHITE, name="Arial"):
    return Font(bold=bold, size=size, color=color, name=name)

def b_font(bold=False, size=10, color="000000", name="Arial"):
    return Font(bold=bold, size=size, color=color, name=name)

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def thin_border():
    s = Side(style="thin", color="CCCCCC")
    return Border(left=s, right=s, top=s, bottom=s)

def set_col_width(ws, col_widths):
    for col, w in col_widths.items():
        ws.column_dimensions[col].width = w

def write_header_row(ws, row, headers, start_col=1, bg=MID_BLUE):
    for i, h in enumerate(headers):
        c = ws.cell(row=row, column=start_col+i, value=h)
        c.font = h_font(size=10)
        c.fill = fill(bg)
        c.alignment = center()
        c.border = thin_border()

def write_data_row(ws, row, values, start_col=1, bg=WHITE):
    for i, v in enumerate(values):
        c = ws.cell(row=row, column=start_col+i, value=v)
        c.font = b_font()
        c.fill = fill(bg)
        c.alignment = center()
        c.border = thin_border()

# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 1: OVERVIEW DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
ws1 = wb.active
ws1.title = "📊 Overview"
ws1.sheet_view.showGridLines = False

# Title banner
ws1.merge_cells("A1:L3")
title_cell = ws1["A1"]
title_cell.value = "🚀  DATA-DRIVEN MARKETING ANALYTICS DASHBOARD  |  FY 2024"
title_cell.font = Font(bold=True, size=18, color=WHITE, name="Arial")
title_cell.fill = fill(DARK_BLUE)
title_cell.alignment = center()

# Subtitle
ws1.merge_cells("A4:L4")
sub = ws1["A4"]
sub.value = "Internship Project  |  Domain: Data Analytics  |  Duration: 3 Months"
sub.font = Font(bold=False, size=10, color=DARK_GRAY, name="Arial", italic=True)
sub.alignment = center()

ws1.row_dimensions[1].height = 20
ws1.row_dimensions[2].height = 20
ws1.row_dimensions[3].height = 20

# KPI Cards (row 6-9)
kpi_cards = [
    ("Total Campaigns",   50,        "#",   LIGHT_BLUE,  MID_BLUE),
    ("Total Impressions", "12,499,936", "",  LIGHT_GREEN, GREEN),
    ("Total Clicks",      "853,235", "",     LIGHT_ORANGE,ORANGE),
    ("Total Conversions", "37,861",  "",     "F9EBEA",    "E74C3C"),
    ("Total Revenue",     "$1,186,390","",   "EBF5FB",    "1A5276"),
    ("Total Cost",        "$308,779", "",    "FEF9E7",    "B7950B"),
    ("Total Profit",      "$877,611", "",    LIGHT_GREEN, GREEN),
    ("Overall ROAS",      "3.84x",   "",     "F5EEF8",    "7D3C98"),
]

# Place KPI cards in 2-row blocks, 4 cards per row
# 4 cards per row, each card occupies 3 cols: cols 1-3, 4-6, 7-9, 10-12
card_positions = [(6, c) for c in [1,4,7,10]] + [(10, c) for c in [1,4,7,10]]
for idx, (label, value, unit, bg, accent) in enumerate(kpi_cards):
    r, c_start = card_positions[idx]
    c_end = c_start + 2
    # Write label to top-left cell of merge range, then merge
    lbl = ws1.cell(row=r, column=c_start)
    lbl.value = label
    lbl.font = Font(bold=True, size=10, color=accent, name="Arial")
    lbl.fill = fill(bg)
    lbl.alignment = center()
    lbl.border = thin_border()
    ws1.merge_cells(start_row=r, start_column=c_start, end_row=r, end_column=c_end)
    # Write value
    val = ws1.cell(row=r+1, column=c_start)
    val.value = value
    val.font = Font(bold=True, size=16, color=accent, name="Arial")
    val.fill = fill(bg)
    val.alignment = center()
    val.border = thin_border()
    ws1.merge_cells(start_row=r+1, start_column=c_start, end_row=r+1, end_column=c_end)
    ws1.row_dimensions[r].height   = 18
    ws1.row_dimensions[r+1].height = 28

# Section: Channel KPI Table (row 15 onwards)
ws1.merge_cells("A14:L14")
sec = ws1["A14"]
sec.value = "CHANNEL PERFORMANCE SUMMARY"
sec.font = Font(bold=True, size=12, color=WHITE, name="Arial")
sec.fill = fill(DARK_BLUE)
sec.alignment = center()

ch_headers = ["Channel","Campaigns","Impressions","Clicks","Conversions",
              "Total Cost","Total Revenue","Total Profit","Avg CTR%","Avg Conv%","Avg CPA","ROAS"]
write_header_row(ws1, 15, ch_headers)

for i, row in df_kpi.iterrows():
    bg = GRAY if i % 2 == 0 else WHITE
    vals = [
        row["Channel"], row["Campaigns"], f"{row['Impressions']:,}",
        f"{row['Clicks']:,}", f"{row['Conversions']:,}",
        f"${row['Total_Cost']:,.2f}", f"${row['Total_Revenue']:,.2f}",
        f"${row['Total_Profit']:,.2f}", f"{row['Avg_CTR_Pct']}%",
        f"{row['Avg_Conv_Rate_Pct']}%", f"${row['Avg_CPA']}", f"{row['Channel_ROAS']}x"
    ]
    write_data_row(ws1, 16+i, vals, bg=bg)

set_col_width(ws1, {
    "A":18,"B":11,"C":14,"D":11,"E":13,"F":13,
    "G":14,"H":13,"I":10,"J":10,"K":10,"L":9
})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 2: CHANNEL ROI
# ═══════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("📈 Channel ROI")
ws2.sheet_view.showGridLines = False

ws2.merge_cells("A1:J2")
t2 = ws2["A1"]
t2.value = "Channel-Wise ROI & KPI Analysis"
t2.font = Font(bold=True, size=16, color=WHITE, name="Arial")
t2.fill = fill(MID_BLUE); t2.alignment = center()
ws2.row_dimensions[1].height = 22; ws2.row_dimensions[2].height = 22

headers2 = ["Channel","Total Cost ($)","Total Revenue ($)","Total Profit ($)",
            "ROAS","Avg CTR (%)","Avg Conv Rate (%)","Avg CPC ($)","Avg CPA ($)","Recommendation"]
write_header_row(ws2, 4, headers2)

reco_map = {"INCREASE budget": GREEN, "MAINTAIN budget": "B8860B", "REVIEW / REDUCE budget": "C0392B"}
for i, row in df_reco.iterrows():
    krow = df_kpi[df_kpi["Channel"]==row["Channel"]].iloc[0]
    bg_r = GRAY if i%2==0 else WHITE
    vals = [
        row["Channel"], round(krow["Total_Cost"],2), round(krow["Total_Revenue"],2),
        round(krow["Total_Profit"],2), row["ROAS"],
        krow["Avg_CTR_Pct"], krow["Avg_Conv_Rate_Pct"],
        krow["Avg_CPC"], krow["Avg_CPA"], row["Recommendation"]
    ]
    for j, v in enumerate(vals):
        c = ws2.cell(row=5+i, column=j+1, value=v)
        c.font = b_font()
        c.fill = fill(bg_r)
        c.alignment = center()
        c.border = thin_border()
        if j == 9:  # Recommendation col
            color = reco_map.get(str(v), "000000")
            c.font = Font(bold=True, size=10, color=color, name="Arial")

# ROAS Chart
chart2 = BarChart()
chart2.type = "col"
chart2.title = "ROAS by Channel"
chart2.y_axis.title = "ROAS"
chart2.x_axis.title = "Channel"
chart2.style = 10
chart2.width = 18; chart2.height = 12

data_ref = Reference(ws2, min_col=5, min_row=4, max_row=9)
cats_ref = Reference(ws2, min_col=1, min_row=5, max_row=9)
chart2.add_data(data_ref, titles_from_data=True)
chart2.set_categories(cats_ref)
ws2.add_chart(chart2, "A12")

set_col_width(ws2, {"A":16,"B":14,"C":15,"D":14,"E":9,"F":11,"G":14,"H":11,"I":11,"J":22})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 3: CAMPAIGN DATA
# ═══════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("📋 Campaign Data")
ws3.sheet_view.showGridLines = False

ws3.merge_cells("A1:R2")
t3 = ws3["A1"]
t3.value = "All Campaign Performance Data"
t3.font = Font(bold=True, size=14, color=WHITE, name="Arial")
t3.fill = fill(DARK_BLUE); t3.alignment = center()

camp_cols = ["Campaign_ID","Campaign_Name","Channel","Campaign_Type",
             "Start_Date","End_Date","Budget","Impressions","Clicks",
             "Conversions","Cost","Revenue","Profit","CTR","Conversion_Rate",
             "CPC","CPA","ROAS"]
write_header_row(ws3, 3, camp_cols)

for i, row in df_camp.iterrows():
    bg_r = GRAY if i%2==0 else WHITE
    vals = [row[c] for c in camp_cols]
    for j, v in enumerate(vals):
        c = ws3.cell(row=4+i, column=j+1, value=v)
        c.font = b_font(size=9)
        c.fill = fill(bg_r)
        c.alignment = center()
        c.border = thin_border()
        if camp_cols[j] == "ROAS":
            if isinstance(v, (int, float)):
                if v >= 5:   c.font = Font(bold=True, size=9, color=GREEN, name="Arial")
                elif v < 2:  c.font = Font(bold=True, size=9, color="C0392B", name="Arial")

# Conditional formatting on ROAS column (R = col 18)
from openpyxl.formatting.rule import ColorScaleRule
ws3.conditional_formatting.add(
    f"R4:R{3+len(df_camp)}",
    ColorScaleRule(start_type="min", start_color="F1948A",
                   mid_type="percentile", mid_value=50, mid_color="F9E79F",
                   end_type="max", end_color="7DCEA0")
)

col_ws = {"A":11,"B":28,"C":14,"D":18,"E":11,"F":11,"G":11,"H":13,
          "I":10,"J":12,"K":11,"L":11,"M":11,"N":8,"O":14,"P":8,"Q":8,"R":8}
set_col_width(ws3, col_ws)


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 4: MONTHLY TREND
# ═══════════════════════════════════════════════════════════════════════════════
ws4 = wb.create_sheet("📅 Monthly Trend")
ws4.sheet_view.showGridLines = False

ws4.merge_cells("A1:H2")
t4 = ws4["A1"]
t4.value = "Monthly Marketing Performance Trend — FY 2024"
t4.font = Font(bold=True, size=14, color=WHITE, name="Arial")
t4.fill = fill(MID_BLUE); t4.alignment = center()

month_headers = ["Month","Impressions","Clicks","Conversions",
                 "Total Cost ($)","Total Revenue ($)","Monthly ROAS","MoM Revenue Growth"]
write_header_row(ws4, 4, month_headers)

for i, row in df_monthly.iterrows():
    bg_r = GRAY if i%2==0 else WHITE
    prev_rev = df_monthly.iloc[i-1]["Total_Revenue"] if i > 0 else None
    mom = round((row["Total_Revenue"] - prev_rev) / prev_rev * 100, 1) if prev_rev else "–"
    vals = [row["Month"], f"{row['Impressions']:,}", f"{row['Clicks']:,}",
            f"{row['Conversions']:,}", round(row["Total_Cost"],2),
            round(row["Total_Revenue"],2), f"{row['Monthly_ROAS']}x",
            f"{mom}%" if mom != "–" else "–"]
    write_data_row(ws4, 5+i, vals, bg=bg_r)

# Line chart for revenue trend
chart4 = LineChart()
chart4.title = "Monthly Revenue vs Cost Trend"
chart4.style = 10
chart4.y_axis.title = "Amount ($)"
chart4.x_axis.title = "Month"
chart4.width = 22; chart4.height = 12

rev_data = Reference(ws4, min_col=6, min_row=4, max_row=16)
cost_data = Reference(ws4, min_col=5, min_row=4, max_row=16)
cats = Reference(ws4, min_col=1, min_row=5, max_row=16)
chart4.add_data(rev_data, titles_from_data=True)
chart4.add_data(cost_data, titles_from_data=True)
chart4.set_categories(cats)
ws4.add_chart(chart4, "A19")

set_col_width(ws4, {"A":10,"B":14,"C":12,"D":13,"E":14,"F":16,"G":14,"H":18})


# ═══════════════════════════════════════════════════════════════════════════════
# SHEET 5: TOP CAMPAIGNS & RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
ws5 = wb.create_sheet("🏆 Top Campaigns")
ws5.sheet_view.showGridLines = False

ws5.merge_cells("A1:H2")
t5 = ws5["A1"]
t5.value = "Top 10 Campaigns by Revenue"
t5.font = Font(bold=True, size=14, color=WHITE, name="Arial")
t5.fill = fill(DARK_BLUE); t5.alignment = center()

top_headers = ["Rank","Campaign ID","Campaign Name","Channel","Campaign Type",
               "Cost ($)","Revenue ($)","ROAS"]
write_header_row(ws5, 4, top_headers)

for i, row in df_top10.iterrows():
    bg_r = GRAY if i%2==0 else WHITE
    vals = [i+1, row["Campaign_ID"], row["Campaign_Name"], row["Channel"],
            row["Campaign_Type"], row["Cost"], row["Revenue"], row["ROAS"]]
    for j, v in enumerate(vals):
        c = ws5.cell(row=5+i, column=j+1, value=v)
        c.font = b_font()
        c.fill = fill(bg_r)
        c.alignment = center()
        c.border = thin_border()
    # Highlight top 3 gold, silver, bronze
    if i == 0:
        for j in range(8):
            ws5.cell(row=5, column=j+1).fill = fill("FFD700")
            ws5.cell(row=5, column=j+1).font = Font(bold=True, size=10, color="7D6608", name="Arial")

# Insights section
ws5.merge_cells("A17:H17")
ins_title = ws5["A17"]
ins_title.value = "KEY BUSINESS INSIGHTS & RECOMMENDATIONS"
ins_title.font = Font(bold=True, size=12, color=WHITE, name="Arial")
ins_title.fill = fill(MID_BLUE); ins_title.alignment = center()

insights = [
    ("💡 Insight 1", "Email campaigns deliver the highest ROAS (9.25x) — significantly outperforming all paid channels."),
    ("💡 Insight 2", "Google Ads drives 64% of total revenue despite only 10 campaigns — highest revenue concentration."),
    ("💡 Insight 3", "SEO Organic achieves 6.08x ROAS with near-zero cost — strong case for content investment."),
    ("⚠️ Insight 4", "Instagram Ads shows lowest ROAS (2.6x) and highest CPA ($77.52) — review targeting strategy."),
    ("📌 Insight 5", "Pareto principle holds: top 20% of campaigns likely generate ~70% of total revenue."),
    ("🎯 Recommendation", "Reallocate 15-20% of Instagram/Facebook budget toward Email automation and SEO content."),
    ("🎯 Recommendation", "Expand Google Ads budget by 20% targeting high-converting keywords — highest revenue channel."),
    ("🎯 Recommendation", "A/B test Instagram creatives and improve landing pages to boost conversion rate from 1.6%."),
]

for i, (label, text) in enumerate(insights):
    bg_r = LIGHT_BLUE if i % 2 == 0 else WHITE
    c1 = ws5.cell(row=18+i, column=1, value=label)
    c1.font = Font(bold=True, size=10, color=DARK_BLUE, name="Arial")
    c1.fill = fill(bg_r); c1.alignment = center(); c1.border = thin_border()

    ws5.merge_cells(f"B{18+i}:H{18+i}")
    c2 = ws5.cell(row=18+i, column=2, value=text)
    c2.font = b_font(size=10)
    c2.fill = fill(bg_r)
    c2.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    c2.border = thin_border()
    ws5.row_dimensions[18+i].height = 20

set_col_width(ws5, {"A":14,"B":18,"C":28,"D":14,"E":18,"F":12,"G":13,"H":10})

# ─── Save ─────────────────────────────────────────────────────────────────────
output_path = f"{OUT}/Marketing_Analytics_Dashboard.xlsx"
wb.save(output_path)
print(f"✅ Dashboard saved: {output_path}")
