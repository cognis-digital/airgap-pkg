# airgap-pkg demos — index

Each numbered subdirectory is a self-contained, **real-input-format** scenario
with its own `SCENARIO.md` (where the data came from, what to expect, the exact
command, and how to act on the result). Every demo has been verified to actually
produce its intended output. The original minimal fixture lives in `src/`.

| # | Demo | Action exercised | Expected result |
|---|------|------------------|-----------------|
| 01 | [STIG hardening baseline transfer](01-stig-baseline-transfer/) | `build` + `verify` | clean verify |
| 02 | [Offline pip wheelhouse](02-offline-pip-wheelhouse/) | `build` + `verify --format json` | clean verify, exit 0 |
| 03 | [Container image bundle](03-container-image-bundle/) | `build` + `verify` | clean verify |
| 04 | [Tampered incoming tarball](04-tamper-detected-incoming/) | `verify` | **FAIL** — SHA-256 mismatch, exit 1 |
| 05 | [Missing checksum sidecar](05-missing-checksum-incoming/) | `verify` | **FAIL** — no `.sha256`, exit 1 |
| 06 | [Undeclared file injected (BOM mismatch)](06-bom-mismatch-incoming/) | `verify` | **FAIL** — extra file not in BOM, exit 1 |
| 07 | [Switch firmware update package](07-firmware-update-package/) | `build` + `verify --format json` | clean verify |
| 08 | [Multi-package inbound scan + CI gate](08-multi-package-scan-dir/) | `scan` + `--format` + `--fail-on` | 2 clean, 1 HIGH; `--fail-on high` exits 1 |
| 09 | [Operator classification banner](09-classified-banner-briefing/) | `scan --classification` | banner threaded into report |

## Quick run

```bash
# happy path
airgap-pkg build demos/01-stig-baseline-transfer/src -o /tmp/out.tar
airgap-pkg verify /tmp/out.tar

# triage a whole inbound directory and gate CI on it
airgap-pkg scan demos/08-multi-package-scan-dir --format sarif
airgap-pkg scan demos/08-multi-package-scan-dir --fail-on high; echo "exit=$?"
```

> **Placeholder note.** Demos 02/03/07 ship clearly-marked PLACEHOLDER binary
> stand-ins (wheels, OCI image blobs, firmware) so the repo stays small and
> contains no fabricated real-world hashes. Swap in real artifacts for
> production use; the build/verify mechanics are identical.
