"""Tests covering error handling and edge-case paths added during hardening."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from airgap_pkg.core import AirgapError, build_bom, build_package, scan, verify_package

DEMOS_SRC = Path(__file__).parent.parent / "demos" / "src"


def _isolated_src(tmp_path):
    dst = tmp_path / "src"
    shutil.copytree(DEMOS_SRC, dst)
    bom = dst / "BOM.json"
    if bom.exists():
        bom.unlink()
    return dst


# ---------------------------------------------------------------------------
# build_bom / build_package — invalid inputs
# ---------------------------------------------------------------------------


def test_build_bom_missing_dir(tmp_path):
    """build_bom raises AirgapError when source directory does not exist."""
    with pytest.raises(AirgapError, match="not found"):
        build_bom(tmp_path / "does_not_exist")


def test_build_bom_not_a_dir(tmp_path):
    """build_bom raises AirgapError when given a file path instead of a directory."""
    f = tmp_path / "file.txt"
    f.write_text("hello")
    with pytest.raises(AirgapError, match="not a directory"):
        build_bom(f)


def test_build_package_missing_source(tmp_path):
    """build_package raises AirgapError for a non-existent source dir."""
    with pytest.raises(AirgapError, match="not found"):
        build_package(tmp_path / "no_such_dir", tmp_path / "out.tar")


def test_build_bom_empty_dir(tmp_path):
    """build_bom on an empty directory returns a valid manifest with zero files."""
    src = tmp_path / "empty"
    src.mkdir()
    bom = build_bom(src)
    assert bom["file_count"] == 0
    assert bom["entries"] == []
    assert bom["total_bytes"] == 0


# ---------------------------------------------------------------------------
# verify_package — missing / corrupt inputs
# ---------------------------------------------------------------------------


def test_verify_missing_tarball(tmp_path):
    """verify_package returns a clean error when the tarball does not exist."""
    ok, errs = verify_package(tmp_path / "ghost.tar")
    assert not ok
    assert any("not found" in e.lower() for e in errs)


def test_verify_not_a_tar(tmp_path):
    """verify_package returns a clean error for a file that is not a valid tar archive."""
    bad = tmp_path / "bad.tar"
    bad.write_bytes(b"this is not a tar file at all")
    sha = tmp_path / "bad.tar.sha256"
    import hashlib

    digest = hashlib.sha256(bad.read_bytes()).hexdigest()
    sha.write_text(f"{digest}  bad.tar\n")
    ok, errs = verify_package(bad)
    assert not ok
    assert any("cannot open" in e.lower() for e in errs)


def test_verify_empty_checksum_file(tmp_path):
    """verify_package handles a zero-byte checksum file without IndexError."""
    src = _isolated_src(tmp_path)
    tar = build_package(src, tmp_path / "pkg.tar")
    # Overwrite sha256 with empty content
    sha = tar.with_suffix(".tar.sha256")
    sha.write_text("")
    ok, errs = verify_package(tar)
    assert not ok
    assert any("empty" in e.lower() for e in errs)


def test_verify_corrupt_bom_json(tmp_path):
    """verify_package handles a tarball whose BOM.json is malformed JSON."""
    import io
    import tarfile as tf_mod

    src = _isolated_src(tmp_path)
    tar_path = build_package(src, tmp_path / "pkg.tar")

    # Rebuild the tar replacing BOM.json with invalid JSON
    new_tar = tmp_path / "corrupt.tar"
    with tf_mod.open(tar_path) as orig, tf_mod.open(new_tar, "w") as out:
        for member in orig.getmembers():
            if member.name.endswith("BOM.json"):
                bad_data = b"{not valid json!!!"
                member.size = len(bad_data)
                out.addfile(member, io.BytesIO(bad_data))
            else:
                out.addfile(member, orig.extractfile(member))

    import hashlib

    digest = hashlib.sha256(new_tar.read_bytes()).hexdigest()
    (tmp_path / "corrupt.tar.sha256").write_text(f"{digest}  corrupt.tar\n")

    ok, errs = verify_package(new_tar)
    assert not ok
    assert any("json" in e.lower() for e in errs)


# ---------------------------------------------------------------------------
# scan — edge cases
# ---------------------------------------------------------------------------


def test_scan_nonexistent_target():
    """scan on a missing path returns a HIGH finding rather than crashing."""
    result = scan("/no/such/path/xyz_nonexistent_12345")
    assert result.total_findings() > 0
    from airgap_pkg.core import Severity

    assert any(f.severity == Severity.HIGH for f in result.findings)


def test_scan_none_target():
    """scan(None) defaults to CWD and does not raise."""
    result = scan(None)
    # Should complete without exception; items_scanned may be 0 if no .tar files in CWD
    assert result is not None


def test_scan_empty_dir(tmp_path):
    """scan on a directory with no .tar files returns 0 items scanned."""
    result = scan(str(tmp_path))
    assert result.items_scanned == 0


# ---------------------------------------------------------------------------
# CLI — exit codes via subprocess
# ---------------------------------------------------------------------------


def test_cli_build_missing_output():
    """airgap-pkg build without -o exits with code 2."""
    r = subprocess.run(
        [sys.executable, "-m", "airgap_pkg", "build", "."],
        capture_output=True,
    )
    assert r.returncode == 2


def test_cli_build_missing_source_dir(tmp_path):
    """airgap-pkg build with a non-existent source dir exits non-zero and prints to stderr."""
    r = subprocess.run(
        [sys.executable, "-m", "airgap_pkg", "build", str(tmp_path / "no_such"), "-o", str(tmp_path / "out.tar")],
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0
    assert "error" in r.stderr.lower()


def test_cli_verify_missing_tarball(tmp_path):
    """airgap-pkg verify with a nonexistent file exits non-zero."""
    r = subprocess.run(
        [sys.executable, "-m", "airgap_pkg", "verify", str(tmp_path / "ghost.tar")],
        capture_output=True,
    )
    assert r.returncode != 0
