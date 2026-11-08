# Sentinel MNQ: clock-field correction, no economic definition change

Original preregistration: `5e066bb56aa587f33c11248eb6bad59e696b1ac4`.
First design screen failed: net−$3,013.62,1238trades; dependent stages remain prohibited.

During maker audit, `exit_at` for protective stops was found to label the containing minute's opening boundary,
although OHLC establishes only an intraminute interval. Correct this serialization before closing the task:
intraminute stop `exit_at` is missing, explicit interval start/end retained; stop gaps at known opens get their
own reason. Scheduled close and indicator next-open timestamps remain exact within the assumed bar model.
This changes no decision, price, side, sizing, cost, trade universe or gate. The original outputs are retained in
`analysis/outputs/codex_sentinel_mnq_20261108/attempt1/`. Rerun the same implementation once and assert identical
financial columns and summary. Count as implementation rerun, **not** an additional economic trial or rescue.
This amendment does not permit any further return definition or downstream stage.
