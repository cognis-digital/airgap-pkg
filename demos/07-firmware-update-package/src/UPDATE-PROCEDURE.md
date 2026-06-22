# Maintenance window procedure

1. Verify this package:  airgap-pkg verify firmware.tar --format json
2. Compare firmware.bin against the vendor checksum below (out-of-band).
3. Stage on standby supervisor, reload standby, verify, then switchover.
4. Keep prior image as rollback for one full maintenance cycle.
