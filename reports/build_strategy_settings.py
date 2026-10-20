"""Strategy settings sheet (PDF): the evaluation (combine) plan and the funded plan with every chart and input.
  python3 reports/build_strategy_settings.py      -> reports/Strategy_Settings.pdf
Keep in sync with NEW_CHAT_BRIEF.md and funded_strategies/FUNDED_PLAN.md when a size or input changes.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

OUT = "reports/Strategy_Settings.pdf"
UPDATED = "2026-10-20"
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=16, spaceAfter=6, textColor=colors.HexColor("#1F3A5F"))
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#1F3A5F"))
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=8.5, leading=11)
C = ParagraphStyle("C", parent=B, fontSize=7.6, leading=9.4)
CB = ParagraphStyle("CB", parent=C, fontName="Helvetica-Bold")
CW = ParagraphStyle("CW", parent=CB, textColor=colors.white)
NOTE = ParagraphStyle("N", parent=B, fontSize=8, textColor=colors.HexColor("#444444"))


def tbl(rows, widths, head_color="#1F3A5F"):
    data = [[Paragraph(str(x), CW if i == 0 else C) for x in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * inch for w in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(head_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B0B7C3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F9")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def foot(canvas, doc):
    canvas.saveState(); canvas.setFont("Helvetica", 7); canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(0.5 * inch, 0.35 * inch, f"Strategy settings - Apex accounts, MultiCharts via Rithmic - updated {UPDATED}")
    canvas.drawRightString(10.5 * inch, 0.35 * inch, f"page {doc.page}")
    canvas.restoreState()


s = []
s.append(Paragraph("Strategy Settings: Evaluation (Combine) and Funded Plans", H1))
s.append(Paragraph(f"Updated {UPDATED}. All times Central (CT, exchange time). MultiCharts on the QuantVPS (Chicago), Rithmic "
                   "(System Rithmic 01, Gateway Chicago Area). Code: the repo files named below (private repo: open on GitHub while "
                   "logged in, or <i>git pull</i> in C:\\TradingVault). Add new code as a NEW signal, never paste over an old one "
                   "(MultiCharts keeps old input values).", B))

# ---------------- Evaluation ----------------
s.append(Paragraph("1. Evaluation (combine) plan - Apex 50K EOD", H2))
s.append(Paragraph("Rules: +$3,000 target (pass at $53,000), $2,000 end-of-day trailing drawdown, $1,000 daily loss limit (Apex "
                   "closes everything and locks the day), flat by 15:59 CT. Backtest: about 50% pass per try, median 6 trading days. "
                   "Start new evaluations 5-10 trading days apart; each account gets its own chart set (no copier yet).", B))
s.append(Spacer(1, 4))
s.append(tbl([
    ["Strategy", "Code (repo file)", "Chart", "Inputs (evaluation)", "When it trades"],
    ["Vault Break", "apex_strategies/NQ_Vault_Break_SP.txt (or the pre-NR7 version)",
     "30-min MNQ, CME 24h, Exchange time, Bar Magnifier 1 min",
     "NumContracts <b>8</b>, FlaggedContracts <b>-1</b>, NR7Contracts <b>-1</b> (if present); others default "
     "(NoiseMult 0.30, TargetPts 40, StopPts 75, FirstDecision 1000, Flatten 1430)",
     "Long breakouts above the noise level and VWAP, decisions from 10:00, flat 14:30 (half-days 11:30)"],
    ["Overnight Bias ADX30", "apex_strategies/NQ_Overnight_Bias_ADX30.txt",
     "15-min MNQ, CME 24h, Exchange time, Bar Magnifier 1 min",
     "RiskPerTrade <b>1100</b>, NumContracts 1, ADXMin <b>30</b>, StopAtrPct <b>0.25</b>, RewardRisk 3, ExitTime 1430, "
     "EarlyExitTime 1130, EntryBufTicks 2",
     "Opening-range break 8:45-14:00 in the overnight-bias direction, long or short; out by 14:30"],
    ["Expiration Open Short (EOS)", "funded_strategies/NQ_Expiration_Open_Short.txt",
     "5-min MNQ, CME 24h, Exchange time, Bar Magnifier 1 min (30+ days loaded)",
     "RiskPerTrade <b>500</b>, EntryBarTime 830, ExitTime 1000, StopAtrPct 0.30, ClosedFriday1-4 as in the file",
     "Third Friday of the month only: short at the 8:30 open, out by 10:00 (next: Fri 11/20)"],
    ["Bridge Monday Long", "The Bridge: L644NQ_MondayLong_NQ v2.1 (not in repo)",
     "5-min MNQ, full Globex 24h, Exchange time",
     "NumContracts <b>2</b>, TargetPts 100, StopPts <b>0</b> (no stop), others default",
     "Sunday 19:00 -> Monday 15:55 when its daily ADX(7) 10-50 and DI+ > DI- filter allows (~25 Sundays a year)"],
], [1.25, 1.9, 1.6, 2.9, 2.35]))
s.append(Spacer(1, 6))
s.append(Paragraph("<b>On every evaluation chart, next to the strategy:</b> "
                   "<b>Apex Target Guard</b> (apex_strategies/Apex_Target_Guard.txt): TargetBalance 53050, StartBalance = that "
                   "account's Apex balance (update every evening). "
                   "<b>Apex Trade Logger</b> (apex_strategies/Apex_Trade_Logger.txt): Folder C:\\TradingLogs\\, Tag \"VB\" / \"ONB\" / "
                   "\"EOS\" / \"MON_BR\" (account #2: \"VB-2\" ...).", B))

# ---------------- Funded ----------------
s.append(PageBreak())
s.append(Paragraph("2. Funded plan - Apex 50K EOD Performance Account (after an account passes)", H2))
s.append(Paragraph("Goal: all 6 payouts ($13,000). Bootstrapped bench: 2-year expected payouts about $12,000, blown about 7%, "
                   "median 278 days to the 6th payout. Remove the Target Guard on funded charts. Sizes below are FULL size "
                   "(cushion $1,500 or more); see the cushion table.", B))
s.append(Spacer(1, 4))
s.append(tbl([
    ["Strategy", "Code (repo file)", "Chart", "Inputs (funded, full size)", "When it trades"],
    ["Vault Break SP", "apex_strategies/NQ_Vault_Break_SP.txt", "30-min MNQ, CME 24h, Exchange time, Bar Magnifier 1 min",
     "NumContracts <b>2</b>, FlaggedContracts <b>1</b> (single-print filter on), NR7Contracts -1", "As in the evaluation"],
    ["Overnight Bias ML v2", "funded_strategies/NQ_Overnight_Bias_ML.txt (current file: has 'ON Bias LSG')",
     "15-min MNQ, CME 24h, Exchange time, Bar Magnifier 1 min, 90+ trading days loaded",
     "RiskPerTrade <b>400</b>, ADXMin 20, StopAtrPct 0.30, UseMLFilter true, LongMinScore 0.03, ShortMinScore 0",
     "Overnight Bias on days the frozen ML score allows (~40% of days)"],
    ["Monday Long", "funded_strategies/NQ_Monday_Long.txt", "5-min MNQ, CME 24h, Exchange time, Bar Magnifier 1 min",
     "NumContracts <b>1</b>, RiskPerTrade 0, StopAtrPct 0.50, ExitTime 1500", "Mondays: buy the 8:30 open, out 15:00"],
    ["Expiration Open Short", "funded_strategies/NQ_Expiration_Open_Short.txt", "5-min MNQ (as evaluation)",
     "RiskPerTrade <b>700</b>", "Third Fridays, 8:30 -> 10:00"],
    ["Late-Day Flow", "funded_strategies/NQ_Late_Day_Flow.txt", "5-min MNQ, CME 24h, Exchange time, Bar Magnifier 1 min",
     "NumContracts <b>2</b>, RiskPerTrade 0, MinMoveAtr 0.40, StopAtrPct 0.25, SignalTime 1400, ExitTime 1430",
     "Follow a >= 0.4 ATR move 8:30->14:00, from 14:00 to 14:30"],
    ["NFP Fade", "funded_strategies/NQ_NFP_Fade.txt", "5-min MNQ, CME 24h (needs the 7:30 bar), 30+ days loaded",
     "RiskPerTrade <b>500</b>, SpikeMult 3.0, StopAtrPct 0.50, ExitTime 900", "Payroll Fridays: fade 7:30-7:45 reaction, 7:46-9:00"],
    ["Bridge Monday Long", "The Bridge L644NQ_MondayLong_NQ v2.1", "5-min MNQ, full Globex, Exchange time",
     "NumContracts <b>1</b>, TargetPts 100, StopPts 0", "Sunday 19:00 -> Monday 15:55 (filtered)"],
    ["CL Sunday Gap Fade", "funded_strategies/CL_Sunday_Gap_Fade.txt",
     "5-min <b>MCL</b>, <b>Eastern</b> exchange time (ExitTime 1000 = 9:00 CT)",
     "NumContracts <b>2</b>, GapAtrPct 0.10, StopAtrPct 0.75, ExitTime 1000",
     "Sunday 17:05 CT short on a >= 0.1 ATR up-gap, out Monday 9:00 CT (~11 a year). Check Apex allows MCL first."],
    ["ES MOC Follow", "funded_strategies/ES_MOC_Follow.txt", "5-min <b>MES</b>, CME 24h, Exchange time, Bar Magnifier 1 min",
     "NumContracts <b>2</b>, RiskPerTrade 0, MinMoveAtr 0.30, StopAtrPct 0.25, DecisionTime 1450, ExitTime 1500",
     "Follow a >= 0.3 ATR 14:00->14:50 move, 14:51->15:00"],
], [1.2, 1.85, 1.75, 2.85, 2.35]))
s.append(Spacer(1, 6))
s.append(Paragraph("<b>Cushion sizing (funded):</b> each morning cushion = Apex balance - trailing threshold; f = cushion / $1,500, "
                   "kept between 0.5 and 1; multiply each full-size input by f and round DOWN. The Bridge Monday Long uses "
                   "Sunday's cushion (Friday's close).", B))
s.append(Spacer(1, 4))
s.append(tbl([
    ["Cushion", "f", "VB (Num / Flagged)", "ONB ML risk", "Monday", "EOS risk", "LDF", "NFP risk", "Bridge", "CL fade (MCL)", "ES MOC (MES)"],
    ["$1,500 or more", "1.0", "2 / 1", "$400", "1", "$700", "2", "$500", "1", "2", "2"],
    ["$1,125", "0.75", "1 / 0", "$300", "0 (off)", "$525", "1", "$375", "0 (off)", "1", "1"],
    ["$750 or less", "0.5", "1 / 0", "$200", "0 (off)", "$350", "1", "$250", "0 (off)", "1", "1"],
], [1.05, 0.4, 1.05, 0.8, 0.65, 0.75, 0.5, 0.75, 0.65, 0.95, 0.95]))

# ---------------- Common setup ----------------
s.append(PageBreak())
s.append(Paragraph("3. Setup on every live chart", H2))
s.append(tbl([
    ["Item", "Setting"],
    ["Auto Trading", "Format Signals > Properties > Auto Trading: Broker plug-in Rithmic; ACCOUNT via the gear icon next to Rithmic "
     "(each chart set on its own account); mode AA; initial position Flat; 'Stop auto-trading after N rejected orders' = 10; "
     "intra-bar order generation off."],
    ["Chart Trading (new charts)", "Click the small side-arrow on the chart's right edge to open / activate Chart Trading, then set its broker drop-down (green dot) to Rithmic and pick the Apex account. If skipped, the chart sits on SIM 001 and doesn't work."],
    ["Symbol mapping", "File > Broker Profiles > Symbol Mapping (Rithmic): @MNQ -> MNQZ6 (and @MES -> MESZ6, MCL monthly when live). "
     "Roll ~Thu 12/10: MNQZ6 -> MNQH7."],
    ["Trade logger", "Apex Trade Logger on every live chart, Tag per strategy (VB, ONB, EOS, MON_BR; funded: ONB_ML, MON, LDF, NFP, "
     "MOC_MES, CLS; account suffix -2, -3 ...). Writes C:\\TradingLogs\\YYYYMMDD.csv; Task Scheduler 'PushTradeLogs' pushes it "
     "16:10 CT; Claude fills the journal at 16:40 CT."],
    ["Stop guards", "Built into VB, ONB, EOS, Monday, LDF, NFP, CL fade (orders named 'SG'). Bridge: StopPts 0, nothing to guard."],
    ["One login", "Only the VPS is logged in to Rithmic with the live login. Never test a second machine during market hours."],
], [1.4, 8.6]))
s.append(Paragraph("4. Daily routine", H2))
s.append(tbl([
    ["When", "What"],
    ["Before 8:30 CT", "All AT buttons green; Rithmic connected; no red errors left from yesterday (Logs tab); Strategy Positions flat."],
    ["After any Apex lock / disconnect / manual action", "With the account flat: auto-trading off and on (initial position Flat) on the "
     "affected charts; check Strategy Positions before the next open."],
    ["Evening", "Target Guard StartBalance = each evaluation account's balance; give Cowork the Apex balances for the journal."],
    ["Friday before 16:47 CT", "Export the weekly MultiCharts reports into live/ and sync; Claude's weekly review runs at 16:47."],
    ["Sunday before 19:00 CT", "Bridge Monday charts on (green); CL fade Sunday 17:05 when funded."],
], [2.2, 7.8]))
s.append(Spacer(1, 6))
s.append(Paragraph("Sources: NEW_CHAT_BRIEF.md, funded_strategies/FUNDED_PLAN.md, the strategy files' headers, "
                   "MULTICHARTS_PITFALLS.md. Rebuild: python3 reports/build_strategy_settings.py.", NOTE))

SimpleDocTemplate(OUT, pagesize=landscape(letter), leftMargin=0.5 * inch, rightMargin=0.5 * inch, topMargin=0.5 * inch,
                  bottomMargin=0.6 * inch, title="Strategy Settings", author="Claude").build(s, onFirstPage=foot, onLaterPages=foot)
print("wrote", OUT)
