# Continuous-futures trend (QuantJourney example 25, user upload 2026-10-30) - saved for later, NOT tested by us

Rule (from the file): monthly (business month end) rebalance; per market sign(SMA 63 - SMA 252) of daily closes;
weight = signal / 63-day annualised volatility, scaled to unit gross. Long or short, holds weeks to months.
Universe in the file: MES, MNQ, ZN, CL, GC, ZC (Yahoo '=F' continuous series: no roll rule, no roll costs, no contract P&L).
Their result (6 May 2019 - 1 Jan 2026, $1M, unit gross): +46.3%, CAGR 5.9%, Sharpe 0.62, Sortino 0.88, max DD -9.7%,
beta 0.04, 370 trades, PF 5.85 (per their engine). SPY +158% same period.

Our first read: classic time-series momentum (Moskowitz, Ooi & Pedersen 2012); low beta, a crisis hedge for the intraday
book; but Sharpe ~0.6, multi-day (personal account only, not Apex), needs ~$150k+ to hold one contract per market.
Test when the personal account reaches ~$150k: rebuild on our data with proper rolls (NQ, ES, CL, GC, ZN; YM or 6E for
corn), then personal_portfolio.py add / weight tests. Trend profits since ~2010 are well below the long-run record.
