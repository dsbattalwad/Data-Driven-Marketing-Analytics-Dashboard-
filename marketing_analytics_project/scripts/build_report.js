const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, WidthType, BorderStyle, ShadingType,
  LevelFormat, PageNumber, Header, Footer, TabStopType, TabStopPosition,
  PageBreak
} = require("docx");
const fs = require("fs");
const path = require("path");

const OUT = path.join(__dirname, "..", "reports");
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

// ─── Colours ─────────────────────────────────────────────────────────────────
const DARK_BLUE  = "1F3864";
const MID_BLUE   = "2D6A9F";
const LIGHT_BLUE = "D6E4F0";
const GREEN      = "1E8449";
const ORANGE_BG  = "FDEBD0";
const GREEN_BG   = "D5F5E3";
const GRAY       = "F2F2F2";

// ─── Helpers ─────────────────────────────────────────────────────────────────
const hBorder = { style: BorderStyle.SINGLE, size: 1, color: "AAAAAA" };
const borders  = { top: hBorder, bottom: hBorder, left: hBorder, right: hBorder };
const noBorder = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
                   left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }};

function run(text, opts = {}) {
  return new TextRun({ text, font: "Arial", size: opts.size || 22,
    bold: opts.bold || false, italics: opts.italic || false,
    color: opts.color || "000000" });
}

function para(children, opts = {}) {
  return new Paragraph({
    children: Array.isArray(children) ? children : [children],
    alignment: opts.align || AlignmentType.LEFT,
    spacing: { before: opts.before || 80, after: opts.after || 80 },
    indent: opts.indent ? { left: opts.indent } : undefined,
  });
}

function heading(text, level, color = DARK_BLUE) {
  return new Paragraph({
    heading: level,
    children: [new TextRun({ text, font: "Arial", bold: true,
      size: level === HeadingLevel.HEADING_1 ? 36 : level === HeadingLevel.HEADING_2 ? 28 : 24,
      color })],
    spacing: { before: 240, after: 120 },
  });
}

function bullet(text, opts = {}) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [run(text, opts)],
    spacing: { before: 40, after: 40 },
  });
}

function subBullet(text) {
  return new Paragraph({
    numbering: { reference: "sub-bullets", level: 0 },
    children: [run(text, { size: 20, color: "333333" })],
    spacing: { before: 20, after: 20 },
  });
}

function divider() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: MID_BLUE } },
    spacing: { before: 60, after: 60 },
    children: [],
  });
}

function headerCell(text, width, bg = MID_BLUE) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders, margins: { top: 80, bottom: 80, left: 120, right: 120 },
    shading: { fill: bg, type: ShadingType.CLEAR },
    children: [para(run(text, { bold: true, color: "FFFFFF", size: 20 }), { align: AlignmentType.CENTER })],
  });
}

function dataCell(text, width, bg = "FFFFFF", color = "000000", bold = false) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders, margins: { top: 80, bottom: 80, left: 120, right: 120 },
    shading: { fill: bg, type: ShadingType.CLEAR },
    children: [para(run(text, { color, bold, size: 20 }), { align: AlignmentType.CENTER })],
  });
}

function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

// ─── Tables ───────────────────────────────────────────────────────────────────
const W = 9360; // total content width DXA (1" margins on US Letter)

function kpiTable() {
  const rows = [
    ["Metric", "Value", "Metric", "Value"],
    ["Total Campaigns", "50", "Overall ROAS", "3.84x"],
    ["Total Impressions", "12,499,936", "Total Revenue", "$1,186,390"],
    ["Total Clicks", "853,235", "Total Cost", "$308,779"],
    ["Total Conversions", "37,861", "Total Profit", "$877,611"],
    ["Overall CTR", "6.83%", "Overall Conv. Rate", "4.44%"],
  ];
  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: [2400, 1980, 2400, 2580],
    rows: rows.map((r, i) =>
      new TableRow({
        children: i === 0
          ? r.map((h, j) => headerCell(h, [2400,1980,2400,2580][j]))
          : r.map((v, j) => dataCell(v, [2400,1980,2400,2580][j],
              j % 2 === 1 ? (i%2===0 ? LIGHT_BLUE : GREEN_BG) : (i%2===0 ? GRAY : "FFFFFF"),
              j % 2 === 1 ? MID_BLUE : "000000", j % 2 === 1))
      })
    )
  });
}

function channelTable() {
  const hdrs = ["Channel", "Campaigns", "Total Cost", "Total Revenue", "ROAS", "Avg CTR", "CPA", "Recommendation"];
  const widths = [1600, 900, 1100, 1200, 800, 850, 850, 2060];
  const rows = [
    ["Email", "8", "$12,129", "$112,248", "9.25x", "18.54%", "$0.69", "INCREASE budget"],
    ["SEO Organic", "16", "$24", "$147", "6.08x", "5.82%", "$0.00", "INCREASE budget"],
    ["Google Ads", "10", "$184,537", "$763,480", "4.14x", "4.44%", "$57.47", "MAINTAIN budget"],
    ["Facebook Ads", "10", "$54,406", "$160,489", "2.95x", "2.28%", "$62.21", "REVIEW/REDUCE"],
    ["Instagram Ads", "6", "$57,683", "$150,027", "2.60x", "2.69%", "$77.52", "REVIEW/REDUCE"],
  ];
  const recoBg = { "INCREASE budget": GREEN_BG, "MAINTAIN budget": "FDFEFE", "REVIEW/REDUCE": ORANGE_BG };
  const recoColor = { "INCREASE budget": GREEN, "MAINTAIN budget": "000000", "REVIEW/REDUCE": "C0392B" };

  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ children: hdrs.map((h, j) => headerCell(h, widths[j])) }),
      ...rows.map((r, i) =>
        new TableRow({
          children: r.map((v, j) => {
            const bg = j === 7 ? (recoBg[v] || "FFFFFF") : (i%2===0 ? GRAY : "FFFFFF");
            const color = j === 7 ? (recoColor[v] || "000000") : (j === 4 ? MID_BLUE : "000000");
            return dataCell(v, widths[j], bg, color, j === 4 || j === 7);
          })
        })
      )
    ]
  });
}

function kpiDefinitionsTable() {
  const hdrs = ["KPI", "Formula", "Our Value", "Industry Benchmark"];
  const widths = [1800, 2800, 1600, 3160];
  const rows = [
    ["CTR (Click-Through Rate)", "Clicks / Impressions × 100", "6.83%", "2–5% (Search), 0.5–1% (Display)"],
    ["Conversion Rate", "Conversions / Clicks × 100", "4.44%", "2–5% (average)"],
    ["CPC (Cost per Click)", "Total Cost / Total Clicks", "$0.36 avg", "$1–2 (Search), $0.5–1 (Social)"],
    ["CPA (Cost per Acquisition)", "Total Cost / Conversions", "$8.15 avg", "Varies by industry"],
    ["ROAS (Return on Ad Spend)", "Revenue / Ad Spend", "3.84x", "4x+ (good), 2x (break-even)"],
    ["Revenue per Campaign", "Total Revenue / Campaigns", "$23,728", "Higher is better"],
  ];
  return new Table({
    width: { size: W, type: WidthType.DXA },
    columnWidths: widths,
    rows: [
      new TableRow({ children: hdrs.map((h, j) => headerCell(h, widths[j])) }),
      ...rows.map((r, i) =>
        new TableRow({
          children: r.map((v, j) =>
            dataCell(v, widths[j], i%2===0 ? GRAY : "FFFFFF",
              j === 2 ? MID_BLUE : "000000", j === 2))
        })
      )
    ]
  });
}

// ─── Document ─────────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [
      { reference: "bullets",     levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "sub-bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "◦",
          alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 360 } } } }] },
      { reference: "numbers",     levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: DARK_BLUE },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: MID_BLUE },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "2C3E50" },
        paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 } },
    ]
  },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 },
               margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: MID_BLUE } },
          spacing: { before: 0, after: 60 },
          children: [
            run("Data-Driven Marketing Analytics Dashboard  |  3-Month Internship Project", { size: 18, color: DARK_BLUE, bold: true }),
          ]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: MID_BLUE } },
          spacing: { before: 60 },
          tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
          children: [
            run("Internship Project Report  |  Data Analytics Domain", { size: 16, color: "888888" }),
            new TextRun({ text: "\tPage ", font: "Arial", size: 16, color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: "888888" }),
            new TextRun({ text: " of ", font: "Arial", size: 16, color: "888888" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], font: "Arial", size: 16, color: "888888" }),
          ]
        })]
      })
    },
    children: [
      // ─── COVER PAGE ─────────────────────────────────────────────────────────
      para(run(""), { before: 400 }),
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 0, after: 40 },
        children: [run("DATA-DRIVEN", { bold: true, size: 52, color: DARK_BLUE })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 0, after: 40 },
        children: [run("MARKETING ANALYTICS DASHBOARD", { bold: true, size: 52, color: MID_BLUE })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 20, after: 60 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ORANGE_BG.replace("FDEBD0","E8763A") } },
        children: [run(" ", { size: 28 })]
      }),
      para(run(""), { before: 40 }),
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 20, after: 20 },
        children: [run("3-Month Internship Project", { bold: true, size: 32, color: "555555" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 10, after: 10 },
        children: [run("Domain: Data Analytics", { size: 26, color: "777777" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 10, after: 10 },
        children: [run("Tools: Excel | SQL | Python | Power BI / Tableau | Matplotlib | Seaborn", { size: 22, italic: true, color: "888888" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER, spacing: { before: 60, after: 20 },
        children: [run("Academic Year: 2024 – 2025", { size: 22, color: "999999" })]
      }),
      para(run(""), { before: 80 }),
      pageBreak(),

      // ─── SECTION 1: PROJECT OVERVIEW ─────────────────────────────────────
      heading("1.  Project Overview", HeadingLevel.HEADING_1),
      divider(),
      para([
        run("Marketing teams today generate enormous volumes of data from multiple digital channels — Google Ads, social media, email, and website analytics. Yet many businesses struggle to aggregate this data meaningfully and measure the true performance of each marketing rupee spent. "),
        run("This project addresses that gap by building an end-to-end Marketing Analytics Dashboard", { bold: true }),
        run(" — a comprehensive system that tracks campaign KPIs, measures ROI, and generates actionable insights."),
      ], { after: 120 }),
      para([
        run("The project simulates real-world marketing operations across "),
        run("5 digital channels", { bold: true, color: MID_BLUE }),
        run(" and "),
        run("50 campaigns", { bold: true, color: MID_BLUE }),
        run(", spanning the full calendar year of 2024. Every step of the data analytics workflow — from raw data collection to executive-ready dashboards — is implemented using industry-standard tools and technologies."),
      ], { after: 120 }),

      heading("1.1  Business Problem Statement", HeadingLevel.HEADING_2),
      para(run("How can a business measure marketing effectiveness across multiple channels and optimise campaign spending using data-driven insights?"), { before: 40, after: 80 }),
      para([
        run("Without a unified analytics framework, marketing decisions are often made on intuition rather than evidence. Budget gets allocated to channels that appear busy (high impressions, high clicks) rather than channels that are truly profitable. This project demonstrates how a structured data analytics approach transforms raw campaign data into clear, actionable recommendations."),
      ]),

      heading("1.2  Project Objectives", HeadingLevel.HEADING_2),
      bullet("Track and monitor key marketing KPIs across all digital channels"),
      bullet("Measure campaign performance, ROI, and Return on Ad Spend (ROAS)"),
      bullet("Identify high-performing channels and underperforming campaigns"),
      bullet("Enable data-driven marketing budget allocation decisions"),
      bullet("Build a production-ready analytics dashboard suitable for executive reporting"),
      bullet("Demonstrate mastery of the full data analytics workflow as an internship deliverable"),

      pageBreak(),

      // ─── SECTION 2: TOOLS & DATA ──────────────────────────────────────────
      heading("2.  Tools, Technologies & Data Sources", HeadingLevel.HEADING_1),
      divider(),

      heading("2.1  Tools & Technologies", HeadingLevel.HEADING_2),
      para(run("The following industry-standard tools were used across the project phases:")),
      para(run("")),

      new Table({
        width: { size: W, type: WidthType.DXA },
        columnWidths: [2200, 3100, 4060],
        rows: [
          new TableRow({ children: [headerCell("Tool / Technology", 2200), headerCell("Purpose", 3100), headerCell("Usage in This Project", 4060)] }),
          ...([
            ["Microsoft Excel", "Data exploration, KPI tracking", "Dashboard prototyping, KPI summary sheets"],
            ["SQL (SQLite)", "Data querying & aggregation", "15+ analytical queries for KPI extraction"],
            ["Python (Pandas, NumPy)", "Data generation, cleaning, analysis", "50-campaign dataset, daily time-series"],
            ["Matplotlib / Seaborn", "Statistical visualisation", "10 publication-ready chart figures"],
            ["Power BI / Tableau", "Interactive dashboards", "Dashboard wireframe & design reference"],
            ["openpyxl", "Excel file automation", "5-sheet formatted Excel dashboard"],
          ]).map((r, i) => new TableRow({
            children: r.map((v, j) => dataCell(v, [2200,3100,4060][j], i%2===0 ? GRAY : "FFFFFF"))
          }))
        ]
      }),
      para(run("")),

      heading("2.2  Data Sources & Schema", HeadingLevel.HEADING_2),
      para([
        run("Three datasets were constructed using a Python simulation engine ("),
        run("scripts/generate_data.py", { bold: true, color: MID_BLUE }),
        run(") that models realistic channel-level performance distributions based on documented industry benchmarks:"),
      ]),
      bullet("campaigns.csv — 50 campaigns with 18 attributes each"),
      bullet("daily_performance.csv — 2,486 daily observations across all active campaigns"),
      bullet("kpi_summary.csv — aggregated KPI view by channel"),
      para(run("")),
      para(run("Key dataset fields include:")),
      bullet("Campaign_ID, Campaign_Name, Channel, Campaign_Type"),
      bullet("Start_Date, End_Date, Budget, Impressions, Clicks, Conversions"),
      bullet("Cost, Revenue, Profit, CTR, Conversion_Rate, CPC, CPA, ROAS"),

      pageBreak(),

      // ─── SECTION 3: KPI FRAMEWORK ─────────────────────────────────────────
      heading("3.  KPI Framework & Definitions", HeadingLevel.HEADING_1),
      divider(),
      para([
        run("Six core KPIs were selected to comprehensively measure marketing effectiveness — covering reach, engagement, conversion, cost efficiency, and profitability:"),
      ], { after: 120 }),
      kpiDefinitionsTable(),
      para(run("")),

      // ─── SECTION 4: PROJECT WORKFLOW ──────────────────────────────────────
      heading("4.  Project Workflow", HeadingLevel.HEADING_1),
      divider(),

      heading("4.1  Phase 1 — Data Collection & Generation", HeadingLevel.HEADING_2),
      para([
        run("Since real campaign data requires active advertising accounts, this project uses a "),
        run("statistically rigorous simulation engine", { bold: true }),
        run(" that models realistic marketing channel behaviour. Each channel was configured with distinct performance profiles drawn from published industry benchmarks (Google Ads avg CTR ~4–5%, Email avg CTR ~18–20%, social media ~2–3%)."),
      ]),
      bullet("50 campaigns generated across 5 channels and 5 campaign types"),
      bullet("Each campaign has randomised duration (14–90 days) and budget ($2K–$25K)"),
      bullet("Daily performance data generated with noise factors to simulate real-world variability"),

      heading("4.2  Phase 2 — Data Cleaning & Integration", HeadingLevel.HEADING_2),
      para(run("The following data quality checks were applied:")),
      bullet("Null value checks — no missing values in generated dataset"),
      bullet("Negative value prevention — all financial and engagement metrics clipped at zero"),
      bullet("Date validation — campaign end dates capped at year-end boundary"),
      bullet("Schema normalisation — consistent column naming and data types across all tables"),
      bullet("Derived metrics calculation — CTR, Conv Rate, CPC, CPA, ROAS, Profit all computed"),

      heading("4.3  Phase 3 — KPI Calculation via SQL", HeadingLevel.HEADING_2),
      para([
        run("A comprehensive SQL query library ("),
        run("sql/marketing_queries.sql", { bold: true, color: MID_BLUE }),
        run(") was developed with 15 production-quality queries covering:"),
      ]),
      bullet("Overall performance aggregations (Q1)"),
      bullet("Channel-wise KPI breakdowns with ROAS ranking (Q2, Q3)"),
      bullet("Top/bottom campaign identification (Q4, Q5)"),
      bullet("Budget overspend detection (Q6)"),
      bullet("Campaign type cross-analysis (Q7, Q8)"),
      bullet("Monthly and weekly time-series trends (Q9, Q10, Q11)"),
      bullet("Pareto analysis — campaigns contributing 80% of revenue (Q12, Q13)"),
      bullet("Budget reallocation recommendations (Q14, Q15)"),

      heading("4.4  Phase 4 — Exploratory Data Analysis", HeadingLevel.HEADING_2),
      para(run("Ten visualisation figures were produced using Matplotlib and Seaborn (stored in reports/figures/):")),
      bullet("Figure 01 — Channel ROAS Comparison (bar chart)"),
      bullet("Figure 02 — Revenue vs Cost by Channel (grouped bar)"),
      bullet("Figure 03 — CTR Distribution by Channel (box plot)"),
      bullet("Figure 04 — Monthly Spend Trend by Channel (multi-line)"),
      bullet("Figure 05 — Overall Conversion Funnel (horizontal bar)"),
      bullet("Figure 06 — Cost per Acquisition (CPA) by Channel (horizontal bar)"),
      bullet("Figure 07 — Campaign Cost vs Revenue Scatter Plot"),
      bullet("Figure 08 — ROAS Heatmap: Channel × Campaign Type"),
      bullet("Figure 09 — Pareto Chart: Top 20 Campaigns by Revenue"),
      bullet("Figure 10 — Weekly Revenue Trend (area chart)"),

      heading("4.5  Phase 5 — Dashboard Development", HeadingLevel.HEADING_2),
      para(run("A 5-sheet Excel dashboard was built using openpyxl (dashboard/Marketing_Analytics_Dashboard.xlsx):")),
      bullet("Sheet 1 — Overview: KPI cards, channel summary table"),
      bullet("Sheet 2 — Channel ROI: ROAS table with recommendations, bar chart"),
      bullet("Sheet 3 — Campaign Data: Full dataset with conditional ROAS formatting"),
      bullet("Sheet 4 — Monthly Trend: Time-series table with embedded line chart"),
      bullet("Sheet 5 — Top Campaigns: Pareto table, insights & recommendations"),

      pageBreak(),

      // ─── SECTION 5: RESULTS ───────────────────────────────────────────────
      heading("5.  Results & Analysis", HeadingLevel.HEADING_1),
      divider(),

      heading("5.1  Overall KPI Summary", HeadingLevel.HEADING_2),
      kpiTable(),
      para(run("")),
      para([
        run("The overall ROAS of 3.84x indicates that for every rupee spent on marketing, the business generates approximately "),
        run("₹3.84 in revenue", { bold: true, color: GREEN }),
        run(". Total profit of $877,611 on a spend of $308,779 represents a "),
        run("284% return on marketing investment", { bold: true, color: GREEN }),
        run(" — a strong result that reflects the high efficiency of email and SEO channels in the portfolio."),
      ]),

      heading("5.2  Channel Performance Analysis", HeadingLevel.HEADING_2),
      channelTable(),
      para(run("")),

      heading("5.3  Key Findings", HeadingLevel.HEADING_2),
      bullet("Email marketing delivers the highest ROAS at 9.25x with the lowest CPA ($0.69) — by far the most cost-efficient channel", { bold: false }),
      subBullet("Reason: No media cost (CPC ≈ $0). Only infrastructure cost. High engagement (18.54% CTR)."),
      bullet("SEO Organic achieves 6.08x ROAS at virtually zero cost — strong justification for content marketing investment"),
      subBullet("Reason: Organic traffic has no per-click cost. Scales with content volume."),
      bullet("Google Ads generates 64.4% of total revenue despite representing only 20% of campaigns"),
      subBullet("This concentration risk warrants diversification but also justifies maintaining/growing the budget."),
      bullet("Instagram Ads shows the lowest ROAS (2.60x) and highest CPA ($77.52) — flagged for review"),
      subBullet("Low conversion rate (1.60%) suggests poor landing page alignment or audience mismatch."),
      bullet("Pareto analysis confirms the 80/20 rule: a minority of high-performing campaigns drive the majority of revenue"),

      pageBreak(),

      // ─── SECTION 6: INSIGHTS & RECOMMENDATIONS ────────────────────────────
      heading("6.  Business Insights & Recommendations", HeadingLevel.HEADING_1),
      divider(),

      heading("6.1  Budget Reallocation Strategy", HeadingLevel.HEADING_2),
      para(run("Based on ROAS analysis, the following budget changes are recommended for the next quarter:")),
      para(run("")),
      new Table({
        width: { size: W, type: WidthType.DXA },
        columnWidths: [2000, 1500, 1800, 4060],
        rows: [
          new TableRow({ children: [headerCell("Channel",2000), headerCell("Current Spend",1500), headerCell("Recommended Action",1800), headerCell("Justification",4060)] }),
          ...([
            ["Email", "$12,129", "↑ Increase 40%", "Highest ROAS (9.25x). Scale automation. Near-zero incremental cost."],
            ["SEO / Content", "$24", "↑ Invest in content", "6.08x ROAS with zero ad spend. Content investment compounds over time."],
            ["Google Ads", "$184,537", "↔ Maintain / slight increase", "Highest revenue channel (64%). Optimize keywords and bidding strategies."],
            ["Facebook Ads", "$54,406", "↓ Reduce 15%", "ROAS 2.95x is below portfolio average. Improve creative and targeting."],
            ["Instagram Ads", "$57,683", "↓ Reduce 20%", "Lowest ROAS (2.60x). A/B test creatives. Improve landing page CRO."],
          ]).map((r, i) => new TableRow({
            children: r.map((v, j) => {
              const bg = v.includes("↑") ? GREEN_BG : v.includes("↓") ? ORANGE_BG : (i%2===0?GRAY:"FFFFFF");
              const color = v.includes("↑") ? GREEN : v.includes("↓") ? "C0392B" : "000000";
              return dataCell(v, [2000,1500,1800,4060][j], bg, color, j===2);
            })
          }))
        ]
      }),
      para(run("")),

      heading("6.2  Campaign Optimisation Recommendations", HeadingLevel.HEADING_2),
      bullet("Implement A/B testing for Instagram ad creatives — test image vs. video, different CTAs"),
      bullet("Audit Google Ads keyword targeting — pause low-quality-score keywords to reduce CPC"),
      bullet("Build a drip email automation workflow to capitalise on the channel's 9.25x ROAS"),
      bullet("Create retargeting audiences from high-intent website visitors for Facebook/Instagram"),
      bullet("Develop a content calendar for SEO — targeting high-volume, low-competition keywords"),
      bullet("Set budget caps on underperforming campaigns to prevent continued overspend"),

      heading("6.3  Dashboard Usage Recommendations", HeadingLevel.HEADING_2),
      bullet("Review Channel ROI sheet weekly — flag any channel with ROAS dropping below 2.5x"),
      bullet("Use Monthly Trend sheet to identify seasonal peaks and pre-allocate budget accordingly"),
      bullet("Monitor Top Campaigns sheet for Pareto shifts — ensure revenue is not over-concentrated"),
      bullet("Refresh data monthly by re-running the Python pipeline and updating the Excel dashboard"),

      pageBreak(),

      // ─── SECTION 7: FUTURE ENHANCEMENTS ───────────────────────────────────
      heading("7.  Future Enhancements", HeadingLevel.HEADING_1),
      divider(),

      heading("7.1  Predictive Marketing Analytics", HeadingLevel.HEADING_2),
      para([
        run("Using historical campaign data, machine learning models can be trained to "),
        run("forecast future campaign performance", { bold: true }),
        run(" before budget is committed. A time-series forecasting model (ARIMA, Prophet) on monthly revenue data would enable proactive budget planning."),
      ]),

      heading("7.2  Customer Lifetime Value (CLV) Tracking", HeadingLevel.HEADING_2),
      para([
        run("Integrating customer-level transaction data would enable CLV calculation — attributing long-term customer value to acquisition channels. This would fundamentally improve CPA comparisons across channels with different customer retention profiles."),
      ]),

      heading("7.3  Multi-Touch Attribution Modelling", HeadingLevel.HEADING_2),
      para([
        run("Currently, conversions are attributed to a single channel (last-touch). A "),
        run("multi-touch attribution model", { bold: true }),
        run(" (linear, time-decay, or data-driven) would more fairly distribute conversion credit across the customer journey — email discovers the brand, Google Ads retargets, and Instagram closes the conversion."),
      ]),

      heading("7.4  Real-Time Dashboard Integration", HeadingLevel.HEADING_2),
      para([
        run("Connecting to live APIs (Google Ads API, Meta Marketing API, Mailchimp API) would enable a real-time Power BI or Tableau dashboard. This would eliminate the monthly data refresh cycle and enable daily performance monitoring."),
      ]),

      heading("7.5  Automated Alerting System", HeadingLevel.HEADING_2),
      para([
        run("A Python-based monitoring script could send automated email or Slack alerts when campaign ROAS drops below threshold, budget is about to be exhausted, or CTR declines significantly — enabling proactive campaign management."),
      ]),

      pageBreak(),

      // ─── SECTION 8: CONCLUSION ────────────────────────────────────────────
      heading("8.  Conclusion", HeadingLevel.HEADING_1),
      divider(),
      para([
        run("This project successfully demonstrates how a structured data analytics workflow can transform raw marketing data into clear, measurable, and actionable intelligence. Starting from simulated campaign data and progressing through SQL analysis, Python-based EDA, and a formatted Excel dashboard, the project delivers a complete view of marketing ROI across all channels."),
      ], { after: 120 }),
      para([
        run("The analysis revealed that "),
        run("Email and SEO Organic channels offer the best return on investment", { bold: true, color: GREEN }),
        run(", while "),
        run("paid social channels (Instagram, Facebook) require strategic improvement", { bold: true, color: "C0392B" }),
        run(". Google Ads — while the most expensive — remains the primary revenue driver and should be maintained and optimised rather than reduced."),
      ], { after: 120 }),
      para([
        run("The 80/20 Pareto finding confirms that marketing resources can be significantly optimised by doubling down on the top-performing campaigns and channels. A budget reallocation of even 15–20% toward higher-ROAS channels could meaningfully improve overall marketing profitability."),
      ], { after: 120 }),
      para([
        run("As a portfolio project, this work demonstrates proficiency in the complete data analytics stack — "),
        run("data engineering, SQL, Python analytics, statistical visualisation, and business intelligence", { bold: true }),
        run(" — and provides a strong foundation for real-world marketing analytics roles."),
      ]),
      para(run("")),
      divider(),

      // ─── SECTION 9: PROJECT STRUCTURE ─────────────────────────────────────
      heading("9.  Project File Structure", HeadingLevel.HEADING_1),
      divider(),
      para(run("The submitted ZIP archive contains the following structure:"), { after: 80 }),
      new Table({
        width: { size: W, type: WidthType.DXA },
        columnWidths: [3600, 5760],
        rows: [
          new TableRow({ children: [headerCell("File / Folder", 3600), headerCell("Description", 5760)] }),
          ...([
            ["data/campaigns.csv", "50 marketing campaigns with 18 KPI attributes"],
            ["data/daily_performance.csv", "2,486 daily performance observations"],
            ["data/kpi_summary.csv", "Aggregated KPI summary by channel"],
            ["data/sql_results/", "CSV exports of all 6 SQL query results"],
            ["scripts/generate_data.py", "Python data simulation engine"],
            ["scripts/eda_visualization.py", "EDA & 10 chart generation script"],
            ["scripts/run_sql_queries.py", "SQL query execution via SQLite"],
            ["scripts/build_dashboard.py", "Excel dashboard builder"],
            ["sql/marketing_queries.sql", "15 SQL query library with comments"],
            ["dashboard/Marketing_Analytics_Dashboard.xlsx", "5-sheet formatted Excel dashboard"],
            ["reports/Marketing_Analytics_Report.docx", "This project report document"],
            ["reports/figures/", "10 PNG visualisation figures (01–10)"],
            ["README.md", "Setup and run instructions"],
          ]).map((r, i) => new TableRow({
            children: r.map((v, j) =>
              dataCell(v, [3600,5760][j], i%2===0 ? GRAY : "FFFFFF",
                j===0 ? MID_BLUE : "000000", j===0))
          }))
        ]
      }),
      para(run("")),

      // ─── SECTION 10: REFERENCES ───────────────────────────────────────────
      heading("10.  References & Data Sources", HeadingLevel.HEADING_1),
      divider(),
      bullet("WordStream (2024). Google Ads Benchmarks by Industry. wordstream.com/google-adwords"),
      bullet("Mailchimp (2024). Email Marketing Benchmarks and Statistics. mailchimp.com/resources/email-marketing-benchmarks"),
      bullet("Meta Business (2024). Facebook Ads Performance Benchmarks. business.facebook.com"),
      bullet("HubSpot (2024). State of Marketing Report 2024. hubspot.com/state-of-marketing"),
      bullet("Google (2024). Think with Google — Marketing Insights. thinkwithgoogle.com"),
      bullet("McKinsey & Company (2023). The value of getting personalisation right. mckinsey.com"),
      bullet("Python Software Foundation. pandas, NumPy, Matplotlib, Seaborn documentation. python.org"),
      bullet("Microsoft Corporation. openpyxl Documentation. openpyxl.readthedocs.io"),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  const outPath = path.join(OUT, "Marketing_Analytics_Report.docx");
  fs.writeFileSync(outPath, buf);
  console.log("✅ Report saved:", outPath);
});
