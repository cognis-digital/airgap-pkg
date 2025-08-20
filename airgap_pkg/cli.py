"""CLI: airgap-pkg build|verify|scan."""
import argparse, sys
from pathlib import Path
from cognis_mil import to_console, to_json
from .core import build_package, verify_package, scan
from . import __version__
def main():
    p = argparse.ArgumentParser(prog="airgap-pkg")
    p.add_argument("action", nargs="?", default="scan", choices=["build","verify","scan"])
    p.add_argument("source", nargs="?", default=".", help="Source dir (build) or tarball (verify)")
    p.add_argument("-o","--output", help="Output tarball path (build)")
    p.add_argument("--format", choices=["console","json"], default="console")
    p.add_argument("-v","--version", action="version", version=f"airgap-pkg {__version__}")
    args = p.parse_args()
    if args.action == "build":
        if not args.output: print("Usage: airgap-pkg build <source-dir> -o <out>.tar", file=sys.stderr); sys.exit(2)
        t = build_package(Path(args.source), Path(args.output))
        print(f"✓ Built {t} ({t.with_suffix(t.suffix+'.sha256').read_text().split()[0][:12]}…)")
    elif args.action == "verify":
        ok, errs = verify_package(Path(args.source))
        if ok: print(f"✓ {args.source} verified")
        else:
            print(f"✗ {args.source} failed verification:")
            for e in errs: print(f"  - {e}"); sys.exit(1)
    else:
        r = scan(args.source)
        print(to_json(r) if args.format == "json" else to_console(r))
if __name__ == "__main__": main()
