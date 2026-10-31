# PrimeSync v2: account-test research code

[Code](PrimeSync_v2.txt). Not compiled or trade-matched in MultiCharts.
No current plan addition/replacement is recommended by the account tests.

Same entry and full-exit rules as v1; default ExitMode0 keeps everything to4.5R,
with stop to entry at1.5R, then to original1.5R at2.5R.

New **FixedSizeContracts1** matches the account-test sizing projection: one
micro per existing eligible signal. The original three-unit/$500 risk-eligibility
screen remains in force, preserving tested signals/cooldown. FixedSizeContracts0
restores the original variable-risk screen; only that mode supports partial ExitMode1.
EnableEntries false disables new entries while managing an existing position.

Use the [original chart/setup notes](PrimeSync_SETUP.md): new Signal,15/30-minute
chart, Central Exchange time, full Globex, MaxBarsBack200, MinimumStudyBars100,
IOG on and1-minute Bar Magnifier, one-point limit trade-through. No other signal
or stop manager on this research chart. Initial protection must be checked.

Native micro volume may differ from the NQ/ES signal source. For comparison
against the Python mini-price/micro-dollar proxy on a full NQ/ES research chart,
scale the eligibility budget/reserve to5000/50, keep FixedSizeContracts1, and
normalize that full-contract report's money by10. Its synthetic fee must be
$10.40 per full contract round trip, with one adverse tick on market/stop fills.
This is a research unit conversion, not permission to trade a full contract.

In funded simulations, the one-micro allocation switches off below full cushion
because floor(1*f)=0. This file does not read Apex balances or automate cushion
sizing. It is not a deployment file. Export Settings/List of Trades and matching
minute/total-volume data for parity before any plan decision.
