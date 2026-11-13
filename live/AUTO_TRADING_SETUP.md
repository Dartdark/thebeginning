# Auto-trading setup and account safety (MultiCharts + Rithmic + Apex)

Written 2026-10-26 after the account-#3 mix-up: #3's charts were copies of #2's, so the strategies still sent orders to
APEX-681524-02. #3 never traded, #2 held 28 MNQ instead of 8, and the clean-up opened an accidental 20-lot short on #3.
Follow this sheet every time a chart set is created, copied, changed, or switched back on. Times are Central (CT).

---

## 0. The one rule behind everything

**Each strategy sends its orders to the account in its own Auto Trading settings (the gear), NOT to the account shown in
the chart-trading panel.** The chart-trading panel (Buy Mkt / Sell Mkt, the account drop-down at the top right) only
controls manual clicks. A copied chart keeps the gear account of the chart it was copied from.

---

## 1. Account register (keep this table current)

| # | Account | Type | Status | Chart set | Logger tag suffix | Target Guard |
|---|---|---|---|---|---|---|
| 1 | APEX-681524-01 | 50K evaluation | **Failed 2026-10-26** | remove its charts or switch AA off | (none) | — |
| 2 | APEX-681524-02 | 50K evaluation | live | VB, ONB ADX30, EOS, Bridge | `-2` (e.g. `VB-2`) | TargetBalance 53050 |
| 3 | APEX-681524-03 | 150K evaluation (No-Activation) | live from 2026-10-26 | VB, ONB ADX30, EOS, Bridge | `-3` (e.g. `VB-3`) | TargetBalance 159050 |

Sizes per account type (the combine set):

| Strategy | Chart | 50K evaluation | 150K evaluation (x 2.5) |
|---|---|---|---|
| ~~Vault Break~~ (removed from 150K evaluations 2026-11-11) | 30-min | `NumContracts` 8 | none |
| ONB ADX30 | 15-min | risk $1,100 | risk $2,750 |
| Expiration Open Short | 5-min | risk $500 | risk $1,250 |
| Bridge Monday Long | 5-min | 2 | 5 |

---

## 2. New account: build its chart set (outside market hours: after 16:00 CT, or the weekend)

1. **Rithmic:** the new account appears in the Order and Position Tracker > Accounts tab (balance shown). If it does not,
   reconnect the Rithmic broker profile before going further.
2. **Create or copy the four charts** (VB 30-min, ONB 15-min, EOS 5-min, Bridge 5-min; `@MNQ`, Exchange time zone, 24-hour
   session, Bar Magnifier as the strategy file says). Copying is fine **only if step 3 is done on every chart**.
3. **On EVERY chart, for EVERY signal on it:** right-click > Format Signals > select the strategy > Properties >
   **Auto Trading** tab:
   - Broker: **Rithmic**; click the **gear** next to it; **Account = the new account** (e.g. `APEX-681524-03`).
     If the drop-down is empty, type it exactly (no spaces) and press Enter; reopen the gear to confirm it stuck.
   - Mode **AA** (automated, asynchronous). **Initial position: Flat.** **No automatic position synchronisation.**
   - Intra-bar order generation **off** (unless the strategy file says otherwise).
   - 'Stop auto-trading after N rejected orders' = **10**.
4. **Inputs (Format Signals > Inputs):** sizes from the table in section 1. **Helper (since 2026-11-09): ONE signal per chart,
   `Apex Chart Guard`** (`apex_strategies/Apex_Chart_Guard.txt`; replaces Trade Logger, Chart Monitor, Target Guard and Stop
   Guard): `Tag` = strategy name + the account suffix, `AccountName` = the account typed exactly, everything else default
   (2026-11-09: AUTO from the account in the chart's Auto Trading gear: evaluation or funded, 50K or 150K, from the account
   name and balance; target guard, finish mode and cushion guard switch themselves on for the right account type). The only
   per-chart inputs left: the strategy's size inputs, its HeartbeatTag and the guard's `Tag`.
5. **Symbol Mapping:** `@MNQ -> MNQZ6` (rolls to MNQH7 on 12/10; see TODO).
6. **Rename each chart window** with the account number (e.g. "#3 VB 30m"), so the four sets can't be confused on screen.
7. Fill in section 1's register.

## 3. Switching auto-trading ON (each chart)

Only when **all** of these are true:
- [ ] The account is **flat** in Open Positions, and the Orders tab shows **no working orders** for that account.
- [ ] It is **outside the strategy's trade window**:
      VB 10:00-14:30 · EOS opening window on expiration days · Bridge Sunday 19:00 to Monday close · ONB evening entry to its exit.
- [ ] The gear account on this chart is the right account (open it and look; don't trust the panel at the top right).
- [ ] Sizes are the right ones for this account type (section 1).

Then click **AA** (it turns green). If MultiCharts asks about the current position: choose **Flat / no position**.

## 4. Check the first orders (every new or changed chart set)

1. Orders tab: **widen the Account column** until the full number shows (…-02 / …-03).
2. The first entry from each chart must show **its own account** and the planned **quantity** (8 vs 20 etc.).
3. Open Positions: each account's quantity equals what its own strategies hold (Strategy Positions tab: strategy
   position = broker position). Two accounts that run the same plan should show the same trades at their own sizes.
4. Accounts tab: each account's Last Update moves when its strategies trade. An account whose Last Update stays at the
   previous session while its charts are on = its orders are going somewhere else.

## 5. Daily check (2 minutes, before 10:00 CT)

- [ ] Accounts tab: every live account connected, Last Update current; balances as expected.
- [ ] Open Positions: only positions the plan explains (e.g. Bridge long on Monday morning, ONB overnight).
- [ ] Each chart's AA green, with its strategy and one Apex Chart Guard on it (nothing to type daily).
- [ ] A failed or paused account: AA **off** on all of its charts.

---

## 6. If something is wrong (wrong account, wrong size, unexpected position)

**Do, in this order:**
1. **AA off** on the chart(s) that sent the wrong orders. If MultiCharts asks to close the strategy's position, answer
   **No** unless the strategy's position is exactly the one you want closed on that account.
2. **Orders tab: cancel every working order** of those charts on the affected account(s) (stops and targets too).
   Leftover exit orders become new positions later.
3. **Open Positions:** bring each account back to its plan size with a manual market order **on that account**
   (chart-trading panel set to that account). Re-check Open Positions until it matches.
4. Fix the cause (gear account / sizes), then re-enable per section 3.

**Never:**
- Use **"Close Position" on a strategy chart** to fix an account: it closes what the *strategy* thinks it holds, and on an
  account that is already flat it opens a position (that made #3's 20-lot short).
- Turn AA on while you hold a **manual position** in the same account and symbol: the strategy doesn't know about it.

## 7. Placing a manual trade (only to replace a missed signal; prefer skipping it)

1. Chart-trading panel: **account = the right one** (top right drop-down).
2. Entry: Market, quantity = plan size, side as the strategy. **Bracket icon OFF** (gray), or it attaches its own exits.
3. Stop: **Stop** tab, **Sell** side for a long, quantity = position, price = the strategy's stop (VB: entry - 75 pts).
   Check the big button reads **"Sell <qty> at <price> Stop"** before clicking.
4. Target: **Limit** tab, **Sell** side, price = the strategy's target (VB: entry + 40 pts); button must read
   **"Sell <qty> at <price> Limit"**. A blue button saying **"Buy …" ADDS to the position: don't click it.**
5. The stop and target are **not linked**: the moment one fills, cancel the other.
6. Close at market at the strategy's time exit (VB 14:30) if neither filled; cancel both.
7. Keep that strategy's AA **off** until the manual trade is closed; then re-enable per section 3.
8. Note it in the journal (it is not a backtest trade).
