# vp56-community-lib

Independent VP56-family strategy library for CUBEEXTRUSION-NLS / agentic-nls-blockcode.

This module was created after VP56 debugging to provide a reusable logic layer
that can be forwarded to FFmpeg community discussions as an RFC-style proposal.

## Goals

- normalize VP56/VP9 token parsing (`vp56`, `libxVP56`, `vp6f`, `vp9`, `vp09`)
- reinterpret VP56 requests into `vp09` mode when VP56 encoder support is missing
- preserve functional defaults for cross-platform gatekeepers
- expose truncation-safe MP4 movflags policy

## API summary

Header: `include/vp56_community.h`

- `vp56_parse_codec_name(...)`
- `vp56_resolve_export_strategy(...)`
- `vp56_codec_name(...)`
- `vp56_strategy_name(...)`

## Build

```bash
cmake -S vp56-community-lib -B vp56-community-lib/build
cmake --build vp56-community-lib/build
ctest --test-dir vp56-community-lib/build --output-on-failure
```

## Demo

```bash
./vp56-community-lib/build/vp56_probe_demo libxVP56 0 1 1
```

Arguments:

1. requested codec string
2. VP56 encoder availability (`0` or `1`)
3. VP9 encoder availability (`0` or `1`)
4. truncation-safe mode (`0` or `1`)

## Upstream review package

See `upstream/FFMPEG_RFC_SUBMISSION.md` for:

- RFC cover-letter template
- pointers to original FFmpeg VP56 sources
- recommended submission route to `ffmpeg-devel`


Core asset handoff note: `CUBEEXTRUSION-NLS/FORMZ_VCODEC_CORE_ASSET.md`.
