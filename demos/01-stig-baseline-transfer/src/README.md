# RHEL 9 DISA STIG Hardening Baseline (V2R1)

Ansible-driven remediation content for the Red Hat Enterprise Linux 9 STIG.
Intended for one-way transfer to a SIPR-side build host that has no internet
access. Apply with `ansible-playbook site.yml -i inventory` after verifying
the package on the high side.

- Source: DISA RHEL 9 STIG benchmark, Version 2 Release 1 (public, UNCLASSIFIED).
- Scope: CAT I/II controls only; CAT III left to local policy.
