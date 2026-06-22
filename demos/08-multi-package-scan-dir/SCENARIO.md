# 08 — Scan a whole inbound directory and gate a pipeline

**Where the data came from.** A drop directory holding three received packages:
`alpha.tar` and `bravo.tar` are clean; `charlie.tar` was corrupted after build.
This is the batch case — a courier delivers many packages and you triage them in
one pass and feed the result to CI / RMF tooling.

**What to expect.** `scan` reports 3 items, 2 verified (very_low) and 1 HIGH
finding for `charlie.tar`. With `--fail-on high` the command exits non-zero so a
pipeline stops.

**Run it.**
```bash
# human-readable triage
airgap-pkg scan demos/08-multi-package-scan-dir

# machine formats for pipelines / dashboards
airgap-pkg scan demos/08-multi-package-scan-dir --format json
airgap-pkg scan demos/08-multi-package-scan-dir --format sarif    # code-scanning
airgap-pkg scan demos/08-multi-package-scan-dir --format oscal    # eMASS/Xacta

# CI gate — non-zero exit if any HIGH+ finding exists
airgap-pkg scan demos/08-multi-package-scan-dir --fail-on high; echo "exit=$?"
```

**How to act.** Release `alpha`/`bravo` for install. Quarantine `charlie` and
request a re-transfer. Wire `--fail-on high` into CI so a bad package blocks the
high-side build automatically.
