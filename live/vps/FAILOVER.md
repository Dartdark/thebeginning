# Failover: when the VPS or MultiCharts is down with positions open (2026-11-01)

The VPS is a single point of failure: if it dies mid-trade, open positions sit there with no stop management and no time
exit (the broker still holds the protective stops that were already sent). Goal: every account flat, or safely stopped,
within minutes, from your phone if needed.

## Fill these in once (then this page works under stress)
| Item | Value |
|---|---|
| VPS provider + dashboard URL (restart / console) | QuantVPS: ____________ |
| VPS provider support (chat / phone) | ____________ |
| Apex support (help desk / Discord), and whether they can flatten an account for you | ____________ |
| A second way to reach Rithmic: R Trader Pro on your own PC (same login), or a Rithmic mobile app if your plan has one | ____________ (tested? Y/N) |
| Rithmic / Apex login for each account (store in a password manager, not here) | password manager entry: ________ |

## If you can't reach the VPS (no remote desktop, alerts stopped)
1. **Positions first.** Log in to Rithmic from your own PC (R Trader Pro, same credentials) and check each account: flatten
   what's open, cancel working orders. If that isn't possible, contact Apex support and ask them to flatten the account.
2. **Then the VPS.** Restart it from the provider's dashboard. If it doesn't come back in ~15 min, open a support ticket.
3. **When it's back:** follow the Sunday routine in `VPS_MAINTENANCE.md` section 4 (MultiCharts only, connections green,
   positions flat, auto-trading on with initial position Flat), and tell Claude so the logs are checked.

## If MultiCharts crashes but the VPS is fine
1. Order and Position Tracker / the broker platform: check positions; flatten anything a strategy can no longer manage.
2. Restart MultiCharts; turn auto-trading on per chart with initial position **Flat** (never 'from broker' unless a
   strategy is meant to resume a position).

## Test once (a quiet weekend)
- Log in to R Trader Pro from your own PC with one account's credentials: you can see the account. Note it above.
- Find the VPS restart button in the provider dashboard. Note the URL above.
- Ask Apex support how a trader flattens an account if their platform is down, and write the answer above.
