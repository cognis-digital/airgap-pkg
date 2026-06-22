# 07 — Stage a network-switch firmware update for an offline maintenance window

**Where the data came from.** `src/` represents a vendor firmware image staged
for flashing on a high-side switch. `firmware.bin` is a PLACEHOLDER blob; the
real value is the vendor-published image. `vendor-checksum.txt` is intentionally
a fill-in-the-blank — the operator pastes the **vendor's** published SHA-256
obtained out-of-band. This demo shows the two-layer integrity model: vendor
checksum **and** airgap-pkg BOM.

**What to expect.** A verifiable transfer package plus an UPDATE-PROCEDURE the
maintenance crew follows.

**Run it.**
```bash
airgap-pkg build demos/07-firmware-update-package/src -o demos/07-firmware-update-package/firmware.tar
airgap-pkg verify demos/07-firmware-update-package/firmware.tar --format json
```

**How to act.** Verify with airgap-pkg, then compare `firmware.bin` against the
vendor checksum out-of-band, then follow `UPDATE-PROCEDURE.md`. Never flash
without an approved change ticket and a rollback image.
