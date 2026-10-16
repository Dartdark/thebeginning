"""Builds reports/Trading_Business_Plan.pdf (2026-10-16): the plan as a business report.
All numbers come from the repo's analyses (see FUNDED_PLAN.md, TIER_LIST.md, DEVELOPMENT_PROCESS.md).
  python3 reports/build_business_plan.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether)

OUT = "reports/Trading_Business_Plan.pdf"
NAVY = colors.HexColor("#1F3A5F"); TEAL = colors.HexColor("#2A7F8E"); LIGHT = colors.HexColor("#EEF3F8")
GREEN = colors.HexColor("#E6F4EA"); AMBER = colors.HexColor("#FFF4E0"); GREY = colors.HexColor("#5A6470")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=NAVY, fontSize=17, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=TEAL, fontSize=12.5, spaceBefore=10, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9.6, leading=13.2, spaceAfter=5)
BL = ParagraphStyle("BL", parent=B, leftIndent=12, bulletIndent=2)
SM = ParagraphStyle("SM", parent=B, fontSize=8, leading=10.5, textColor=GREY)
CELL = ParagraphStyle("CELL", parent=B, fontSize=8.4, leading=10.6, spaceAfter=0)
CELLB = ParagraphStyle("CELLB", parent=CELL, fontName="Helvetica-Bold")
HEAD = ParagraphStyle("HEAD", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)


def p(t, s=B): return Paragraph(t, s)
def bullets(items): return [Paragraph(i, BL, bulletText="•") for i in items]


def table(rows, widths, highlight=None, bold_first_col=False):
    data = [[Paragraph(str(c), HEAD) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(str(c), CELLB if (bold_first_col and i == 0) else CELL) for i, c in enumerate(r)])
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D3DE")),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for r in (highlight or []):
        st.append(("BACKGROUND", (0, r), (-1, r), GREEN))
    t.setStyle(TableStyle(st)); return t


def callout(text, bg=AMBER):
    t = Table([[Paragraph(text, B)]], colWidths=[7.0 * inch])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 0.6, TEAL),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 7.5); c.setFillColor(GREY)
    c.drawString(0.75 * inch, 0.5 * inch, "Algorithmic Futures Trading Plan  |  Business Report  |  October 2026")
    c.drawRightString(7.75 * inch, 0.5 * inch, f"Page {d.page}")
    c.restoreState()


def cover(c, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, 6.2 * inch, 8.5 * inch, 4.8 * inch, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 28)
    c.drawString(0.8 * inch, 9.0 * inch, "Algorithmic Futures")
    c.drawString(0.8 * inch, 8.5 * inch, "Trading Plan")
    c.setFont("Helvetica", 14); c.drawString(0.8 * inch, 7.9 * inch, "Business report: strategy, funding model, roadmap and risk")
    c.setFont("Helvetica", 11); c.drawString(0.8 * inch, 7.3 * inch, "NQ / MNQ and MCL futures  |  MultiCharts automation  |  Apex Trader Funding")
    c.drawString(0.8 * inch, 6.9 * inch, "October 16, 2026")
    c.setFillColor(NAVY); c.setFont("Helvetica-Bold", 12); c.drawString(0.8 * inch, 5.4 * inch, "In one sentence")
    c.setFont("Helvetica", 11); c.setFillColor(colors.black)
    lines = ["Use prop-firm accounts as a low-cost live test bench and funding source for a",
             "diversified, backtested set of automated futures strategies; scale to Apex's",
             "20-account limit once the edge is confirmed live, and channel payouts into a",
             "personal trading account where proven strategies can grow without payout caps."]
    for i, l in enumerate(lines): c.drawString(0.8 * inch, (5.05 - 0.27 * i) * inch, l)
    c.setFont("Helvetica-Oblique", 8); c.setFillColor(GREY)
    c.drawString(0.8 * inch, 1.0 * inch, "All performance figures are backtests (2018-2026) and simulations, not guarantees. Live results are expected to be lower.")
    c.restoreState()


story = [PageBreak()]

# 1 Executive summary
story += [p("1. Executive summary", H1),
          p("The business runs a portfolio of eight automated futures strategies on proprietary-trading (\"prop\") accounts at "
            "Apex Trader Funding. Prop accounts let us trade with the firm's capital: our only cost is the evaluation and "
            "activation fees, while profits are paid out up to a fixed cap per account. The plan has three stages: "
            "<b>prove</b> the edge live on a few accounts, <b>scale</b> to Apex's 20-account limit, and <b>compound</b> payouts "
            "in a personal account that has no payout cap."),
          table([["Key figure", "Value", "What it means"],
                 ["Strategy edge (backtest, 1 NQ each)", "~$101k / year, Sharpe 2.75", "Max drawdown $24k; 19% of months lose money"],
                 ["Share of profit that is real skill", "92% (alpha t-stat 7.1)", "Only 8% comes from simply being long NQ"],
                 ["Evaluation pass rate", "50% (50K) / 42% (150K)", "Zero-skill baseline is ~40%"],
                 ["Payout per funded account", "$12.5k (50K) / $19.7k (150K)", "Within 2 years; blown 3% / 0%"],
                 ["Value per account slot, 3 years", "$34.8k (50K) / $52.8k (150K)", "Net of all fees"],
                 ["Year-1 outlook", "+$29k (3 accounts), ~+$115k (ramp to 20)", "Backtest-based; ~1/3 of that if live keeps 75% of the edge"],
                 ["Cost of testing the edge live", "~$400-600", "If it fails, we stop after Phase 1"]],
                [2.1 * inch, 2.0 * inch, 2.9 * inch]),
          Spacer(1, 8),
          callout("<b>Recommendation.</b> Continue the 3-account test on <b>50K EOD</b> accounts (bought one at a time, $59) for about two "
                  "months. If live results reach at least 75% of the backtest over ~40-70 trades, scale with <b>150K No-Activation</b> "
                  "accounts at two per week up to 20, and open a small personal account from month 3 using the first payouts.", GREEN)]

# 2 Strategy portfolio
story += [PageBreak(), p("2. The strategy portfolio", H1),
          p("Every strategy is automated in MultiCharts, trades Nasdaq-100 futures (MNQ) or crude oil (MCL), and is flat by "
            "15:59 CT. Each was backtested 2018-2026 with realistic costs ($7.25 commission plus one tick of slippage per fill), "
            "confirmed trade-by-trade in MultiCharts, and ranked on a quality scale from S+ (best) to F."),
          table([["Strategy", "Idea in plain terms", "Rank", "Role"],
                 ["Overnight Bias ML", "Trades the morning in the direction the overnight session leaned, filtered by a model", "S", "Biggest payout driver"],
                 ["Vault Break", "Buys / sells breakouts of the day's 'noise band'; wins ~66% of trades", "A", "Engine of the evaluation; funded core"],
                 ["Bridge Monday Long", "Holds a long from Sunday evening into Monday in uptrends", "A", "Uncorrelated Monday drift"],
                 ["Monday Long", "Our own Monday long with a different trigger", "A", "Uncorrelated"],
                 ["Late-Day Flow", "Follows strong moves into the last hour (ETF rebalancing flows)", "A", "Afternoon diversifier"],
                 ["Expiration Open Short", "Short on monthly options-expiration mornings (dealer hedging)", "A", "Forced-flow event"],
                 ["CL Sunday Gap Fade", "Fades crude oil's Sunday-open gap-ups (weekend overreaction)", "A", "Different market; cuts blow-ups"],
                 ["NFP Fade", "Fades the jobs-report spike", "B", "Small, event-based"]],
                [1.45 * inch, 3.25 * inch, 0.55 * inch, 1.75 * inch]),
          Spacer(1, 6),
          p("<b>Why it should keep working.</b> The strategies are built around repeatable market mechanics (overnight positioning, "
            "forced fund flows, options expiration, weekend gaps) rather than chart patterns. They have near-zero correlation with "
            "each other, and the combined plan is positive in both 2018-22 and 2023-26."),
          p("<b>Quality controls applied to every strategy:</b> realistic costs; random-direction placebo; results split by year and "
            "by long / short; multiple-testing correction (deflated Sharpe ratio); an independent re-implementation by a separate "
            "checker; and a regression showing the profit is not just market drift.")]

# 3 Funding model
story += [PageBreak(), p("3. Funding model: Apex Trader Funding", H1),
          p("An Apex account starts with an <b>evaluation</b>: reach a profit target within 30 days without breaching a trailing "
            "drawdown. Passing unlocks a <b>Performance Account (PA)</b> that pays out up to six times, then closes. A new "
            "evaluation replaces it. Up to 20 accounts can run at once."),
          table([["Rule", "50K account", "150K account"],
                 ["Evaluation profit target", "$3,000", "$9,000"],
                 ["Max drawdown (end-of-day trailing)", "$2,000", "$4,000"],
                 ["Daily loss limit (pauses the day)", "$1,000", "$2,000"],
                 ["Max contracts", "6 mini / 60 micro", "12 mini / 120 micro"],
                 ["Payout ladder (6 payouts, then closes)", "1,500 / 1,500 / 2,000 / 2,500 / 2,500 / 3,000 = $13,000",
                  "2,500 / 3,000 / 3,000 / 3,000 / 4,000 / 5,000 = $20,500"],
                 ["Payout conditions", "5 days of $250+, balance $52,600+, 50% consistency", "5 days of $350+, balance $154,600+, 50% consistency"]],
                [2.2 * inch, 2.4 * inch, 2.4 * inch]),
          p("Source: Apex pricing and rules pages (screenshots in the repository, October 15, 2026).", SM),
          p("Choosing the account type", H2),
          p("Each size comes with or without an activation fee. Trading rules and payouts are identical; only the cost differs. "
            "Because some evaluations fail, the real cost is: evaluation price x tries needed + activation fee."),
          table([["Rank", "Account type", "Price", "Cost per funded account", "Net per slot over 3 years"],
                 ["1", "150K No-Activation", "$249", "$598", "$52,788"],
                 ["2", "150K EOD, 5-pack", "$199 + $150 activation", "$628", "$52,682"],
                 ["3", "150K EOD, single", "$219 + $150 activation", "$676", "$52,525"],
                 ["4", "50K EOD, 5-pack (most cost-efficient)", "$24.50 + $130 activation", "$179", "$34,813"],
                 ["5", "50K No-Activation, 5-pack", "$109", "$218", "$34,751"],
                 ["6", "50K No-Activation, single", "$119", "$238", "$34,690"],
                 ["7", "50K EOD, single", "$59 + $130 activation", "$248", "$34,604"]],
                [0.55 * inch, 2.2 * inch, 1.6 * inch, 1.35 * inch, 1.3 * inch], highlight=[1, 4]),
          Spacer(1, 6),
          bullets(["<b>Test phase:</b> single 50K EOD ($59 + $130 activation on a pass, ~$248 per funded account). The 5-pack is cheaper ($179) but all five evaluations start the day of purchase, so they trade identical days on the copier and pass or fail together: one bet placed five times. Singles keep accounts 5-10 trading days apart.",
                   "<b>Scale phase:</b> 150K No-Activation. Each slot earns ~$18k more over 3 years; with a 20-account cap that is what counts.",
                   "<b>Speed:</b> 50K reaches its first payout ~2 weeks sooner (median 87 vs 95 trading days); 150K pays ~50% more.",
                   "Fees are only 2-4% of payouts on every path, so account size matters far more than the fee option."])]

# 4 Financial projections
story += [PageBreak(), p("4. Financial projections", H1),
          p("Simulated on real market history (start dates 2018-2023, three-year windows), with every account running the plan "
            "through the exact Apex rules. These are backtest-based; Section 7 shows a weaker-edge case."),
          p("Single funded account", H2),
          table([["", "50K (current sizing)", "150K (plan x 1.5)"],
                 ["Payouts within 1 year", "$10,184", "$15,731"],
                 ["Payouts within 2 years", "$12,450 (cap $13,000)", "$19,743 (cap $20,500)"],
                 ["Accounts blown", "3%", "0%"],
                 ["All 6 payouts within 2 years", "94%", "91%"]],
                [2.4 * inch, 2.3 * inch, 2.3 * inch]),
          p("Three accounts: the first year month by month", H2),
          table([["After", "Typical (median)", "Bad case (10th pct)", "Good case (90th pct)", "Any payout received"],
                 ["1 month", "-$400", "-$520", "-$250", "1%"],
                 ["3 months", "-$455", "-$755", "+$5,595", "36%"],
                 ["6 months", "+$4,045", "-$705", "+$19,385", "71%"],
                 ["12 months", "+$29,345", "+$3,455", "+$38,110", "96%"]],
                [1.0 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch]),
          p("Month 1 is fees only: evaluations pass in about 6 trading days, but Apex payouts need the balance built up first, so "
            "the first payout usually arrives in month 2-4.", SM),
          p("Scaling to 20 accounts (cash after fees, median)", H2),
          table([["Schedule", "6 months", "12 months", "24 months", "36 months", "Most cash outlay"],
                 ["Stay at 3 accounts", "$4.0k", "$29k", "$60k", "$90k", "-$0.8k"],
                 ["Recommended: 3 for 2 months, then +2 per week", "$8.2k", "$116k", "$341k", "$564k", "-$4.4k"],
                 ["+2 per week immediately", "$19.3k", "$151k", "$366k", "$578k", "-$4.5k"],
                 ["All 20 at once", "$27.3k", "$196k", "$404k", "$604k", "-$5.7k"]],
                [2.3 * inch, 0.8 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch, 1.05 * inch], highlight=[2]),
          p("Scaling figures use 50K economics; 150K slots pay about 50% more per slot. The recommended schedule gives up some "
            "upside in exchange for confirming the edge before committing fees to 20 accounts.", SM),
          p("Personal account (Phase 3 onward)", H2),
          p("Without Apex's caps, the full plan at 1 NQ per strategy made about <b>$101k a year</b> in the backtest with a <b>$24k</b> "
            "maximum drawdown. Starting at 1/10 size (micro contracts) needs roughly <b>$10k</b>, with a historical worst drawdown "
            "near $2.4k; size grows with the account.")]

# 5 Roadmap
story += [PageBreak(), p("5. Roadmap", H1),
          table([["Phase", "Timing", "Actions", "Gate to move on"],
                 ["1. Prove", "Now to ~week 8",
                  "3 x 50K EOD accounts, added 5-10 trading days apart (#2 Tue 10/20, #3 ~10/27). Weekly MultiCharts reports for live-vs-backtest tracking.",
                  "~40-70 live trades, live average at least 75% of backtest, no drift alarm"],
                 ["2. Scale", "~Month 2-5",
                  "Add 150K No-Activation accounts, 2 per week, to 20 total; replace finished 50K accounts with 150K. Four copier masters (50K / 150K x evaluation / funded).",
                  "Live edge holds; no clustered blow-ups"],
                 ["3. Personal account", "From month 3",
                  "Open with ~$10k from payouts; run the plan at 1/10 size (MNQ). Add Twin Continuation at small size (stop capped at 1 ATR).",
                  "6-12 months of live results matching backtest"],
                 ["4. Grow", "Month 6-12+",
                  "Personal account to full size; promote live-confirmed strategies to S+; new strategies enter through the lifecycle below.",
                  "Ongoing monitoring"]],
                [0.9 * inch, 0.9 * inch, 3.3 * inch, 1.9 * inch], bold_first_col=True),
          p("Strategy lifecycle (how new strategies are added)", H2),
          table([["Stage", "Where", "Gate"],
                 ["1. Research", "Python backtest 2018-2026", "Passes the multiple-testing bar, beats a random-direction placebo, positive in both 2018-22 and 2023-26"],
                 ["2. Confirmation", "MultiCharts + independent checker", "MultiCharts trades match the research version; checker passes it"],
                 ["3. Apex incubation", "Smallest size, on accounts running the full plan", "~40 live trades at 75%+ of backtest, no drift alarm, no rise in blow-ups"],
                 ["4. Live", "Personal account", "Sized so the worst drawdown is 20-30% of the account"]],
                [1.3 * inch, 2.1 * inch, 3.6 * inch], bold_first_col=True),
          p("Demotion: a first drift alarm halves the strategy's size; a second alarm or a live average below half the backtest "
            "sends it back to incubation or retirement.", SM)]

# 6 Governance & ranking
story += [p("6. Quality ranking and governance", H1),
          table([["Rank", "Meaning"],
                 ["S+", "Meets every S requirement and is confirmed in live trading (40+ live trades at 75%+ of backtest). Empty today; Overnight Bias ML is first in line."],
                 ["S", "Extreme profit and edge: ~$20k+ a year per NQ, t-stat 4.5+, profit factor 2+, 8 of 9 years positive, scalable."],
                 ["A", "Very strong: t 2.5+, profit factor 1.4+, 7+ of 9 years positive, MultiCharts-confirmed."],
                 ["B / C", "Real but smaller, or regime-dependent edges."],
                 ["D / F", "Weak after costs, or no edge. Over 200 ideas tested; most end here."]],
                [0.7 * inch, 6.3 * inch], bold_first_col=True),
          Spacer(1, 4),
          bullets(["<b>Live monitoring:</b> weekly reports feed a drift alarm per strategy (OK / WATCH / ALARM).",
                   "<b>Operations:</b> an always-on machine (no sleep or forced updates), one copier master per account type and phase, "
                   "and an error log of every MultiCharts issue solved.",
                   "<b>Compliance:</b> every account runs the full plan on one symbol per market, so positions net within an account and "
                   "never oppose each other across accounts (cross-account hedging is prohibited by Apex)."])]

# 7 Risks
story += [PageBreak(), p("7. Risks and mitigations", H1),
          table([["Risk", "What could happen", "Mitigation"],
                 ["Backtest overstates the edge", "Strategies were selected on the same history they are tested on; live results are typically lower",
                  "Phase-1 gate before scaling; multiple-testing correction; independent checker; drift alarm"],
                 ["Weaker live edge (75% case)", "Year 1: ~$10k with 3 accounts, ~$46k with 20; bad-case first year with 20 accounts about -$10k",
                  "Scale only after the gate; half size on any ALARM"],
                 ["Correlated accounts", "All accounts trade the same signals, so a bad month hits all of them together",
                  "Stagger account starts 5-10 trading days apart; gradual ramp"],
                 ["Prop-firm rule or payout changes", "Apex can change prices, rules or payout timing",
                  "Diversify into the personal account; keep fees a small share of payouts"],
                 ["Operational failures", "Disconnects, rejected orders, PC sleep (already seen in week 1)",
                  "One-account shakedown week, error log, always-on machine, weekly report checks"],
                 ["Personal capital at risk", "Drawdowns in the personal account are real money",
                  "Start at 1/10 size with ~$10k; full size only after 6-12 months of confirmation"],
                 ["Event concentration", "The CL fade earns ~85% of its profit on oil-news weekends",
                  "Small position (2 MCL); expected quiet stretches; watchlist review after each event"]],
                [1.5 * inch, 2.75 * inch, 2.75 * inch], bold_first_col=True)]

# 8 Next steps
story += [p("8. Immediate next steps", H1),
          table([["When", "Action"],
                 ["Fri 10/16", "Expiration Open Short trades on account #1: check fill, size and exit"],
                 ["Sun 10/18, 19:00 CT", "Bridge Monday Long enters: confirm position and size on Monday morning"],
                 ["Tue 10/20", "If both were clean, add account #2 (single 50K EOD, $59)"],
                 ["~Tue 10/27", "Add account #3"],
                 ["Every week", "Export MultiCharts reports to the live/ folder for the live-vs-backtest check"],
                 ["~Mid-December", "Phase-1 gate decision: scale with 150K No-Activation, or review"]],
                [1.5 * inch, 5.5 * inch], bold_first_col=True),
          Spacer(1, 10),
          p("Appendix: account settings", H2),
          table([["Account", "Settings"],
                 ["50K evaluation", "Vault Break 8 MNQ; Overnight Bias ADX30 risk $1,100; Bridge Monday 2 MNQ; Expiration Open Short risk $500"],
                 ["50K funded", "Vault Break 3 MNQ (1 on flagged days); Overnight Bias ML risk $400; Monday Long 1; Expiration Open Short $700; "
                                "Late-Day Flow 2; NFP Fade $500; Bridge Monday 1; CL fade 2 MCL. Full size once the cushion is $1,500, half size below"],
                 ["150K evaluation", "Evaluation set x 2.5: Vault Break 20 MNQ; Overnight Bias ADX30 $2,750; Bridge Monday 5; Expiration Open Short $1,250"],
                 ["150K funded", "Funded set x 1.5: Vault Break 4 (1 flagged); Overnight Bias ML $600; Monday Long 1; Expiration Open Short $1,050; "
                                 "Late-Day Flow 3; NFP Fade $750; Bridge Monday 1; CL fade 3 MCL. Full size from a $3,000 cushion"]],
                [1.3 * inch, 5.7 * inch], bold_first_col=True),
          Spacer(1, 10),
          p("Disclaimer: all figures are historical backtests and simulations using Apex's published rules as of October 2026. "
            "They are estimates, not guarantees; futures trading involves substantial risk of loss.", SM)]

flat = []
for x in story:
    flat.extend(x if isinstance(x, list) else [x])
story = flat

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.7 * inch,
                        bottomMargin=0.8 * inch, title="Algorithmic Futures Trading Plan", author="Trading plan")
doc.build(story, onFirstPage=cover, onLaterPages=footer)
print("wrote", OUT)
