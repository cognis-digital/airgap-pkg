#!/usr/bin/env bash
set -euo pipefail
for img in images/*.tar; do
  echo "Loading ${img} ..."
  docker load -i "${img}"
done
