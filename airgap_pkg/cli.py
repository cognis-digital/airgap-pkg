"""CLI: airgap-pkg build|verify|scan.

Outputs (for `verify`/`scan`) are available in five formats — all respect an
operator-supplied classification banner via ``--classification``:

    airgap-pkg <target> --format console     # default
    airgap-pkg <target> --format json
    airgap-pkg <target> --format sarif        # code-scanning pipelines
    airgap-pkg <target> --format markdown     # PRs / briefings
    airgap-pkg <target> --format oscal        # OSCAL Assessment Results skeleton

CI gating: ``--fail-on {very_low,low,moderate,high,very_high}`` exits non-zero
when any finding at or above the given severity is present.
"""
import argparse, sys
from pathlib import Path
from cognis_mil import (
    to_console, to_json, to_sarif, to_markdown, to_oscal_skeleton,
)
from cognis_mil.models import Severity, WEIGHTS
from .core import build_package, verify_package, scan
from . import __version__

FORMATTERS = {
    "console": to_console,
    "json": to_json,
    "sarif": to_sarif,
    "markdown": to_markdown,
    "oscal": to_oscal_skeleton,
}

# Severity ordering (low -> high), used by --fail-on.
_SEV_ORDER = [
    Severity.VERY_LOW, Severity.LOW, Severity.MODERATE,
    Severity.HIGH, Severity.VERY_HIGH,
]


def render(result, fmt: str) -> str:
    return FORMATTERS[fmt](result)


def _fail_on_triggered(result, threshold: str) -> bool:
    """True if any finding's severity is >= the threshold severity."""
    floor = _SEV_ORDER.index(Severity(threshold))
    return any(_SEV_ORDER.index(f.severity) >= floor for f in result.findings)


def _force_utf8_stdout():
    """Best-effort UTF-8 stdout so banners/glyphs render on legacy consoles
    (e.g. Windows cp1252) instead of raising UnicodeEncodeError."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


def main(argv=None):
    _force_utf8_stdout()
    p = argparse.ArgumentParser(prog="airgap-pkg")
    p.add_argument("action", nargs="?", default="scan", choices=["build", "verify", "scan"])
    p.add_argument("source", nargs="?", default=".", help="Source dir (build) or tarball/dir (verify/scan)")
    p.add_argument("-o", "--output", help="Output tarball path (build)")
    p.add_argument("--format", choices=list(FORMATTERS), default="console")
    p.add_argument("--classification", default=None,
                   help="Operator-supplied classification banner (placeholder shape only)")
    p.add_argument("--fail-on", choices=[s.value for s in _SEV_ORDER], default=None,
                   help="Exit non-zero if any finding is at or above this severity")
    p.add_argument("-v", "--version", action="version", version=f"airgap-pkg {__version__}")
    args = p.parse_args(argv)

    if args.action == "build":
        if not args.output:
            print("Usage: airgap-pkg build <source-dir> -o <out>.tar", file=sys.stderr)
            return 2
        t = build_package(Path(args.source), Path(args.output))
        digest = t.with_suffix(t.suffix + ".sha256").read_text().split()[0]
        print(f"✓ Built {t} ({digest[:12]}…)")
        return 0

    if args.action == "verify":
        # verify is a single-tarball convenience; honor --format via a scan result too.
        ok, errs = verify_package(Path(args.source))
        if args.format == "console":
            if ok:
                print(f"✓ {args.source} verified")
            else:
                print(f"✗ {args.source} failed verification:")
                for e in errs:
                    print(f"  - {e}")
            return 0 if ok else 1
        # structured formats: route through scan() so the result is a full ScanResult
        result = scan(args.source)
        if args.classification:
            result.classification_placeholder = args.classification
        print(render(result, args.format))
        return 0 if ok else 1

    # scan
    result = scan(args.source)
    if args.classification:
        result.classification_placeholder = args.classification
    print(render(result, args.format))
    if args.fail_on and _fail_on_triggered(result, args.fail_on):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
