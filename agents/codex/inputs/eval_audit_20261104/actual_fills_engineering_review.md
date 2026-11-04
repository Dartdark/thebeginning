# Actual-fill account engineering reproduction: PASS

Summary: Reproduced the same original FC2B50K risk0.50 policy on2018-04-02, its earliest saved2018design case with fills.
157/157checks passed against the saved fast outcome and an independent event cash ledger.
18source fills and2DLL market liquidations reconcile; costs total$112.00.
Outcomeexpire:cash/equity$49305.50,EODfloor$49189.10; no changed quantity, rule or2023account outcome.
This verifies conditional-tape engineering identities, not native MultiCharts matching or strategy profitability.

Exact policy`E50_2436d1f22f21ef54`was already counted and completed under original preregistration`a087708b13697df4c3dd0b0814f98cb53a2b254a`.
The retrospective case choice is only earliest2018with fills, to exercise fees and liquidation; no return/side/date
optimization follows. It uses target_guard=False, nominal50Kstart, unchanged$1,000source-risk requests, integer
micros, RT$1.24fees and one adverse tick per market/stop fill. No corrected DT overlay is used.

Source commission$55.80,source slippage$45.00,DLL liquidation costs$11.20
reconcile with the saved total. Every accepted source fill is checked against its raw event/reference price,
side, native point value, source-known stop and integer request. The independent cash ledger reproduces
each logged account equity, final realized cash and the highest-EOD floor. DLL entries are checked against
the current session's realized/unrealized loss threshold, their first crossing on the same raw shared-price
tape and prevailing-market closing costs. Account-death timing matches the saved case; later source trades
do not accrue to that account. The raw minimum is compared with the fast visited minimum/conservative bound.

Reproduce with`actual_fills_engineering_check.py`; full checks, timestamps and ledger are in
`actual_fills_engineering_review.json`. Raw/fast parity and independent arithmetic on one fixed modeled path
are not independent market evidence. Real quote chronology, source/settings acceptance and native matching
remain conditional; the core's author performed this reproduction. Claude/economic verification stays pending.
