# Pinned Jesse sizing reference

Source: https://raw.githubusercontent.com/jesse-ai/jesse/9a3ebe075d9d0af5f012f921f46c2286f234af68/jesse/utils.py

Commit: `9a3ebe075d9d0af5f012f921f46c2286f234af68`. Retrieved for the uploaded RSI/Bollinger no-return audit.
Only three sizing functions are extracted by AST; the full module is not imported.
Original strategy and framework versions used by the user remain unknown.

The indicator wrapper files rsi.py, bollinger_bands.py, supertrend.py, atr.py and adx.py were retrieved unchanged
from the same pinned commit's jesse/indicators/ directory for the frozen futures screen. Only Rust kernels are
imported by the adapter; these reference files and the full framework are not executed. MIT LICENSE applies.
