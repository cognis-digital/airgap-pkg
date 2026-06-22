# Offline pip wheelhouse — analyst workstation deps

Self-contained Python dependency bundle for a disconnected analysis box.
No `pip install` ever touches PyPI on the high side; everything resolves from
`wheelhouse/`. Verify this package, extract, then run `install-offline.sh`.
