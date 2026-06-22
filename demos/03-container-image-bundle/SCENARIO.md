# 03 — Seed an offline registry from a container image bundle

**Where the data came from.** `src/` mimics a `docker save` / `podman save`
export: a `manifest.txt` mapping `name:tag → file`, a `load-images.sh`, and the
image tarballs under `src/images/`. The `*.tar` blobs here are clearly-marked
PLACEHOLDERS — replace `images/nginx-1.27.tar` with real `docker save nginx:1.27`
output in production.

**What to expect.** A single signed, BOM-attested transfer artifact that carries
multiple image tarballs and the load script.

**Run it.**
```bash
airgap-pkg build demos/03-container-image-bundle/src -o demos/03-container-image-bundle/images.tar
airgap-pkg verify demos/03-container-image-bundle/images.tar
```

**How to act.** After a clean verify, extract and run `load-images.sh` on the
disconnected docker host, then `docker tag`/`docker push` into the local
registry.
