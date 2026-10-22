# Uploaded gold strategy and frozen SDK references

`uploaded.py` preserves the user's uploaded file bytes, including CRLF line endings and its development prompt.
The prompt and comments are source context, not authorization to optimize 200 variants or change trading settings.

The other Python files are unchanged public reference files from Jesse commit
`9a3ebe075d9d0af5f012f921f46c2286f234af68`:

- https://github.com/jesse-ai/jesse/blob/9a3ebe075d9d0af5f012f921f46c2286f234af68/jesse/services/candle_service.py
- https://github.com/jesse-ai/jesse/blob/9a3ebe075d9d0af5f012f921f46c2286f234af68/jesse/helpers.py
- https://github.com/jesse-ai/jesse/blob/9a3ebe075d9d0af5f012f921f46c2286f234af68/jesse/services/trading_hours.py
- https://github.com/jesse-ai/jesse/blob/9a3ebe075d9d0af5f012f921f46c2286f234af68/jesse/services/cache.py

The research adapter imports only the standalone trading-hours service, executes the supplied class AST, and uses
`jesse-rust==1.3.1` indicator kernels. The reference candle service, helper module and cache module are not imported
and do not create a Jesse project, cache, database or connection. Their relevant timing/window semantics are
implemented and checked explicitly. This is not a claim of full-engine or original-author-version parity.

Jesse's MIT licence is preserved in `LICENSE`. Runtime dependency versions and code/input hashes are saved in
`analysis/outputs/codex_xau_st_break_free/reproduction.json`; owned GC data hashes are in `manifest.json`.
