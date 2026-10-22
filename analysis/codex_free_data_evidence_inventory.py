"""Evidence-only counts, liquidity and planning hurdles. Never reads candidate prices/returns.

Run with the configured Python from the repository root. No strategy execution,
signal calculation, return test, cache, external request or live-file write.
"""
from pathlib import Path
import hashlib
import json
import math

import exchange_calendars as xcals
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/outputs/codex_free_data_evidence"
START, END = "2018-01-01", "2022-12-31"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def hurdle(n, sd, commission, tick_value):
    cost = commission + 2 * tick_value
    net = 2 * sd / math.sqrt(n)
    return dict(n=n, assumed_sd=sd, commission=commission, tick_value=tick_value,
                round_trip_cost=cost, net_mean_for_t2=net,
                gross_mean_for_t2=net + cost, gross_1_5_cost=1.5 * cost,
                gross_ticks_for_t2=(net + cost) / tick_value)


def gap(occupancy, first, last, weights):
    rows = occupancy[occupancy.minute.between(first, last)].copy()
    assert len(rows) == 5 * (last - first + 1)
    # A marginal probability of a flat minute, not a joint probability that
    # a whole window is flat and not the flat fraction on candidate events.
    rates = (1 - rows.groupby("weekday").any_open_fraction.mean()).to_dict()
    return dict(first_minute=first, last_minute=last, bars=last-first+1,
                flat_minute_fraction_by_weekday=rates,
                equally_weighted_weekday_flat_fraction=sum(rates.values()) / 5,
                weekday_weights=weights,
                weighted_flat_minute_fraction=sum(rates[d] * n for d, n in weights.items()) / sum(weights.values()),
                interpretation="weekday-marginal minute occupancy; not event-conditional or whole-window flat")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    calendar_path = ROOT / "data/treasury_auctions.csv"
    occupancy_path = ROOT / "analysis/outputs/codex_sge_delivery_screen/roster_minute_occupancy.csv"
    cal = pd.read_csv(calendar_path, usecols=["auction_date", "security_type", "security_term",
                                            "closing_time_comp", "reopening", "cusip",
                                            "inflation_index_security", "floating_rate"])
    occ = pd.read_csv(occupancy_path)
    cal["date"] = pd.to_datetime(cal.auction_date)
    years = pd.to_numeric(cal.security_term.str.extract(r"^(\d+)-Year")[0], errors="coerce")
    # Reopening remaining terms below the original integer maturity.
    months = pd.to_numeric(cal.security_term.str.extract(r"Year (\d+)-Month")[0], errors="coerce").fillna(0)
    cal["tenor"] = years + (months > 0).astype(int)
    auctions = cal[(cal.date.between(START, END)) & (cal.security_type == "Note")
                   & (cal.inflation_index_security == "No") & (cal.floating_rate == "No")
                   & (cal.closing_time_comp == "01:00 PM") & cal.tenor.isin([5, 7, 10])].copy()
    auctions["tenor"] = auctions.tenor.astype(int)
    assert not auctions.duplicated(["date", "tenor"]).any()
    # NYSE calendar is a descriptive cash-session proxy, NOT final ZN holiday eligibility.
    nyse = xcals.get_calendar("XNYS", start="2017-01-01", end="2023-01-05")
    sessions = nyse.sessions.tz_localize(None) if nyse.sessions.tz is not None else nyse.sessions
    auctions["following_cash_session"] = [sessions[sessions.searchsorted(d, side="right")] for d in auctions.date]
    events = auctions.sort_values("tenor").drop_duplicates("date", keep="last").copy()
    events["next_weekday"] = events.following_cash_session.dt.weekday
    auction_weights = {int(k): int(v) for k, v in events.next_weekday.value_counts().items()}
    cash_days = sessions[(sessions >= START) & (sessions <= END)]
    cash_weights = {int(k): int(v) for k, v in pd.Series(cash_days.weekday).value_counts().items()}
    auctions.to_csv(OUT / "auction_inventory.csv", index=False)
    # Liquidity census only. Explicit usecols forbids loading OHLC fields.
    volumes, coverage, hashes = [], [], {}
    for year in range(2018, 2023):
        path = ROOT / f"data/ZN_1min_{year}.csv"
        raw = pd.read_csv(path, usecols=["date", "time", "volume"])
        minute = raw.time // 100 * 60 + raw.time % 100
        w = raw[minute.between(466, 505)]
        g = w.groupby("date").agg(bars=("time", "size"), unique_bars=("time", "nunique"), contracts=("volume", "sum"))
        complete = g[(g.bars == 40) & (g.unique_bars == 40)].copy()
        complete["year"] = year
        complete["date"] = pd.to_datetime(complete.index.astype(str), format="%Y%m%d")
        complete = complete[complete.date.dt.weekday < 5]
        volumes.append(complete.reset_index(drop=True))
        coverage.append(dict(year=year, observed_window_dates=len(g), complete_weekday_windows=len(complete)))
        hashes[str(path.relative_to(ROOT))] = digest(path)
    volume = pd.concat(volumes, ignore_index=True)
    volume.to_csv(OUT / "zn_window_volume.csv", index=False)
    planned_n = max(1, len(events) // 2)  # assumption, NOT an observed dealer-share signal count
    etf_planned_n = int(len(cash_days) * 0.2)  # hypothetical top quintile, not observed fails signals
    auction_samples = []
    for date, primary, competitive, url in [
        ("2018-01-10", 4407365000, 19991883000,
         "https://www.treasurydirect.gov/instit/annceresult/press/preanre/2018/R_20180110_1.pdf"),
        ("2022-01-12", 5977970000, 35992396200,
         "https://www.treasurydirect.gov/instit/annceresult/press/preanre/2022/R_20220112_2.pdf")]:
        auction_samples.append(dict(date=date, primary_dealer_accepted=primary,
                                    total_competitive_accepted=competitive,
                                    primary_dealer_share=primary/competitive, source=url))
    # Sensitivity scenario, NOT an observed hedge or DV01 estimate.
    hypothetical_dollar_shock = 1e9
    hypothetical_modified_duration = 7
    hypothetical_zn_dv01 = 70
    full_hedge = hypothetical_dollar_shock * hypothetical_modified_duration * 0.0001 / hypothetical_zn_dv01
    median_volume = float(volume.contracts.median())
    inventory = dict(
        source_commit="e097c0f", inventory_plan_commit="41ffc93", trials=0,
        candidate_returns_computed=False, candidate_price_columns_read=False,
        caches_built=False, purchases=0,
        auction=dict(rows=len(auctions), unique_dates=len(events),
                     by_year={int(k): int(v) for k,v in auctions.groupby(auctions.date.dt.year).size().items()},
                     by_tenor={int(k): int(v) for k,v in auctions.groupby("tenor").size().items()},
                     simultaneous_multi_tenor_dates=int((auctions.groupby("date").size() > 1).sum()),
                     planning_signal_fraction=0.5, planned_n=planned_n,
                     fields_owned=list(pd.read_csv(calendar_path, nrows=0).columns),
                     dealer_award_fields_owned=False, pdf_spot_checks=auction_samples,
                     gap=gap(occ, 466, 505, auction_weights),
                     power=[hurdle(planned_n, sd, 7.25, 15.625) for sd in (150, 300)]),
        zn_liquidity=dict(coverage=coverage, complete_windows=len(volume),
                          median_window_contracts=median_volume,
                          p10_window_contracts=float(volume.contracts.quantile(.1)),
                          hypothetical_cash_inventory_shock=hypothetical_dollar_shock,
                          assumed_modified_duration=hypothetical_modified_duration,
                          assumed_zn_dv01=hypothetical_zn_dv01,
                          hypothetical_full_hedge_contracts=full_hedge,
                          hypothetical_full_hedge_over_median_volume=full_hedge/median_volume,
                          actual_hedge_fraction="unknown; zero is possible"),
        etf_ftd=dict(cash_sessions=len(cash_days), hypothetical_fraction=.2,
                     hypothetical_signal_n=etf_planned_n, known_timely_active_closeout_events=0,
                     gap=gap(occ, 481, 505, cash_weights),
                     power=[hurdle(etf_planned_n, sd, 5, 12.5) for sd in (500, 1000)]),
        limitations=["planning SDs are assumed, not observed strategy results",
                     "independence is optimistic; correlated events lower effective n",
                     "calendar has no 2017 award warmup; signal count is an upper planning assumption",
                     "free public historical allocation archive spot-checked, not fully downloaded or audited",
                     "cash-session proxy must be replaced by instrument-specific holiday rules before any test"],
        source_sha256={str(calendar_path.relative_to(ROOT)):digest(calendar_path),
                       str(occupancy_path.relative_to(ROOT)):digest(occupancy_path), **hashes})
    (OUT / "inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(json.dumps({k: v for k, v in inventory.items() if k != "source_sha256"}, indent=2))


if __name__ == "__main__":
    main()
