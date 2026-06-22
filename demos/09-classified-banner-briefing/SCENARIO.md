# 09 — Stamp an operator-supplied classification banner on the report

**Where the data came from.** `src/briefing.md` is UNCLASSIFIED sample content.
The point of this demo is the **`--classification`** flag: a cleared operator
supplies the real banner at runtime; the tool validates banner *shape*, never
content, and never ships real markings.

**What to expect.** Identical verification, but the report banner reflects the
operator-supplied string.

**Run it.**
```bash
airgap-pkg build demos/09-classified-banner-briefing/src -o demos/09-classified-banner-briefing/briefing.tar
airgap-pkg scan demos/09-classified-banner-briefing \
  --classification 'UNCLASSIFIED//FOR OFFICIAL USE ONLY (DEMO)' --format markdown
```

**How to act.** Use the markdown/SARIF/OSCAL outputs in PRs, code-scanning
pipelines, or eMASS/Xacta. The banner you pass is echoed verbatim into every
format.
