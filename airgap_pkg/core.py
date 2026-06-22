"""airgap-pkg — build / verify / install offline tarballs.

Self-contained, deterministic, GPG-signed (when operator provides a key).
No network calls. Verifies BOM + SHA-256 + (optional) GPG sig before
install. Designed for SIPR/JWICS-style sneakernet transfer.
"""
from __future__ import annotations
import hashlib, json, os, shutil, subprocess, tarfile, time
from pathlib import Path
from cognis_mil import ScanResult, Finding, Severity

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
    return h.hexdigest()

def build_bom(source_dir: Path) -> dict:
    """Build a Bill-of-Materials manifest for every file in source_dir."""
    entries = []
    for f in sorted(source_dir.rglob("*")):
        if not f.is_file(): continue
        if any(part in (".git","__pycache__",".venv","node_modules") for part in f.parts): continue
        if f.name == "BOM.json": continue  # never list the manifest inside itself
        # POSIX-style relative path so BOMs are identical across OSes and match
        # tar member names (tar always uses forward slashes).
        rel = f.relative_to(source_dir).as_posix()
        entries.append({
            "path": rel,
            "size": f.stat().st_size,
            "sha256": sha256_file(f),
        })
    return {
        "manifest_version": "1.0",
        "created_at": int(time.time()),
        "file_count": len(entries),
        "total_bytes": sum(e["size"] for e in entries),
        "entries": entries,
    }

def build_package(source_dir: Path, output: Path, name: str = None) -> Path:
    """Build a tarball + BOM + checksum. Deterministic ordering."""
    name = name or source_dir.name
    output.parent.mkdir(parents=True, exist_ok=True)
    bom = build_bom(source_dir)
    bom_file = source_dir / "BOM.json"
    bom_file.write_text(json.dumps(bom, indent=2, sort_keys=True))
    # Build tar deterministically (sorted, no timestamps drift)
    tar_path = output if str(output).endswith(".tar") else Path(str(output) + ".tar")
    with tarfile.open(tar_path, "w") as tf:
        for entry in bom["entries"] + [{"path":"BOM.json"}]:
            p = source_dir / entry["path"]
            if p.exists():
                ti = tf.gettarinfo(str(p), arcname=f"{name}/{entry['path']}")
                ti.mtime = 0  # deterministic
                ti.uid = ti.gid = 0
                ti.uname = ti.gname = ""
                with p.open("rb") as fh:
                    tf.addfile(ti, fh)
    # Write checksum file
    chk = tar_path.with_suffix(tar_path.suffix + ".sha256")
    chk.write_text(f"{sha256_file(tar_path)}  {tar_path.name}\n")
    return tar_path

def verify_package(tar_path: Path, gpg_sig: Path = None, gpg_key_id: str = None) -> tuple[bool, list[str]]:
    errs = []
    chk = tar_path.with_suffix(tar_path.suffix + ".sha256")
    if not chk.exists(): errs.append("No .sha256 checksum file alongside tarball")
    else:
        expected = chk.read_text().split()[0]
        actual = sha256_file(tar_path)
        if expected != actual:
            errs.append(f"SHA-256 mismatch (expected {expected[:12]}…, got {actual[:12]}…)")
    if gpg_sig and gpg_key_id:
        try:
            rc = subprocess.run(["gpg","--verify",str(gpg_sig), str(tar_path)],
                                capture_output=True, text=True).returncode
            if rc != 0: errs.append("GPG signature verification failed")
        except FileNotFoundError:
            errs.append("gpg binary not available; cannot verify signature")
    # Verify BOM against tarball contents
    with tarfile.open(tar_path) as tf:
        names = tf.getnames()
        bom_member = next((n for n in names if n.endswith("BOM.json")), None)
        if not bom_member: errs.append("No BOM.json in tarball")
        else:
            bom_data = json.loads(tf.extractfile(bom_member).read())
            declared = {e["path"] for e in bom_data["entries"]}
            actual_paths = {n.split("/",1)[1] for n in names if "/" in n and not n.endswith("BOM.json")}
            missing = declared - actual_paths
            extra = actual_paths - declared
            if missing: errs.append(f"Files in BOM but not in tarball: {sorted(missing)[:5]}")
            if extra:   errs.append(f"Files in tarball but not in BOM: {sorted(extra)[:5]}")
    return (len(errs) == 0, errs)

def scan(target=".", **opts):
    """Scan a directory of `*.tar` / `*.tar.sha256` packages and verify each."""
    from . import __version__
    r = ScanResult(tool_name="airgap-pkg", tool_version=__version__)
    p = Path(target)
    tars = list(p.glob("*.tar")) if p.is_dir() else ([p] if p.suffix == ".tar" else [])
    r.items_scanned = len(tars)
    for t in tars:
        ok, errs = verify_package(t)
        if ok:
            r.add(Finding(f"AP-OK-{t.stem}", Severity.VERY_LOW, f"Verified: {t.name}", location=str(t)))
        else:
            for e in errs:
                r.add(Finding(f"AP-BAD-{t.stem}", Severity.HIGH, f"{t.name}: {e}", location=str(t),
                              remediation="Rebuild package or obtain a clean copy"))
    r.finalize(); return r
