#!/bin/sh
# Run an analysis script with its provenance stamp as the first output line (2026-11-01, review gap #5).
#   tools/run_stamped.sh analysis/some_test.py scratch_data > analysis/outputs/some_test_output.txt
python3 analysis/provenance.py
exec python3 -u "$@"
