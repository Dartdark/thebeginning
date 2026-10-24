# GC_COMBO v2 in MultiCharts: step by step (for the parity check, 2026-10-24)

Do it outside market hours and NOT on the live VPS (a backtest workspace on your own PC).
Files (in your clone after `git pull`): `checks/candidates/gc_combo/GC_COMBO_v2_community.txt` and `checks/candidates/gc_combo/GCCOMBO.txt`.

## 1. Compile the strategy
1. Open the **PowerLanguage Editor** (Start menu, or the MultiCharts toolbar button "PL Editor").
2. **File → New → Signal** (not Indicator). Name: `GC_COMBO_v2_community`. OK.
3. Select all the template text (Ctrl+A), delete it, paste the whole `GC_COMBO_v2_community.txt` (Ctrl+V).
4. Press **F3**. The Output pane at the bottom must say **compiled successfully**. If it shows an error, send a screenshot.

## 2. Put the data file in its own folder
1. In File Explorer make a new folder, e.g. `C:\MCData\GCCOMBO\`.
2. Copy `GCCOMBO.txt` into it. Nothing else in that folder; keep the name exactly `GCCOMBO.txt` (it becomes the symbol name).

## 3. Map it in QuoteManager
1. Open **QuoteManager** (Start menu → MultiCharts → QuoteManager).
2. **File → Map ASCII…**. Click **Browse**, pick `C:\MCData\GCCOMBO\`. The file shows as a blue link `GCCOMBO`.
3. Click the blue link. In the settings dialog:
   - Fields, in this order: **Date, Time, Open, High, Low, Close, Volume**; delimiter **comma**.
   - **Start at row 2** (row 1 is the header).
   - Date format **MM/DD/YYYY**, time **HH:MM:SS** (the file looks like `10/03/2016,05:00:00,…`).
   - Resolution: choose **Minute** and type **1** in the small box (not Day, not Tick).
   - Exchange **CME**, time zone **Exchange**; leave "bar-close" / time conversion options unchecked.
4. OK, then OK. It should say **mapped 1 file successfully**. GCCOMBO now appears in QuoteManager's symbol list.

## 4. Build the chart (order matters: Data1, then Data2, then Data3)
1. In MultiCharts: **File → New → Chart Window**.
   - Data source: your normal feed (Rithmic). Symbol **@GC** (continuous gold). Resolution **1 Minute**.
   - **Settings** tab: session = the full CME Globex / 24-hour session (the same kind you use for NQ, 17:00-16:00 CT);
     time zone **Exchange**; **Build Volume On: Trade Volume** (vote B needs up / down volume; tick count breaks it).
   - Data range: **From 01/01/2017** to today (the ATR and crude votes need ~20 sessions to warm up). OK. = **Data1**.
2. **Insert → Instrument…** → same feed, symbol **@CL**, **1 Minute**, same session type and time zone, from 01/01/2017. = **Data2**.
3. **Insert → Instrument…** → data source **ASCII Mapping** → symbol **GCCOMBO**, **1 Minute**, from 01/01/2017. = **Data3**.
   Then right-click the GCCOMBO pane → **Format Instrument → Settings → Session: 24/5** (or any 24-hour session).
   It must show one tiny bar a day at 05:00. If it says "No data": resolution must be 1 Minute (on the chart and in Map ASCII),
   the session must be 24/5 (a 09:30-16:00 session hides the 05:00 bar), then click the chart and press Ctrl+R.
4. Check the order: Format → Instruments (or the status line) must list @GC as Data1, @CL as Data2, GCCOMBO as Data3.
   If CL or GCCOMBO ended up first, delete the chart and redo it.

## 5. Insert the strategy and set it
1. **Insert → Strategy… → GC_COMBO_v2_community** → OK.
2. **Format → Strategies → Format…** → **Inputs** tab: leave every input at its default; **ETminusChart = 1** (your chart is
   on Exchange time = Chicago; New York = Chicago + 1 hour).
3. **Properties** tab: commission **$2.30 per contract per side**, slippage **1 tick per side** (the author's settings, so the
   check in step 6 matches); Initial capital anything (e.g. $50,000).
4. **Backtesting** tab: **Intra-bar order generation OFF**; **Bar Magnifier OFF**; limit-order fill: "fill when the price
   **exceeds the limit by 1** point" (MultiCharts' "point" = 1 tick), not Classic.
5. OK. The chart recalculates (can take a few minutes on 9 years of 1-min data ×3).

## 6. Check it matches the author
Open the report: **View → Strategy Performance Report** (or Alt+Shift+P). For **2017-09-18 → 2026-08-07** the note says about
**1,204 trades, ~$226k net, 52.5% wins**. A few percent off = your data vendor; far off (e.g. 300 trades, or 0 short / 0 long)
= a step above is wrong (most often: Data order, Build Volume, GCCOMBO "no data", or ETminusChart).
Quick sanity checks: Data1 bars at 09:00 CT = 10:00 ET; trades labelled BL_L / BL_S enter at 09:01 CT and exit at the 12:30 CT
bar; ST_S trades are shorts.

## 7. Export and send
1. In the report window: **File → Save As…** (or the Export button) → **Excel (.xlsx)**, name it
   `Backtesting Strategy Performance Report _ @GC - 1 Minute GC COMBO v2.xlsx`.
2. Put it in `mc_reports/` in your clone, then `git pull`, `git add`, `git commit`, `git push` (or just upload it in the chat).
Claude then: matches it trade by trade with the rebuild (all but vote B should agree), replaces the proxy vote B with the
MultiCharts trades, and reruns the funded and evaluation benches at MGC.

## Afterwards
Save the workspace (File → Save Workspace). For live use it would run on @MGC (gold above $4,000 makes 1 GC too big), with
GCCOMBO.txt updated from the author (the file ends 2026-09-25; after that votes C and E read 0).
