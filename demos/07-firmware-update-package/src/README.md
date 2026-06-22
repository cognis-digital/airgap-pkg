# Network switch firmware update package

Vendor-supplied firmware image staged for an offline maintenance window on a
high-side network switch. Operator verifies the airgap-pkg signature/BOM, then
verifies the vendor's own published checksum before flashing. Two layers of
integrity: vendor checksum + airgap-pkg BOM.

DO NOT flash without an approved change ticket and a rollback image on hand.
