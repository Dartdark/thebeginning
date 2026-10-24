# T_ONESIDE, night-volume switch, NQ (candidate, 2026-10-24)

Source: the user's PowerLanguage file `T_ONESIDE.txt` in this folder (the BASE strategy; you may read it) and
`T_ONESIDE_v2.txt` (= the same file plus the research note's stop; you may read it). The research note
`T_ONESIDE_research_note.pdf` gives the stop rule. Instrument: NQ, 1-minute bars stamped with their CLOSE time, Central
time; data = `data/NQ_1min_20*.csv` (08:00-15:15 CT) + `data/NQ_1min_ON_20*.csv` (15:16-07:59 CT) joined (24-hour; the
`scratch_data/g24.pkl` Grid24 is the same data). Volume = the files' `volume` column (total volume). Trades 2018-01-02
onward (Dec 2017 = warm-up). One contract (per NQ, $20 a point). At most one trade a day; the two legs never on the same day.

## Night
- A 'day' bar is one stamped 08:30-16:59 CT; every other bar is a night bar. The night of trading day D = the night bars
  after the last day bar before D's 08:29 bar, up to and including D's 08:29 bar (normally the 17:00/17:01 reopen of the
  previous session -> 08:29; Sunday evening -> Monday 08:29).
- Night volume = sum of the night bars' volume; night return = close of the 08:29 bar - open of the first night bar.
  A night is valid with >= 30 night bars.
- Heavy ('fat') night: night volume > 1.4 x the median of the volumes of the previous 20 VALID nights (D's own night
  excluded; needs 20 banked nights).

## Leg T (heavy nights only)
- Night return > 0 -> short; < 0 -> long. Entry at the OPEN of the bar stamped 08:30 (i.e. 08:29:00).
- Exit at the OPEN of the bar stamped 08:45 (08:44:00).

## Leg OS (valid, NOT heavy nights; the note's 'ONESIDE long')
- Morning from the bar stamped 08:30: P0 = open of the 08:30 bar; box high / low = highest high / lowest low of the bars
  stamped 08:30-09:59; session VWAP = cumulative (typical price (H+L+C)/3 x volume) / cumulative volume from the 08:30 bar.
- At the bar stamped 09:59: if (box high - P0) > 2 x (P0 - box low) AND its close > VWAP -> long at the OPEN of the 10:00 bar.
- Exit: the first bar from the 10:00 bar on whose close < VWAP (VWAP keeps accumulating) -> out at the next bar's open;
  otherwise at the open of the 11:00 bar.

## Stop (research note; the file itself has none)
- ATRd = mean over the previous 20 FULL sessions (sessions that have a 15:00 bar) of (highest high - lowest low) of the
  bars stamped 08:31-15:00.
- Stop distance from the entry price: 0.40 x ATRd for T, 0.30 x ATRd for OS; active from the entry bar on; a stop fills at
  the stop price (no gap handling needed for these windows beyond: if a bar opens beyond, the stop price is still used in
  the maker's build; flag it if you think that is optimistic).

## Costs
$7.25 per round trip + 1 tick ($5) per fill (entry and exit are both market or stop): $17.25 a trade.

## Mechanism (the author's view)
Heavy overnight volume = inventory built in thin hours, unwound at the cash open (the open reverts); a quiet night = the
day's flow arrives in the cash session, and a one-sided morning above VWAP continues. The author pre-declared 5
falsification cells; the maker ran them: fade on quiet nights, OS on heavy nights, dose-response by volume tercile,
mirror short, entry at the bell.

## Variants tried
The rule and multiples are frozen by the author (stop chosen on 2016-20 by its author); the maker ran no parameter search,
only the 5 cells above: `variants` 5. Not pre-registered by us. `placebo.csv` = 20 runs of leg T with a random side.

## trades.csv
date, leg (T / OS), side (+1 / -1), net ($ per NQ after costs), entry, exit, kind (stop / flat).
