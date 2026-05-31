# FFmpeg RFC Submission Bundle (VP56 family strategy layer)

This folder documents how to forward the independent `vp56-community-lib`
concept to FFmpeg maintainers for public review.

## Scope

The proposal is not a direct replacement for FFmpeg codec internals.  
It is an RFC for a strategy/capability abstraction layer that:

1. normalizes VP56-family syntax requests
2. provides deterministic fallback behavior
3. supports `vp09` tag signaling for VP9 MP4 compatibility paths
4. introduces truncation-safe output policy hints

## Why this is useful

- current FFmpeg deployments may expose VP56 decode but not encode
- community tooling often receives ambiguous strings (`libxVP56`, `vp56 family`)
- a small reusable compatibility gate can improve user-facing behavior without
  altering low-level codec correctness

## Upstream source references

- https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/vp56.c
- https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/vp56.h
- https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/vp6.c
- https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/allcodecs.c
- https://github.com/FFmpeg/FFmpeg/blob/master/doc/general_contents.texi

## Suggested submission steps

1. Create an FFmpeg fork and branch (outside this repository).
2. Add an RFC patch series (or discussion patch) referencing this module.
3. Generate a short RFC 0/1 cover letter + patch set:
   - `./vp56-community-lib/upstream/prepare_ffmpeg_rfc_cover.sh HEAD ./rfc-out`
   - this creates:
     - `./rfc-out/0000-*.patch` (cover letter, auto-filled from template)
     - `./rfc-out/0001-*.patch` (your patch)
4. Send RFC to `ffmpeg-devel@ffmpeg.org` with:
   - problem statement
   - compatibility behavior matrix
   - test evidence (including `vp09` tagging and truncation-safe mode)
5. Iterate on maintainer feedback before requesting merge.

Send command:

`git send-email --to=ffmpeg-devel@ffmpeg.org ./rfc-out/0000-*.patch ./rfc-out/0001-*.patch`

## RFC cover letter template

```text
[RFC PATCH 0/1] avcodec: introduce vp56-family capability strategy helper

This RFC proposes a lightweight helper that normalizes ambiguous VP56-family
user requests and resolves deterministic strategy output:
- vp56 bridge path when encoder exists
- vp09 reinterpretation when vp56 encode is unavailable but vp9 exists
- h264 fallback as last-resort interoperable output

The intent is to improve gateway behavior for platform wrappers and truncated
transfer scenarios without altering existing VP56 decode implementations.

References:
- libavcodec/vp56.c
- libavcodec/vp6.c
- libavcodec/allcodecs.c

Feedback requested on:
- API placement (libavcodec helper vs external tool guidance)
- naming and policy defaults
- acceptance criteria for compatibility behavior
```

Short ready-to-use version is available in:

- `vp56-community-lib/upstream/FFMPEG_RFC_0_1_COVERLETTER.txt`

## Notes

- This repository cannot directly push to FFmpeg upstream.
- The package here is a ready-to-forward community review artifact.
