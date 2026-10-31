# MultiCharts account API provenance

Retrieved: 2026-10-23, approximately 22:54 UTC, through the web search/open connector.
Purpose: routine vendor-documentation check for the independent weekly review; no account connection, live changes or return calculations.

## GetAccount: indexed account-list lookup

Primary vendor source: MultiCharts China, "图表部位、策略部位、经纪商部位":
https://www.multicharts.cn/post?idno=106

Direct short quotes from the fetched page:

> GetAccount | 返回交易追踪器账户列表中指定位置的账户名

> 排在最上面的资金账号的位置是1

English paraphrase: GetAccount returns the account name at a specified position in the Trade Tracker account list; the top account occupies position 1. The explanatory example uses GetAccount(7) to obtain the seventh listed account. These are account-list positions, rather than the account selected for a particular chart.

Retrieval reference: turn610438view2, source lines 28 and 48. Line 49 also states that balance-query account strings must match the tracker account name, including any suffix shown there.

Additional primary reference: https://www.multicharts.cn/powerlanguage/03_words/AccountsPositions/GetAccount.htm (turn361409view0, lines 2–7). This retrieval had garbled Chinese encoding; the clear article above is the quoted evidence. The English GetAccount wiki request returned HTTP 520, so it is not used as affirmative evidence.

## GetAccountID: chart auto-trading account

Primary vendor source: MultiCharts English help:
https://www.multicharts.com/trading-software/index.php?title=GetAccountID

Direct short quote:

> Returns the account number which is used for auto trading on the chart, where the strategy is applied.

Retrieval reference: turn610438view1, lines 84–88; help-page last-edited date shown as 2025-05-16.

This establishes the distinction between indexed account discovery and the chart strategy's account. It does not establish that GetAccountID can be substituted directly into this indicator: compilation, auto-trading availability and exact account-name formatting still require an isolated platform check.

## Repository observation

Reviewed repository pin: 52a6543589941455b775d46dfc23dcfbf16ec188.
Source: tools/checks/Apex_Account_Check.txt, blob e3b06a788bec1f8f29af23f65ac28e24299d3198.
Line 5 says an empty AccountName uses the chart account; line 12 actually assigns GetAccount(1). This is a confirmed account-selection mismatch in a no-order diagnostic proposed as step 1 of future cushion automation. It is not evidence that automated cushion sizing is deployed or that current orders used a wrong account balance.
