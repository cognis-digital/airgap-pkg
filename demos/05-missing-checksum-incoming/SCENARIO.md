# 05 — Reject an incoming package with no checksum sidecar

**Where the data came from.** `incoming.tar` arrived **without** its
`incoming.tar.sha256` sidecar — the courier dropped it, or someone exported only
the tarball. Without the sidecar there is no integrity anchor.

**What to expect.** Verification **FAILS**: `No .sha256 checksum file alongside
tarball`, exit code `1`.

**Run it.**
```bash
airgap-pkg verify demos/05-missing-checksum-incoming/incoming.tar
echo $?   # 1
```

**How to act.** Do not install. A package with no checksum cannot be trusted on
a high-side network. Obtain the original `.sha256` (or a freshly rebuilt,
signed package) before proceeding.
