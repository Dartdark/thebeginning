# Tasks for Antigravity (blind checks of the current strategies)

Each task is a written rule only; Antigravity rebuilds it in Jesse, runs it, and returns the trade list. Claude then
compares those trades with MultiCharts and its own Jesse runs (`analysis/jesse/compare.py`).

| # | Task | Market / bars | Note |
|---|---|---|---|
| 01 | `TASK_01_CL_SUNDAY_FADE.md` | CL, 5 min, Eastern | self-contained (own data section) |
| 02 | `TASK_02_VAULT_BREAK.md` | NQ, 30 min | needs COMMON_NQ.md |
| 03 | `TASK_03_OVERNIGHT_BIAS_ADX30.md` | NQ, 15 min | needs COMMON_NQ.md |
| 04 | `TASK_04_OVERNIGHT_BIAS_ML.md` | NQ, 15 min | needs COMMON_NQ.md + Task 03 |
| 05 | `TASK_05_MONDAY_LONG.md` | NQ, 5 min | needs COMMON_NQ.md |
| 06 | `TASK_06_EXPIRATION_OPEN_SHORT.md` | NQ, 5 min | needs COMMON_NQ.md |
| 07 | `TASK_07_LATE_DAY_FLOW.md` | NQ, 5 min | needs COMMON_NQ.md |
| 08 | `TASK_08_NFP_FADE.md` | NQ, 5 min | needs COMMON_NQ.md |
| 09 | `TASK_09_ES_MOC_FOLLOW.md` | ES, 5 min | needs COMMON_NQ.md (done: PASS, 198 trades, +636.17 pts) |

## Academic Research & Strategy Foundations

- `RESEARCH_ACADEMIC_EDGE.md`: Deep literature synthesis of market microstructure forced flows (Cheng & Madhavan 2009, Admati & Pfleiderer 1988, Berkman et al. 2012, Ni et al. 2005) and quantitative trade construction using Dr. Ernest P. Chan's *Algorithmic Trading* (Wiley, 2013).

Not included: Vault Break SP (Vault Break's entries; its single-print flag only sets the size) and Bridge Monday Long
(closed source).

Suggested order: 01, then 06 (simplest NQ rule), 05, 07, 08, 02, 03, 04.

How to run each one:
- **One task per Antigravity conversation**, strongest Gemini Pro model, high effort.
- Prompt: `Read tasks/TASK_NN_....md (and the files it names) and do exactly what it says, using the Jesse MCP tools.
  Don't skip the backtest.`
- Output goes in `tasks/out_NN/`. Commit and push it to `antigravity/jesse`.
