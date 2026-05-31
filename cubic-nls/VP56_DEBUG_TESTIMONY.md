# VP56 Debug Testimony (Agentic NLS Blockcode)

This testimony records the first debug pass for VP56/libxVP56 support in the
cubic-nls integration branch.

## What was checked

Commands used:

- `ffmpeg -hide_banner -encoders | rg "vp56|vp6|vp5|h264|libx"`
- `ffmpeg -hide_banner -codecs | rg "vp5|vp6|vp6a|vp6f|vp56"`
- `ffmpeg -hide_banner -h encoder=vp6f`
- `python3 scripts/debug_ffmpeg_vp56_testimony.py`
- `python3 scripts/export_visual_music_video.py --duration 5 --mode vp56-bridge`

## Findings

1. `libx264` encoders are available and MP4/H.264 output works.
2. VP56 family codecs (`vp5`, `vp6`, `vp6a`, `vp6f`) are present as **decode-only**.
3. No VP56 encoder is present in this FFmpeg build:
   - `vp6f` encoder: unavailable
   - `libxvp56` encoder: unavailable
4. Forcing `--mode vp56-bridge` now falls back to H.264 mode with an explicit
   debug hint and still produces valid MP4 output.

## Upstream FFmpeg source references

- https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/vp56.c
- https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/vp56.h
- https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/vp6.c
- https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/allcodecs.c
- https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/general_contents.texi

## Conclusion

The requested label `libxVP56` does not correspond to an available encoder in
the current FFmpeg build/environment. The reliable production path remains:

- render with `agentic-nls-blockcode` + exporter script
- encode final `.mp4` using `libx264`

If true VP56 bridge output is required, a custom FFmpeg build that exposes a
VP56 encoder is needed before enabling that path.

## VP9/vp09 compatibility check

A parallel path is now available in the exporter:

- `--mode vp9-vp09` to encode with `libvpx-vp9`
- `-tag:v vp09` applied automatically for MP4 stream signaling
- `--truncation-safe` for fragmented MP4 output when streams may be truncated
