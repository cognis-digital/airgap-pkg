"""CLI: airgap-pkg build|verify|scan."""
import argparse
import sys
from pathlib import Path

from cognis_mil import to_console, to_json

from . import __version__
from .core import AirgapError, build_package, scan, verify_package


def main() -> int:
    p = argparse.ArgumentParser(prog="airgap-pkg")
    p.add_argument("action", nargs="?", default="scan", choices=["build", "verify", "scan"])
    p.add_argument("source", nargs="?", default=".", help="Source dir (build) or tarball (verify)")
    p.add_argument("-o", "--output", help="Output tarball path (build)")
    p.add_argument("--format", choices=["console", "json"], default="console")
    p.add_argument("-v", "--version", action="version", version=f"airgap-pkg {__version__}")
    args = p.parse_args()

    try:
        if args.action == "build":
            if not args.output:
                print("Usage: airgap-pkg build <source-dir> -o <out>.tar", file=sys.stderr)
                return 2
            t = build_package(Path(args.source), Path(args.output))
            sha_file = t.with_suffix(t.suffix + ".sha256")
            sha_parts = sha_file.read_text().split() if sha_file.exists() else []
            sha_preview = sha_parts[0][:12] + "…" if sha_parts else "(no checksum)"
            print(f"Built {t} ({sha_preview})")
            return 0

        elif args.action == "verify":
            ok, errs = verify_package(Path(args.source))
            if ok:
                print(f"OK {args.source} verified")
                return 0
            else:
                print(f"FAIL {args.source} failed verification:", file=sys.stderr)
                for e in errs:
                    print(f"  - {e}", file=sys.stderr)
                return 1

        else:  # scan
            r = scan(args.source)
            print(to_json(r) if args.format == "json" else to_console(r))
            return 0

    except AirgapError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"Error: file not found — {exc}", file=sys.stderr)
        return 2
    except PermissionError as exc:
        print(f"Error: permission denied — {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
