# 04 — Detect a tampered / corrupted incoming tarball

**Where the data came from.** `incoming.tar` is a package that was built
correctly, but extra bytes were appended after the `.sha256` sidecar was
written — simulating bit-rot on the courier media or deliberate tampering in
transit. The checksum file still reflects the *original* bytes.

**What to expect.** Verification **FAILS** with a SHA-256 mismatch and a
non-zero exit code. This is the core safety property: never trust an incoming
package whose bytes don't match its checksum.

**Run it.**
```bash
airgap-pkg verify demos/04-tamper-detected-incoming/incoming.tar
echo $?   # 1
```
Expected: `✗ … SHA-256 mismatch …`, exit code `1`.

**How to act.** Quarantine the media. Do not extract or install. Request a
re-transfer and, if tampering is suspected rather than media error, report per
your incident-response SOP.
