# 02 — Ship an offline pip wheelhouse to a disconnected analyst box

**Where the data came from.** `src/requirements.txt` is a pinned dependency set
(`requests` and its transitive deps). In real use you populate `src/wheelhouse/`
with `pip download -r requirements.txt -d wheelhouse/ --only-binary=:all:`. The
`.whl` files committed here are clearly-marked PLACEHOLDER stand-ins so the demo
stays small and self-contained — replace them with real wheels for production.

**What to expect.** A verifiable bundle the analyst box installs with **zero**
network access via `pip install --no-index --find-links=wheelhouse/`.

**Run it.**
```bash
airgap-pkg build demos/02-offline-pip-wheelhouse/src -o demos/02-offline-pip-wheelhouse/wheelhouse.tar
airgap-pkg verify demos/02-offline-pip-wheelhouse/wheelhouse.tar --format json
echo $?   # 0 on success
```

**How to act.** On a clean verify, extract and run `install-offline.sh`. The
BOM check guarantees no wheel was added or swapped in transit.
