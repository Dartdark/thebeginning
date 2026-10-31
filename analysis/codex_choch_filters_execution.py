"""Frozen executable intraday CHoCH wrapper; no feature or selection logic.

Retains the RR2 engine's clocks, shared minute walker and missing-path rules.
The registered correction charges an immediate round trip when a submitted
market entry fills at or through its swing stop. Stop-first is a diagnostic
stress of ambiguous exit minutes, not a separately selected strategy.
"""
import numpy as np
import pandas as pd

import codex_choch_rr2 as foundation


def ledger(g, valid, events, stop_first=False):
    """Execute already-filtered events, one position at a time, at one MNQ."""
    o, h, l, c = (getattr(g, k).ravel() for k in 'ohlc')
    good = valid.ravel()
    missing = np.cumsum(foundation.repaired.expected_minutes(g) & ~good)
    rows, blocked = [], -1
    for event in events.to_dict('records'):
        signal = int(event['signal'])
        minute, day = signal % 1440, signal // 1440
        flat = foundation.intraday_window(pd.Timestamp(g.ts[day]), minute)
        if flat is None:
            continue
        start, deadline = signal + 2, day * 1440 + flat
        if start <= blocked or start >= len(o) or start >= deadline:
            continue
        side, stop = int(event['side']), float(event['stop'])
        if not good[start]:
            blocked = deadline
            rows.append(dict(**event, entry_j=start, state='missing_entry',
                             entry_gap_through=False,
                             stop_target_collision=False,
                             stop_first_applied=False))
            continue

        entry = float(o[start])
        risk = side * (entry - stop)
        gap_through = bool(risk <= 0)
        collision, stress_applied = False, False
        if gap_through:
            # The market order has filled; a stop-invalid fill cannot vanish.
            end, price, kind, target = start, entry, 0, np.nan
        else:
            target = entry + side * 2 * risk
            end, price, kind, _ = foundation.core._walk(
                o, h, l, c, start, deadline - 1, side, stop, target, 1.)
            end = int(end)
            # _walk identifies the first trigger minute. Only its exit minute
            # can change under stop-first, so the shared walker is preserved.
            if kind in (0, 1):
                hit_stop = l[end] <= stop if side > 0 else h[end] >= stop
                hit_target = (h[end] >= target + 1. if side > 0
                              else l[end] <= target - 1.)
                collision = bool(hit_stop and hit_target)
                opening_stop_gap = bool(side * (o[end] - stop) <= 0)
                if stop_first and collision and not opening_stop_gap:
                    price, kind = stop, 0
                    stress_applied = True
            if kind == 2:
                # Preserve the registered liquidation OPEN, not its later close.
                end, price = deadline, o[deadline]

        blocked = int(end)
        unknown = int(missing[end] - (missing[start - 1] if start else 0))
        state = ('unresolved_missing' if unknown or not np.isfinite(price)
                 else 'resolved')
        row = dict(**event, entry_j=start, exit_j=int(end), entry=entry,
                   exit=float(price), risk=float(risk), target=float(target),
                   kind=int(kind), state=state,
                   missing_expected_minutes=unknown,
                   entry_gap_through=gap_through,
                   stop_target_collision=collision,
                   stop_first_applied=stress_applied)
        if state == 'resolved':
            gross = float(side * (price - entry) * 2)
            row.update(gross_mnq=gross, commission_mnq=1.24,
                       slippage_mnq=1., net_mnq=gross - 2.24)
        rows.append(row)

    result = pd.DataFrame(rows)
    for column in ('state', 'side', 'gross_mnq', 'net_mnq', 'risk',
                   'entry_gap_through', 'stop_target_collision',
                   'stop_first_applied'):
        if column not in result:
            result[column] = np.nan
    for column, jcol in [('entry_time', 'entry_j'), ('exit_time', 'exit_j')]:
        if jcol in result:
            result[column] = [
                pd.NaT if not np.isfinite(j) else
                pd.Timestamp(g.ts[int(j) // 1440]) +
                pd.Timedelta(minutes=int(j) % 1440)
                for j in result[jcol]]
    return result


def checks():
    """Synthetic-only execution checks; never load a market input file."""
    from types import SimpleNamespace

    def fixture(side=1, date='2021-06-28'):
        dates = pd.DatetimeIndex([date])
        g = SimpleNamespace(D=1, dates=dates.strftime('%Y%m%d').astype(int)
                            .to_numpy(), ts=dates.to_numpy())
        good = foundation.repaired.expected_minutes(g).reshape(1, 1440)
        for key in 'oc':
            setattr(g, key, np.where(good, 100., np.nan))
        g.h, g.l = np.where(good, 101., np.nan), np.where(good, 99., np.nan)
        events = pd.DataFrame([dict(signal=540, close=100., side=side,
                                    stop=100. - side * 5, radius=2,
                                    broken_pivot=0)])
        return g, good, events

    for side in (-1, 1):
        start, deadline = 542, 958
        g, valid, events = fixture(side)
        g.o[0, deadline] = 100. + side * 3
        row = ledger(g, valid, events).iloc[0]
        assert row.state == 'resolved' and row.kind == 2
        assert row.exit_j == deadline and row.exit == g.o[0, deadline]
        assert row.target == 100. + side * 10
        assert np.isclose(row.net_mnq, 3.76)

        # Entry-bar protection and the exact one-point target-through boundary.
        near = 'h' if side > 0 else 'l'
        getattr(g, near)[0, start] = 100. + side * 10.75
        assert ledger(g, valid, events).iloc[0].kind == 2
        getattr(g, near)[0, start] = 100. + side * 11
        row = ledger(g, valid, events).iloc[0]
        assert row.kind == 1 and row.exit_j == start
        assert row.exit == 100. + side * 10

        g, valid, events = fixture(side)
        getattr(g, 'l' if side > 0 else 'h')[0, start] = 100. - side * 6
        row = ledger(g, valid, events).iloc[0]
        assert row.kind == 0 and row.exit_j == start
        assert row.exit == 100. - side * 5

        # The primary nearest-extreme walker chooses target here; stress stops.
        g, valid, events = fixture(side)
        if side > 0:
            g.h[0, start], g.l[0, start] = 111., 88.
        else:
            g.h[0, start], g.l[0, start] = 112., 89.
        primary = ledger(g, valid, events).iloc[0]
        stress = ledger(g, valid, events, stop_first=True).iloc[0]
        assert primary.kind == 1 and primary.stop_target_collision
        assert stress.kind == 0 and stress.stop_target_collision
        assert stress.stop_first_applied and stress.exit == events.stop.iloc[0]

        # A gap through the entry stop is a charged, immediate round trip.
        for gap in (5., 8.):
            g, valid, events = fixture(side)
            opening = 100. - side * gap
            g.o[0, start], g.c[0, start] = opening, opening
            g.h[0, start], g.l[0, start] = opening + 1, opening - 1
            row = ledger(g, valid, events).iloc[0]
            assert row.state == 'resolved' and row.entry_gap_through
            assert row.kind == 0 and row.exit_j == start and row.exit == opening
            assert row.gross_mnq == 0. and np.isclose(row.net_mnq, -2.24)

        # Later stop gaps keep the worse open, including in stop-first stress.
        g, valid, events = fixture(side)
        opening = 100. - side * 8
        g.o[0, start + 1] = opening
        g.h[0, start + 1], g.l[0, start + 1] = opening + 1, opening - 1
        for stressed in (False, True):
            row = ledger(g, valid, events, stop_first=stressed).iloc[0]
            assert row.kind == 0 and row.exit == opening

    g, valid, events = fixture()
    valid[0, 542] = False
    later = events.iloc[0].to_dict()
    later['signal'] = 600
    events = pd.concat([events, pd.DataFrame([later])], ignore_index=True)
    rows = ledger(g, valid, events)
    assert len(rows) == 1 and rows.iloc[0].state == 'missing_entry'

    g, valid, events = fixture()
    valid[0, 552] = False
    for key in 'ohlc':
        getattr(g, key)[0, 552] = np.nan
    row = ledger(g, valid, events).iloc[0]
    assert row.state == 'unresolved_missing' and row.missing_expected_minutes == 1
    assert pd.isna(row.get('net_mnq'))

    g, valid, events = fixture(date='2024-11-29')
    g.o[0, 690] = 103.
    row = ledger(g, valid, events).iloc[0]
    assert row.kind == 2 and row.exit_j == 690 and row.exit == 103.
    assert ledger(g, valid, events.iloc[:0]).empty
    return dict(entry_gap_charged=True, entry_bar_protection=True,
                target_through=True, collision_and_stop_first=True,
                worse_gap_preserved=True, time_exit_open=True,
                missing_entry_blocks=True, missing_path_unresolved=True,
                early_flatten=True, long_short_symmetry=True)


if __name__ == '__main__':
    print(checks())
