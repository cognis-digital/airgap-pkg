# 06 — Catch an undeclared file injected into a package

**Where the data came from.** `incoming.tar` has a **valid** outer SHA-256 (so
it passes the checksum gate) but its `BOM.json` declares only two files while
the tarball secretly carries a third — `payload/.backdoor.sh` — that is NOT in
the manifest. This models a supply-chain injection where the BOM and the bytes
disagree.

**What to expect.** Verification **FAILS** on the BOM membership check:
`Files in tarball but not in BOM: ['payload/.backdoor.sh']`, exit code `1`.
The checksum alone would have passed — the BOM is what catches it.

**Run it.**
```bash
airgap-pkg verify demos/06-bom-mismatch-incoming/incoming.tar
echo $?   # 1
```

**How to act.** Treat the undeclared file as hostile until proven otherwise.
Quarantine, do not extract on a target host, and escalate per IR SOP. The BOM
mismatch is exactly the signal you transfer airgapped packages to get.
