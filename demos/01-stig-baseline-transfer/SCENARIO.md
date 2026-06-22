# 01 — Transfer a DISA STIG hardening baseline to a SIPR build host

**Where the data came from.** `src/` holds an Ansible remediation role for the
public, UNCLASSIFIED **DISA RHEL 9 STIG (V2R1)** benchmark. The rule IDs in
`src/stig/main.yml` (e.g. `RHEL-09-211010`, `RHEL-09-412035`) come from the
published benchmark. You build this on a connected staging box and sneakernet
the tarball to a disconnected build host.

**What to expect.** `baseline.tar` + `baseline.tar.sha256` were produced by the
`build` command. On the high side, `verify` confirms the SHA-256 and that every
file in the BOM is present and nothing extra was injected.

**Run it.**
```bash
# (re)build from source on the low side
airgap-pkg build demos/01-stig-baseline-transfer/src -o demos/01-stig-baseline-transfer/baseline.tar
# verify on the high side
airgap-pkg verify demos/01-stig-baseline-transfer/baseline.tar
```
Expected: `✓ … verified`.

**How to act.** After a clean verify, extract and run
`ansible-playbook site.yml -i inventory`. If verify fails, do **not** apply the
baseline — obtain a fresh copy and re-transfer.
