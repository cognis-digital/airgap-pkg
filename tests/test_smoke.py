import shutil
from pathlib import Path

from airgap_pkg.core import build_bom, build_package, verify_package

DEMOS_SRC = Path(__file__).parent.parent / "demos" / "src"


def _isolated_src(tmp_path):
    """Copy demo source to a tmp dir so tests never mutate the repo."""
    dst = tmp_path / "src"
    shutil.copytree(DEMOS_SRC, dst)
    # remove any BOM.json that might be lingering from a previous run
    bom = dst / "BOM.json"
    if bom.exists():
        bom.unlink()
    return dst


def test_bom(tmp_path):
    src = _isolated_src(tmp_path)
    bom = build_bom(src)
    assert bom["file_count"] >= 2
    assert all("sha256" in e for e in bom["entries"])


def test_build_and_verify(tmp_path):
    src = _isolated_src(tmp_path)
    out = tmp_path / "pkg.tar"
    tar = build_package(src, out)
    assert tar.exists()
    assert (tar.with_suffix(".tar.sha256")).exists()
    ok, errs = verify_package(tar)
    assert ok, errs


def test_tamper_detection(tmp_path):
    src = _isolated_src(tmp_path)
    out = tmp_path / "pkg.tar"
    tar = build_package(src, out)
    with open(tar, "ab") as f:
        f.write(b"extra bytes")
    ok, errs = verify_package(tar)
    assert not ok
