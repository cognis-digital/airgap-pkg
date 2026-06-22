"""CLI tests: formats, --classification, --fail-on, and cross-platform BOM paths."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from airgap_pkg import cli
from airgap_pkg.core import build_package, build_bom

DEMOS_SRC = Path(__file__).parent.parent / "demos" / "01-stig-baseline-transfer" / "src"


def _isolated_src(tmp_path):
    dst = tmp_path / "src"
    shutil.copytree(DEMOS_SRC, dst)
    bom = dst / "BOM.json"
    if bom.exists():
        bom.unlink()
    return dst


def test_bom_paths_are_posix(tmp_path):
    """BOM paths must use forward slashes so they match tar members on any OS."""
    src = _isolated_src(tmp_path)
    bom = build_bom(src)
    for e in bom["entries"]:
        assert "\\" not in e["path"], f"backslash leaked into BOM path: {e['path']}"
    # nested dirs exist in this fixture, so we should see at least one slash
    assert any("/" in e["path"] for e in bom["entries"])
    # the manifest must never list itself
    assert all(e["path"] != "BOM.json" for e in bom["entries"])


def _build_scan_dir(tmp_path):
    src = _isolated_src(tmp_path)
    scan_dir = tmp_path / "drop"
    scan_dir.mkdir()
    good = build_package(src, scan_dir / "good.tar")
    # a tampered package
    bad = build_package(src, scan_dir / "bad.tar")
    with open(bad, "ab") as f:
        f.write(b"corruption")
    return scan_dir


@pytest.mark.parametrize("fmt", ["console", "json", "sarif", "markdown", "oscal"])
def test_all_formats_render(tmp_path, capsys, fmt):
    scan_dir = _build_scan_dir(tmp_path)
    rc = cli.main(["scan", str(scan_dir), "--format", fmt])
    out = capsys.readouterr().out
    assert rc == 0
    assert out.strip()
    if fmt in ("json", "sarif", "oscal"):
        json.loads(out)  # must be valid JSON


def test_classification_banner_threads_through(tmp_path, capsys):
    scan_dir = _build_scan_dir(tmp_path)
    banner = "UNCLASSIFIED//FOR OFFICIAL USE ONLY (TEST)"
    rc = cli.main(["scan", str(scan_dir), "--classification", banner, "--format", "json"])
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["classification"] == banner


def test_fail_on_high_returns_nonzero_when_bad(tmp_path, capsys):
    scan_dir = _build_scan_dir(tmp_path)  # contains a tampered (HIGH) package
    rc = cli.main(["scan", str(scan_dir), "--fail-on", "high"])
    capsys.readouterr()
    assert rc == 1


def test_fail_on_high_returns_zero_when_clean(tmp_path, capsys):
    src = _isolated_src(tmp_path)
    scan_dir = tmp_path / "clean"
    scan_dir.mkdir()
    build_package(src, scan_dir / "ok.tar")
    rc = cli.main(["scan", str(scan_dir), "--fail-on", "high"])
    capsys.readouterr()
    assert rc == 0


def test_verify_json_format_routes_through_scan(tmp_path, capsys):
    src = _isolated_src(tmp_path)
    tar = build_package(src, tmp_path / "pkg.tar")
    rc = cli.main(["verify", str(tar), "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    assert json.loads(out)["items_scanned"] == 1
