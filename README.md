# airgap-pkg — Sneakernet installer for airgap networks

[![CI](https://github.com/cognis-digital/airgap-pkg/workflows/CI/badge.svg)](https://github.com/cognis-digital/airgap-pkg/actions)
[![Classification](https://img.shields.io/badge/classification-UNCLASSIFIED-green.svg)](./UPSTREAM.md)

> Build deterministic, signed, BOM-attested tarballs. Verify before install on any high-side network.

## Usage — step by step

1. **Install** the shared library once, then this tool:
   ```bash
   pip install -e ../../shared    # ecosystem shared lib (once)
   pip install -e .               # airgap-pkg
   ```
2. **Build a sneakernet package** from a source directory. `build` is the first positional action; `-o/--output` names the tarball:
   ```bash
   airgap-pkg build demos/src -o demos/out.tar
   ```
3. **Verify a received tarball** on the destination (airgapped) side:
   ```bash
   airgap-pkg verify demos/out.tar
   ```
4. **Read the output** as JSON for tooling (the default action is `scan`; `--format` is `console` or `json`):
   ```bash
   airgap-pkg verify demos/out.tar --format json
   echo $?    # non-zero on a failed verification
   ```
5. **Automate in CI** — build the transfer package and gate the pipeline on a clean verify:
   ```yaml
   - run: pip install -e ../../shared && pip install -e .
   - run: airgap-pkg build . -o transfer.tar
   - run: airgap-pkg verify transfer.tar --format json
   ```

## Upstream

Forks / wraps **(original)**. See [`UPSTREAM.md`](./UPSTREAM.md) for the
licensing posture, supported commits, and how to upgrade.

## What this adds for military / IC use

- Deterministic tarball builder
- BOM (bill-of-materials) generation + verification
- SHA-256 self-check
- GPG signature verification (when operator provides key)
- Sneakernet-friendly: zero network calls

## Install

```bash
# Shared library (only once for the whole ecosystem):
pip install -e ../../shared

# This tool:
pip install -e .
```

## Demos

Nine end-to-end, real-input-format scenarios live under [`demos/`](./demos/)
— each with its own `SCENARIO.md` (provenance, exact command, expected output,
how to act). See the [demo index](./demos/SCENARIO.md). Highlights:

| # | Demo | Shows |
|---|------|-------|
| 01 | [STIG baseline transfer](./demos/01-stig-baseline-transfer/) | build + verify a DISA RHEL 9 STIG role |
| 02 | [Offline pip wheelhouse](./demos/02-offline-pip-wheelhouse/) | ship hash-pinned deps with zero network |
| 03 | [Container image bundle](./demos/03-container-image-bundle/) | seed an offline registry |
| 04 | [Tampered tarball](./demos/04-tamper-detected-incoming/) | SHA-256 mismatch is caught |
| 05 | [Missing checksum](./demos/05-missing-checksum-incoming/) | reject a package with no `.sha256` |
| 06 | [Injected file](./demos/06-bom-mismatch-incoming/) | BOM catches an undeclared file the checksum can't |
| 07 | [Firmware update](./demos/07-firmware-update-package/) | two-layer integrity (vendor + BOM) |
| 08 | [Multi-package scan + CI gate](./demos/08-multi-package-scan-dir/) | triage a drop dir, fail CI on bad packages |
| 09 | [Classification banner](./demos/09-classified-banner-briefing/) | `--classification` threaded into every format |

```bash
airgap-pkg build demos/01-stig-baseline-transfer/src -o /tmp/out.tar
airgap-pkg verify /tmp/out.tar
```

`verify` and `scan` outputs are available in five formats — all respect an
operator-supplied classification banner (`--classification`):

```bash
airgap-pkg <target> --format console      # default
airgap-pkg <target> --format json
airgap-pkg <target> --format sarif        # for code-scanning pipelines
airgap-pkg <target> --format markdown     # for PRs / briefings
airgap-pkg <target> --format oscal        # OSCAL Assessment Results skeleton
```

Gate a pipeline on package integrity with `--fail-on` (exits non-zero when any
finding is at or above the given severity):

```bash
airgap-pkg scan ./inbound --fail-on high   # exit 1 if any package fails to verify
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
    pip install cognis-airgap-pkg
    airgap-pkg scan ./inbound --format oscal --fail-on high > assessment-results.json
- name: Upload to eMASS/Xacta
  run: cognis-rmf-package import assessment-results.json
```

## Part of the Cognis Digital military / IC ecosystem

12 repos. All MIT/Apache-2.0/GPL-3 (per upstream). Cognis additions are
Apache-2.0 unless stated otherwise.

See [the master index](../../MASTER-INDEX.md).

## Interoperability

`airgap-pkg` composes with the 300+ tool Cognis suite — JSON in/out and a shared
OpenAI-compatible `/v1` backbone. See **[INTEROP.md](INTEROP.md)** for the
suite map, composition patterns, and reference stacks.

## Integrations

Forward `airgap-pkg`'s findings to STIX/MISP/Sigma/Splunk/Elastic/Slack/webhooks via
[`cognis-connect`](https://github.com/cognis-digital/cognis-connect). See **[INTEGRATIONS.md](INTEGRATIONS.md)**.
