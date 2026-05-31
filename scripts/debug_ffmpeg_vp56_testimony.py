#!/usr/bin/env python3
"""
Generate a VP56 capability/debug testimony report for FFmpeg.

This is intended for cubic-nls / agentic-nls-blockcode troubleshooting when
users request VP56-based pipelines (for example: vp6f bridge before H.264 MP4).
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


UPSTREAM_REFERENCES = [
    {
        "name": "FFmpeg VP56 common decoder core",
        "url": "https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/vp56.c",
    },
    {
        "name": "FFmpeg VP56 decoder header",
        "url": "https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/vp56.h",
    },
    {
        "name": "FFmpeg VP6 decoder implementation",
        "url": "https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/vp6.c",
    },
    {
        "name": "FFmpeg codec registry (allcodecs.c)",
        "url": "https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/allcodecs.c",
    },
    {
        "name": "FFmpeg supported codec matrix (general_contents.texi)",
        "url": "https://github.com/FFmpeg/FFmpeg/blob/master/doc/general_contents.texi",
    },
]


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, text=True, capture_output=True)


def parse_codec_rows(codecs_text: str) -> dict[str, dict[str, bool | str]]:
    rows: dict[str, dict[str, bool | str]] = {}
    for line in codecs_text.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        flags = parts[0]
        name = parts[1]
        if name not in {"vp5", "vp6", "vp6a", "vp6f"}:
            continue
        rows[name] = {
            "raw": line.strip(),
            "decode": "D" in flags,
            "encode": "E" in flags,
        }
    return rows


def has_encoder(encoders_text: str, encoder: str) -> bool:
    for line in encoders_text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == encoder:
            return True
    return False


def build_markdown_report(
    *,
    ffmpeg_version_line: str,
    codec_rows: dict[str, dict[str, bool | str]],
    encoder_presence: dict[str, bool],
    encoder_probe_output: str,
    json_output_path: Path,
) -> str:
    utc_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    available_vp56_encoders = [k for k, v in encoder_presence.items() if v]

    if available_vp56_encoders:
        verdict = (
            f"VP56 encoder(s) found: {', '.join(available_vp56_encoders)}. "
            "Bridge mode should be runnable."
        )
    else:
        verdict = (
            "No VP56 encoder is available in this FFmpeg build. "
            "VP56 bridge mode cannot run here; only H.264 direct output is supported."
        )

    table_lines = [
        "| codec | decode | encode | raw row |",
        "|---|---:|---:|---|",
    ]
    for key in ["vp5", "vp6", "vp6a", "vp6f"]:
        row = codec_rows.get(key)
        if row is None:
            table_lines.append(f"| {key} | no | no | not listed |")
        else:
            table_lines.append(
                f"| {key} | {'yes' if row['decode'] else 'no'} | "
                f"{'yes' if row['encode'] else 'no'} | `{row['raw']}` |"
            )

    ref_lines = [f"- [{item['name']}]({item['url']})" for item in UPSTREAM_REFERENCES]

    return f"""# FFmpeg VP56 Debug Testimony

Generated: {utc_now}

## Environment

- FFmpeg: `{ffmpeg_version_line}`
- JSON evidence: `{json_output_path}`

## VP56 capability snapshot

{chr(10).join(table_lines)}

## Encoder probes

- `vp6f` encoder present in `ffmpeg -encoders`: `{encoder_presence['vp6f']}`
- `vp6a` encoder present in `ffmpeg -encoders`: `{encoder_presence['vp6a']}`
- `vp6` encoder present in `ffmpeg -encoders`: `{encoder_presence['vp6']}`
- `libxvp56` encoder present in `ffmpeg -encoders`: `{encoder_presence['libxvp56']}`

Probe output (`ffmpeg -h encoder=vp6f`):

```text
{encoder_probe_output.strip()}
```

## Verdict

{verdict}

## Interpretation for agentic-nls-blockcode

- The requested `libxVP56` label is not an FFmpeg encoder name.
- FFmpeg upstream provides VP56 family decoder sources (`vp56.c`, `vp6.c`) and codec entries for decoding.
- In this environment, the exporter should continue using H.264 MP4 output (`libx264`) unless a custom FFmpeg build adds a VP56 encoder.

## Upstream source references

{chr(10).join(ref_lines)}
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate FFmpeg VP56 debug testimony report."
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("output/ffmpeg_vp56_testimony.md"),
        help="Path to markdown testimony output.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("output/ffmpeg_vp56_testimony.json"),
        help="Path to JSON evidence output.",
    )
    args = parser.parse_args()

    ffmpeg_version = run(["ffmpeg", "-version"])
    encoders = run(["ffmpeg", "-hide_banner", "-encoders"])
    codecs = run(["ffmpeg", "-hide_banner", "-codecs"])
    vp6_probe = run(["ffmpeg", "-hide_banner", "-h", "encoder=vp6f"])

    version_line = ffmpeg_version.stdout.splitlines()[0] if ffmpeg_version.stdout else "unknown"
    codec_rows = parse_codec_rows(codecs.stdout)
    encoder_presence = {
        "vp6f": has_encoder(encoders.stdout, "vp6f"),
        "vp6a": has_encoder(encoders.stdout, "vp6a"),
        "vp6": has_encoder(encoders.stdout, "vp6"),
        "libxvp56": has_encoder(encoders.stdout, "libxvp56"),
    }

    project_root = Path(__file__).resolve().parents[1]
    md_path = project_root / args.output_md
    json_path = project_root / args.output_json
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    evidence = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "ffmpeg_version_line": version_line,
        "codec_rows": codec_rows,
        "encoder_presence": encoder_presence,
        "vp6f_probe_stdout": vp6_probe.stdout,
        "vp6f_probe_stderr": vp6_probe.stderr,
        "upstream_references": UPSTREAM_REFERENCES,
    }
    json_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    report = build_markdown_report(
        ffmpeg_version_line=version_line,
        codec_rows=codec_rows,
        encoder_presence=encoder_presence,
        encoder_probe_output=(vp6_probe.stdout + "\n" + vp6_probe.stderr).strip(),
        json_output_path=json_path.relative_to(project_root),
    )
    md_path.write_text(report, encoding="utf-8")

    print(f"Wrote VP56 testimony markdown: {md_path}")
    print(f"Wrote VP56 testimony JSON: {json_path}")


if __name__ == "__main__":
    main()
