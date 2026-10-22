"""Builds reports/Performance_Report_Guide.pdf (2026-10-20): what to look for on a strategy performance report to decide
whether a strategy is bad, good or great. Thresholds follow this repo's testing standard (CLAUDE.md, DEVELOPMENT_PROCESS.md)
and tier list (TIER_LIST.md); the worked example is Relative Strength NQ / ES (analysis/relative_strength_test.py).
  python3 reports/build_report_guide.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

OUT = "reports/Performance_Report_Guide.pdf"
NAVY = colors.HexColor("#1F3A5F"); TEAL = colors.HexColor("#2A7F8E"); LIGHT = colors.HexColor("#EEF3F8")
RED = colors.HexColor("#FBE7E7"); AMBER = colors.HexColor("#FFF4E0"); GREEN = colors.HexColor("#E6F4EA")
GREY = colors.HexColor("#5A6470")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=NAVY, fontSize=17, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=TEAL, fontSize=12.5, spaceBefore=10, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=9.6, leading=13.2, spaceAfter=5)
BL = ParagraphStyle("BL", parent=B, leftIndent=12, bulletIndent=2)
SM = ParagraphStyle("SM", parent=B, fontSize=8, leading=10.5, textColor=GREY)
CELL = ParagraphStyle("CELL", parent=B, fontSize=8.2, leading=10.4, spaceAfter=0)
CELLB = ParagraphStyle("CELLB", parent=CELL, fontName="Helvetica-Bold")
HEAD = ParagraphStyle("HEAD", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)


def p(t, s=B): return Paragraph(t, s)
def bullets(items): return [Paragraph(i, BL, bulletText="•") for i in items]


def table(rows, widths, shade=None):
    """shade: {column index: colour} for the bad / good / great columns."""
    data = [[Paragraph(str(c), HEAD) for c in rows[0]]]
    for r in rows[1:]:
        data.append([Paragraph(str(c), CELLB if i == 0 else CELL) for i, c in enumerate(r)])
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D3DE")),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for c, col in (shade or {}).items():
        st.append(("BACKGROUND", (c, 1), (c, -1), col))
    t.setStyle(TableStyle(st)); return t


def footer(canvas, doc):
    canvas.saveState(); canvas.setFont("Helvetica", 7.5); canvas.setFillColor(GREY)
    canvas.drawString(0.75 * inch, 0.5 * inch, "Performance Report Guide  |  thebeginning repo  |  2026-10-20")
    canvas.drawRightString(7.75 * inch, 0.5 * inch, f"Page {doc.page}"); canvas.restoreState()


S = []
S += [p("Reading a Strategy Performance Report", H1),
      p("How to tell from a backtest report whether a strategy is <b>bad</b>, <b>good</b> or <b>great</b>, with the "
        "thresholds this project uses (NQ / ES futures, MultiCharts reports, Apex accounts and a future personal account)."),
      p("<b>Before anything else:</b> every number in this guide is <b>after costs</b> and <b>per 1 full contract</b> "
        "(1 NQ = 10 MNQ). Our MultiCharts backtests usually run with commission and slippage at 0 (Python adds them), so "
        "subtract the round-trip cost per trade yourself: <b>NQ $17.25</b> ($7.25 commission + 1 tick on entry and exit), "
        "<b>ES $30</b>, CL / GC $34.50. A strategy that only works before costs is not a strategy.", B)]

S += [p("1. The 30-second triage", H2), p("If any of these fails, stop: the rest of the report doesn't matter yet.")]
S += bullets([
    "<b>Costs:</b> is the average trade at least <b>3x the round-trip cost</b> (NQ: about $50+ per trade)? Below 2x, a "
    "little extra slippage live wipes it out.",
    "<b>Enough trades:</b> at least <b>100</b>, better 300+. Twenty great trades prove nothing.",
    "<b>Profit factor after costs</b> above about <b>1.2</b>.",
    "<b>Years:</b> positive in most calendar years, not one great year carrying the rest (Periodical Returns, Annual).",
    "<b>Settings sheet:</b> the inputs, bar size, session and time zone are the ones you meant. Old inputs survive a code "
    "paste in MultiCharts, and that has broken backtests here before."])

S += [p("2. The main numbers: bad / good / great", H2),
      p("Where to find each one in the MultiCharts report is in the second column. t-stat, Sharpe, Calmar and the "
        "year count are quick to compute from the List of Trades sheet (or ask Claude: <i>analysis/metrics.py</i>).")]
rows = [["Metric", "Where (MultiCharts)", "Bad", "Good", "Great", "Why it matters"],
        ["Total trades", "Performance Summary", "< 100", "300+", "1,000+", "More trades = less luck. The t-stat grows with the square root of the count."],
        ["Average trade (after costs)", "Avg Trade, minus cost", "< 2x cost (NQ < $35)", "$75-200 per NQ", "$250+ per NQ", "Room for real-world slippage and fills."],
        ["Profit factor (after costs)", "Profit Factor", "< 1.15", "1.25-1.4", "1.5+ (2+ = exceptional)", "Gross win / gross loss. Above 3 on hundreds of trades: look for a bug."],
        ["t-stat = avg / st.dev x &radic;trades", "compute from List of Trades", "< 2", "2.5-3.5", "3.6+ (our multiple-testing bar)", "How sure the average isn't zero. The bar rises with every idea tested (TRIALS.csv)."],
        ["Years positive", "Periodical Returns: Annual", "6/9 or fewer", "7/9", "9/9", "An edge should show up in most years, not one."],
        ["Recent period (2023+) vs earlier", "split the List of Trades", "PF falls below ~1.1", "PF within ~0.1", "as good or better", "The best stand-in for 'will it keep working'."],
        ["Sharpe (daily, x &radic;252)", "compute; MC's is monthly", "< 0.5", "0.8-1.5", "1.5+", "Return per unit of day-to-day swing. Above 3: suspicious."],
        ["Sortino", "Performance Summary", "< 0.8", "1.2-2", "2+", "Like Sharpe but only counts down days; ~1.5-2x Sharpe is normal."],
        ["Calmar = yearly profit / max drawdown", "Return on Max Strategy DD / years", "< 0.5", "1-2", "2+", "How long a worst drawdown takes to earn back."],
        ["Max drawdown at the size you trade", "Max Strategy Drawdown", "> your limit", "< ~60% of it", "< ~40% of it", "Apex: $2,000 EOD trailing. Size so the backtest DD (and a Monte Carlo 95% DD) fits."],
        ["Longs vs shorts", "Long / Short columns", "one side loses", "both positive", "both PF 1.3+", "On NQ, longs ride the bull market; a long-only edge must beat random long days."],
        ["Top 5% of trades / net profit", "List of Trades, sort by profit", "> 100%", "< 70%", "< 50%", "If the best few trades are the whole profit, a quiet year loses money."]]
S += [table(rows, [1.15 * inch, 1.05 * inch, 0.8 * inch, 0.8 * inch, 0.9 * inch, 2.3 * inch], shade={2: RED, 3: AMBER, 4: GREEN})]
S += [Spacer(1, 4), p("Win rate on its own says nothing. 35% winners with winners 3x the losers is fine; 80% winners with "
                      "losers 6x the winners is a time bomb. Check <b>expectancy = win% x avg win - loss% x avg loss</b> "
                      "(= the average trade). For Apex, a <b>high win rate</b> helps: long losing streaks hit the $2,000 "
                      "trailing drawdown (look at Max Consecutive Losers x Avg Losing Trade at your size).", SM)]

S += [p("3. Red flags (signs of a curve fit or a bug)", H2)]
S += bullets([
    "<b>Many inputs, odd values</b> (a 37-minute window, a 1.83 multiplier) and results that change a lot when one input "
    "moves one step. Good strategies sit on a <b>plateau</b>: neighbouring settings work almost as well.",
    "<b>Only one period tested</b>, or the parameters picked on the same period the report shows. Ask for a 2018-22 / "
    "2023+ split and a walk-forward.",
    "<b>Costs off</b> (Commission 0 / Slippage 0 in the Settings sheet) and an average trade of a few ticks.",
    "<b>Fills too good:</b> limit orders filled just by touching the price (we require a trade-through), stop and target "
    "in the same bar without Bar Magnifier, or entries at a bar's close using that same close (look-ahead).",
    "<b>Session traps:</b> SetExitOnClose on a 24-hour chart exits at midnight, not 15:59; holidays and half-days "
    "trading into a 12:00 CT close; continuous-contract roll jumps (03:30 / 17:00 CT) inside a trade.",
    "<b>MultiCharts' 'Adjusted Net Profit' or 'Select Net Profit' far below Net Profit</b>, or negative: the profit "
    "comes from outliers.",
    "<b>A Sharpe above 3, PF above 3 or a straight-line equity curve</b> on hundreds of trades: almost always a bug.",
    "<b>Max drawdown is recent and the deepest ever</b>: the edge may be fading (watch it, don't panic).",
    "<b>The report shows great numbers on a source's word</b> ('proven', 'battle-tested', 'validated'): only our own "
    "test on our data counts."])

S += [p("4. What a report can't tell you (the extra checks we always run)", H2)]
S += [table([["Check", "Question it answers", "Pass"],
             ["Random-entry placebo", "Does the signal beat the same trades on random days / with a random side?", "p <= 0.05"],
             ["Out-of-sample / walk-forward", "Does it work on data it wasn't designed on?", "2023+ positive, similar PF"],
             ["Multiple testing (trials.py)", "Is it just the best of many tries?", "t >= the bar (3.6 now) or deflated Sharpe >= 0.95"],
             ["Monte Carlo (montecarlo.py)", "How bad can the drawdown get in another ordering of the same trades?", "95% DD fits your limit; P(hit $2,000 trail) < ~5% at plan size"],
             ["Independent checker", "Does a fresh rebuild from the rules alone give the same trades, with no leaks?", "PASS / PASS WITH CONCERNS"],
             ["Plan fit (bootstrapped bench)", "Does it add to (or replace part of) what we already trade?", "faster / more payouts without blown +1 pt"],
             ["Live tracking (drift alarm)", "Is the live average at least ~75% of the backtest?", "no ALARM after ~40 trades"]],
            [1.6 * inch, 3.4 * inch, 2.0 * inch])]

S += [p("5. Putting it together: the tiers", H2)]
S += [table([["Tier", "Rough numbers (after costs)"],
             ["S", "about $20,000+ a year per NQ, t 4.5+, PF 2+, 8/9 years positive, liquid enough to size up"],
             ["A", "t 2.5+, PF 1.4+ (1.9+ if it trades rarely), 7+ of 9 years positive, MultiCharts-confirmed"],
             ["B", "real, profitable edge: t 2-3.5 or PF 1.25-1.4, most years positive"],
             ["C", "positive but small or inconsistent: t 1.5-2.5, weak recent years"],
             ["D", "the effect exists but makes about nothing after costs / stops / rules"],
             ["F", "no edge, loses, flawed study, or can't be traded"]], [0.6 * inch, 6.4 * inch])]

S += [p("6. Worked example: Relative Strength NQ / ES (2026-10-20)", H2)]
S += [table([["Check", "Value", "Verdict"],
             ["Trades", "1,161 (2018-26)", "great"],
             ["Average trade after costs", "$306 per NQ (~18x the $17.25 cost)", "great"],
             ["Profit factor", "1.36 (longs 1.46, shorts 1.26)", "good"],
             ["t-stat", "4.0 (bar 3.6)", "great"],
             ["Years positive", "9/9", "great"],
             ["2018-22 vs 2023+", "$271 vs $344 a trade", "great"],
             ["Sharpe / Sortino / Calmar", "1.33 / 2.23 / 1.39", "good"],
             ["Max drawdown", "$28.5k per NQ = $2.9k per MNQ", "too big for Apex at 1 MNQ alone"],
             ["Top 5% of trades", "111% of the profit", "red flag"],
             ["Placebo / checker", "random side p 0.002 / PASS WITH CONCERNS", "pass"],
             ["Result", "B (PF just under A's 1.4); concerns: tail-dependence, 9:00-only, weak shorts", ""]],
            [1.7 * inch, 3.5 * inch, 1.8 * inch])]

S += [p("7. Checklist", H2)]
S += bullets([
    "Settings sheet: inputs, bar size, session, time zone, Bar Magnifier, commission / slippage as intended.",
    "Subtract costs: average trade >= 3x the round trip.",
    "Trades >= 100 (300+ preferred).",
    "Profit factor after costs >= 1.25 (great 1.5+).",
    "t-stat >= 2.5 (great: above the multiple-testing bar, 3.6 now).",
    "Positive in >= 7 of 9 years; 2023+ about as good as 2018-22.",
    "Sharpe >= 0.8 (daily), Calmar >= 1.",
    "Max drawdown at your size fits your limit with room (Apex: well under $2,000).",
    "Longs and shorts each checked; a long-only NQ edge beats random long days.",
    "Top 5% of trades < ~70% of the profit; Adjusted Net Profit still positive.",
    "No red flags from section 3.",
    "Then the extra checks (section 4): placebo, holdout, trials bar, Monte Carlo, checker, plan fit, live tracking."])
S += [Spacer(1, 10), p("Thresholds are rules of thumb from this project's testing standard (CLAUDE.md, "
                       "DEVELOPMENT_PROCESS.md) and tier list (TIER_LIST.md), not universal laws. Backtests are hypothetical; "
                       "live results usually come in below them (published anomalies lose roughly a quarter to a half "
                       "of their edge out of sample).", SM)]

if __name__ == "__main__":
    doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.75 * inch, title="Performance Report Guide",
                            author="Claude (thebeginning repo)")
    doc.build(S, onFirstPage=footer, onLaterPages=footer); print("wrote", OUT)
