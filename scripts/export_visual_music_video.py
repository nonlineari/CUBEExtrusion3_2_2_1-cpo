#!/usr/bin/env python3
"""
Export a visual-music MP4 from prompt-driven style settings.

This script is designed for the CUBEEXTRUSION-NLS integration branch and can be used
after iterating on prompts in agentic-nls-blockcode.

Features:
- MP4 output with H.264 encoder (libx264)
- optional MP4 output with VP9 encoder using vp09 tag (libvpx-vp9)
- duration presets: 5s or 10s
- optional VP56 bridge mode (vp6f -> h264 mp4) when encoder is available
- truncation-safe fragmented MP4 movflags mode
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


DEFAULT_PROMPT = (
    "Complete a build using a folding neural network left 2 right system inside "
    "a 3 dimensional circular 6sided folding cube with red, white and blue in "
    "black background (0) and visual music rhythm layers."
)

NAMED_COLORS = {
    "red": "#ef4444",
    "white": "#f8fafc",
    "blue": "#3b82f6",
    "black": "#020617",
    "green": "#22c55e",
    "yellow": "#eab308",
    "orange": "#f97316",
    "cyan": "#06b6d4",
    "purple": "#a855f7",
    "magenta": "#d946ef",
}


def run_command(command: list[str]) -> None:
    subprocess.run(command, check=True, text=True)


def ffmpeg_has_encoder(encoder_name: str) -> bool:
    process = subprocess.run(
        ["ffmpeg", "-hide_banner", "-encoders"],
        check=True,
        capture_output=True,
        text=True,
    )
    pattern = re.compile(rf"\b{re.escape(encoder_name)}\b")
    return bool(pattern.search(process.stdout))


def parse_prompt_style(prompt: str) -> dict[str, object]:
    lower = prompt.lower()
    palette: list[str] = []
    for name, hex_color in NAMED_COLORS.items():
        if name != "black" and name in lower:
            palette.append(hex_color)
    if not palette:
        palette = ["#22c55e", "#0ea5e9", "#f97316"]

    return {
        "palette": palette[:3],
        "dark_background": bool(
            re.search(r"black background|dark background|on black", lower)
        ),
        "left_to_right": bool(re.search(r"left\s*(?:to|2)\s*right", lower)),
        "circular": bool(re.search(r"circular|radial|ring", lower)),
        "folding": bool(re.search(r"fold|origami", lower)),
        "cube": bool(re.search(r"cube|box", lower)),
    }


def build_video_filter(style: dict[str, object], duration: int) -> str:
    palette = style["palette"]
    background = "black" if style["dark_background"] else "white"
    grid_color = "white" if background == "black" else "black"
    color_a = palette[0]
    color_b = palette[1] if len(palette) > 1 else palette[0]
    color_c = palette[2] if len(palette) > 2 else palette[0]

    move_a = "mod(t*160\\,w)" if style["left_to_right"] else "w-mod(t*160\\,w)"
    move_b = "w-mod(t*105\\,w)" if style["left_to_right"] else "mod(t*105\\,w)"
    move_c = "mod(t*78\\,w)"

    filters: list[str] = [
        "format=yuv420p",
        f"drawgrid=width=64:height=64:color={grid_color}@0.08:t=1",
        f"drawbox=x={move_a}:y=h*0.18:w=220:h=220:color={color_a}@0.34:t=fill",
        f"drawbox=x={move_b}:y=h*0.44:w=180:h=180:color={color_b}@0.24:t=fill",
        f"drawbox=x={move_c}:y=h*0.68:w=160:h=160:color={color_c}@0.34:t=fill",
    ]

    if style["folding"]:
        filters.append(
            "drawbox=x=(w/2)-120:y=(h/2)-120:w=240:h=240:color=white@0.06:t=2"
        )
        filters.append(
            "drawbox=x=(w/2)-80:y=(h/2)-80:w=160:h=160:color=white@0.08:t=2"
        )

    if style["circular"]:
        filters.append(
            "geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
            "a='if(lt(hypot(X-W/2,Y-H/2),min(W,H)*0.46),255,255)'"
        )

    if style["cube"]:
        filters.append(
            "drawbox=x=(w/2)-180:y=(h/2)-180:w=360:h=360:color=white@0.12:t=2"
        )
        filters.append(
            "drawbox=x=(w/2)-150:y=(h/2)-150:w=300:h=300:color=white@0.12:t=2"
        )

    filters.extend(
        [
            f"rotate='0.02*sin(2*PI*t/{duration})':ow='rotw(iw)':oh='roth(ih)':c={background}",
            "scale=1280:720:flags=lanczos",
            "eq=contrast=1.08:saturation=1.25",
        ]
    )
    return ",".join(filters)


def build_audio_filter() -> str:
    return (
        "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
        "volume=0.22,highpass=f=120,lowpass=f=5600"
    )


def compute_movflags(truncation_safe: bool) -> str:
    if truncation_safe:
        return "+faststart+frag_keyframe+empty_moov+default_base_moof"
    return "+faststart"


def encode_h264(
    output_path: Path,
    duration: int,
    video_filter: str,
    audio_filter: str,
    movflags: str,
) -> None:
    run_command(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=black:s=1280x720:r=30:d={duration}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=220:sample_rate=48000:duration={duration}",
            "-vf",
            video_filter,
            "-af",
            audio_filter,
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            movflags,
            "-shortest",
            str(output_path),
        ]
    )


def encode_vp9_vp09(
    output_path: Path,
    duration: int,
    video_filter: str,
    audio_filter: str,
    movflags: str,
) -> None:
    run_command(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=black:s=1280x720:r=30:d={duration}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=220:sample_rate=48000:duration={duration}",
            "-vf",
            video_filter,
            "-af",
            audio_filter,
            "-c:v",
            "libvpx-vp9",
            "-pix_fmt",
            "yuv420p",
            "-row-mt",
            "1",
            "-tile-columns",
            "1",
            "-frame-parallel",
            "1",
            "-deadline",
            "good",
            "-cpu-used",
            "2",
            "-crf",
            "33",
            "-b:v",
            "0",
            "-tag:v",
            "vp09",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-movflags",
            movflags,
            "-shortest",
            str(output_path),
        ]
    )


def encode_vp56_bridge(
    output_path: Path,
    duration: int,
    video_filter: str,
    audio_filter: str,
    movflags: str,
    keep_intermediate: bool,
) -> None:
    with tempfile.TemporaryDirectory(prefix="cubic_nls_vp56_") as temp_dir:
        temp_flv = Path(temp_dir) / "visual_music_vp56.flv"

        run_command(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=black:s=1280x720:r=30:d={duration}",
                "-vf",
                video_filter,
                "-c:v",
                "vp6f",
                "-b:v",
                "2500k",
                "-an",
                str(temp_flv),
            ]
        )

        run_command(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(temp_flv),
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency=220:sample_rate=48000:duration={duration}",
                "-af",
                audio_filter,
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "160k",
                "-movflags",
                movflags,
                "-shortest",
                str(output_path),
            ]
        )

        if keep_intermediate:
            kept_flv = output_path.with_suffix(".vp56.flv")
            shutil.copy2(temp_flv, kept_flv)
            print(f"Kept VP56 intermediate: {kept_flv}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export visual-music MP4 with 5s/10s presets and codec modes."
    )
    parser.add_argument(
        "--duration",
        type=int,
        choices=[5, 10],
        default=5,
        help="Output duration in seconds.",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "h264", "vp9-vp09", "vp56-bridge"],
        default="auto",
        help=(
            "Encoding mode: direct H264, VP9-vp09 MP4, VP56 bridge, or auto-detect. "
            "Auto keeps H264 default unless VP56 bridge is available."
        ),
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt text used to derive visual style choices.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output MP4 path. Defaults to output/visual_music_<duration>s.mp4",
    )
    parser.add_argument(
        "--keep-intermediate",
        action="store_true",
        help="Keep VP56 intermediate .flv file when using vp56-bridge.",
    )
    parser.add_argument(
        "--truncation-safe",
        action="store_true",
        help="Use fragmented MP4 movflags for better partial/truncated playback behavior.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = (
        args.output
        if args.output is not None
        else output_dir / f"visual_music_{args.duration}s.mp4"
    )

    style = parse_prompt_style(args.prompt)
    video_filter = build_video_filter(style, args.duration)
    audio_filter = build_audio_filter()
    movflags = compute_movflags(args.truncation_safe)

    vp6f_available = ffmpeg_has_encoder("vp6f")
    libxvp56_available = ffmpeg_has_encoder("libxvp56")
    vp9_available = ffmpeg_has_encoder("libvpx-vp9")

    if args.mode == "h264":
        selected_mode = "h264"
    elif args.mode == "vp9-vp09":
        selected_mode = "vp9-vp09"
    elif args.mode == "vp56-bridge":
        selected_mode = "vp56-bridge"
    else:
        selected_mode = "vp56-bridge" if vp6f_available else "h264"

    if selected_mode == "vp56-bridge" and not vp6f_available:
        print("VP56 encoder (vp6f) not available. Falling back to direct H264 mode.")
        print(
            "Run `python3 scripts/debug_ffmpeg_vp56_testimony.py` for a full "
            "diagnostic report and upstream VP56 source references."
        )
        selected_mode = "h264"

    if selected_mode == "vp9-vp09" and not vp9_available:
        print("VP9 encoder (libvpx-vp9) not available. Falling back to direct H264 mode.")
        selected_mode = "h264"

    print(f"Prompt profile mode: {'dark' if style['dark_background'] else 'light'}")
    print(f"Encoding mode: {selected_mode}")
    print(f"vp6f encoder available: {vp6f_available}")
    print(f"libxvp56 encoder available: {libxvp56_available}")
    print(f"libvpx-vp9 encoder available: {vp9_available}")
    print(f"Duration: {args.duration}s")
    print(f"movflags: {movflags}")
    print(f"Output: {output_path}")

    if selected_mode == "vp56-bridge":
        encode_vp56_bridge(
            output_path=output_path,
            duration=args.duration,
            video_filter=video_filter,
            audio_filter=audio_filter,
            movflags=movflags,
            keep_intermediate=args.keep_intermediate,
        )
    elif selected_mode == "vp9-vp09":
        encode_vp9_vp09(
            output_path=output_path,
            duration=args.duration,
            video_filter=video_filter,
            audio_filter=audio_filter,
            movflags=movflags,
        )
    else:
        encode_h264(
            output_path=output_path,
            duration=args.duration,
            video_filter=video_filter,
            audio_filter=audio_filter,
            movflags=movflags,
        )

    print(f"Wrote MP4: {output_path}")


if __name__ == "__main__":
    main()
