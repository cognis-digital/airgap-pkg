# Container image bundle — offline registry seed

A `docker save` / `podman save` style image bundle plus a load script, for
seeding a disconnected registry. The image tarball here is a small placeholder
stand-in; in real use you replace `images/nginx-1.27.tar` with the output of
`docker save nginx:1.27 -o nginx-1.27.tar`.
