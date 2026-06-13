# airgap-pkg — Sneakernet installer for airgap networks

[![CI](https://github.com/cognis-digital/airgap-pkg/workflows/CI/badge.svg)](https://github.com/cognis-digital/airgap-pkg/actions)
[![Classification](https://img.shields.io/badge/classification-UNCLASSIFIED-green.svg)](./UPSTREAM.md)

> Build deterministic, signed, BOM-attested tarballs. Verify before install on any high-side network.

<!-- cognis:layman:start -->
## What is this?

airgap-pkg is a command-line tool that packages software for transfer onto networks that have no internet access — such as classified government systems where files must be physically carried in on a USB drive or hard disk. It bundles your files into a single archive, generates a tamper-proof fingerprint and file inventory, and lets the recipient verify that nothing was changed in transit before installation. It is designed for IT administrators and security engineers working in air-gapped military, intelligence, or government environments where software must be delivered and verified without any network connection.
<!-- cognis:layman:end -->

## Upstream

Forks / wraps **(original)**. See [`UPSTREAM.md`](./UPSTREAM.md) for the
licensing posture, supported commits, and how to upgrade.

## What this adds for military / IC use

- Deterministic tarball builder
- BOM (bill-of-materials) generation + verification
- SHA-256 self-check
- GPG signature verification (when operator provides key)
- Sneakernet-friendly: zero network calls

<!-- cognis:install:start -->
## Install

`airgap-pkg` is source-available (not published to PyPI) — every method below installs
straight from GitHub. Pick whichever you prefer; the one-line scripts auto-detect
the best tool available on your machine.

**One-liner (Linux / macOS):**
```sh
curl -fsSL https://raw.githubusercontent.com/cognis-digital/airgap-pkg/HEAD/install.sh | sh
```

**One-liner (Windows PowerShell):**
```powershell
irm https://raw.githubusercontent.com/cognis-digital/airgap-pkg/HEAD/install.ps1 | iex
```

**Or install manually — any one of:**
```sh
pipx install "git+https://github.com/cognis-digital/airgap-pkg.git"     # isolated (recommended)
uv tool install "git+https://github.com/cognis-digital/airgap-pkg.git"  # uv
pip install "git+https://github.com/cognis-digital/airgap-pkg.git"      # pip
```

**From source:**
```sh
git clone https://github.com/cognis-digital/airgap-pkg.git
cd airgap-pkg && pip install .
```

Then run:
```sh
airgap-pkg --help
```
<!-- cognis:install:end -->

## Install

```bash
# Shared library (only once for the whole ecosystem):
pip install -e ../../shared

# This tool:
pip install -e .
```

## Demo

```bash
airgap-pkg build demos/src -o demos/out.tar
airgap-pkg verify demos/out.tar
```

Outputs are available in five formats — all respect an operator-supplied
classification banner (passed via `--classification`):

```bash
airgap-pkg <target> --format=console     # default
airgap-pkg <target> --format=json
airgap-pkg <target> --format=sarif       # for code-scanning pipelines
airgap-pkg <target> --format=markdown    # for PRs / briefings
airgap-pkg <target> --format=oscal       # OSCAL Assessment Results skeleton
```

## Classification banner

All output is wrapped with an operator-supplied classification banner.
**Default**: `UNCLASSIFIED//FOR PUBLIC RELEASE`.

> ⚠️ This tool **does not** generate or validate the *content* of higher
> classifications. Operators on cleared systems supply real markings at runtime.
> See [`../shared/cognis_mil/classmark.py`](../../shared/cognis_mil/classmark.py).

## Compliance crosswalks (built in)

Every finding can carry references to:
- **NIST 800-53 Rev 5** controls (e.g. `AC-2(1)`)
- **DISA STIG** rule IDs (e.g. `V-242414`)
- **MITRE ATT&CK** technique IDs (e.g. `T1078`)
- **CCI** (Control Correlation Identifier)

These are emitted in JSON, SARIF, and the OSCAL skeleton.

## CI / RMF integration

```yaml
- name: airgap-pkg scan
  run: |
    pip install "git+https://github.com/cognis-digital/airgap-pkg.git"
    airgap-pkg . --format=oscal --out=assessment-results.json --fail-on=high
- name: Upload to eMASS/Xacta
  run: cognis-rmf-package import assessment-results.json
```

## Part of the Cognis Digital military / IC ecosystem

12 repos. All MIT/Apache-2.0/GPL-3 (per upstream). Cognis additions are
Apache-2.0 unless stated otherwise.

See [the master index](../../MASTER-INDEX.md).

<a name="verification"></a>
## Verification

[![tests](https://img.shields.io/badge/tests-3%20passing-2ea44f.svg)](AUDIT.md)

Every push is verified end-to-end. Latest audit (2026-06-13):

```text
tests        : 3 passed, 0 failed, 0 errored
compile      : all modules parse
cli          : airgap-pkg 0.1.0
package      : airgap_pkg
```

<details><summary>CLI surface (<code>--help</code>)</summary>

```text
usage: airgap-pkg [-h] [-o OUTPUT] [--format {console,json}] [-v]
                  [{build,verify,scan}] [source]

positional arguments:
  {build,verify,scan}
  source                Source dir (build) or tarball (verify)

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Output tarball path (build)
  --format {console,json}
  -v, --version         show program's version number and exit
```
</details>

Full machine-readable results: [`AUDIT.md`](AUDIT.md) · regenerate with `python -m airgap_pkg --help` + `pytest -q`.

<div align="right"><a href="#top">↑ back to top</a></div>

