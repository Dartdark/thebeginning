# Sniper execution review inputs

The user's pasted SniperAlgo corresponds to the public vn.py implementation.
`public_upstream/` contains public MIT-licensed source snapshots, not private
account data or trading history. License is retained beside those files.

Repository: https://github.com/vnpy/vnpy_algotrading
Pinned source commit: `bee959dc464749f7cce66e766249ccdbb2d4869a`.
See `source_manifest.json` for upstream paths and Git blob identifiers. The
mechanics-run summary retains SHA256 hashes of the exact archived bytes used.
Text archiving may append a terminal newline; upstream blob identifiers identify
the fetched source rather than asserting byte equality after text archiving.

The harness compiles unchanged class bodies and selected engine method bodies
from these files after removing imports. Enum/data/transport dependencies are
explicitly substituted in memory. This is not installation or full integration
testing of vn.py, an exchange simulator, or any connection to a broker.

Reproduce from the repository root:

`/workspace/venvs/thebeginning/bin/python -B analysis/codex_sniper_mechanics_review.py --output analysis/outputs/codex_sniper_mechanics_reproduction`

Use another new allowed output directory for a later implementation check; the
script refuses to overwrite evidence. No market data or credentials are used.
