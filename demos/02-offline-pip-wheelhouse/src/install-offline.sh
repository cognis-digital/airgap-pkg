#!/usr/bin/env bash
# Install with NO network access — all wheels are local.
set -euo pipefail
pip install --no-index --find-links=wheelhouse/ -r requirements.txt
