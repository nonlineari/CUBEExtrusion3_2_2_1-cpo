#include "vp56_community.h"

#include <ctype.h>
#include <stdio.h>
#include <string.h>

static void copy_text(char *dst, size_t size, const char *src) {
  if (!dst || size == 0) {
    return;
  }
  if (!src) {
    dst[0] = '\0';
    return;
  }
  snprintf(dst, size, "%s", src);
}

static int contains_token(const char *input, const char *token) {
  size_t i = 0;
  size_t j = 0;
  char sanitized[96];
  char token_sanitized[32];

  if (!input || !token) {
    return 0;
  }

  for (i = 0; input[i] != '\0' && j < sizeof(sanitized) - 1; i++) {
    if (isalnum((unsigned char)input[i])) {
      sanitized[j++] = (char)tolower((unsigned char)input[i]);
    }
  }
  sanitized[j] = '\0';

  j = 0;
  for (i = 0; token[i] != '\0' && j < sizeof(token_sanitized) - 1; i++) {
    if (isalnum((unsigned char)token[i])) {
      token_sanitized[j++] = (char)tolower((unsigned char)token[i]);
    }
  }
  token_sanitized[j] = '\0';

  if (token_sanitized[0] == '\0') {
    return 0;
  }
  return strstr(sanitized, token_sanitized) != NULL;
}

int vp56_parse_codec_name(const char *value, vp56_codec_id *out_codec) {
  if (!out_codec) {
    return -1;
  }

  *out_codec = VP56_CODEC_UNKNOWN;
  if (!value || value[0] == '\0') {
    return 0;
  }

  if (contains_token(value, "vp09")) {
    *out_codec = VP56_CODEC_VP09;
  } else if (contains_token(value, "vp9")) {
    *out_codec = VP56_CODEC_VP9;
  } else if (contains_token(value, "vp6a")) {
    *out_codec = VP56_CODEC_VP6A;
  } else if (contains_token(value, "vp6f")) {
    *out_codec = VP56_CODEC_VP6F;
  } else if (contains_token(value, "vp6")) {
    *out_codec = VP56_CODEC_VP6;
  } else if (contains_token(value, "vp5")) {
    *out_codec = VP56_CODEC_VP5;
  } else if (contains_token(value, "vp56") || contains_token(value, "libxvp56")) {
    *out_codec = VP56_CODEC_VP6F;
  } else {
    *out_codec = VP56_CODEC_UNKNOWN;
  }
  return 0;
}

int vp56_is_family_codec(vp56_codec_id codec) {
  return codec == VP56_CODEC_VP5 || codec == VP56_CODEC_VP6 ||
         codec == VP56_CODEC_VP6A || codec == VP56_CODEC_VP6F;
}

const char *vp56_codec_name(vp56_codec_id codec) {
  switch (codec) {
  case VP56_CODEC_VP5:
    return "vp5";
  case VP56_CODEC_VP6:
    return "vp6";
  case VP56_CODEC_VP6A:
    return "vp6a";
  case VP56_CODEC_VP6F:
    return "vp6f";
  case VP56_CODEC_VP9:
    return "vp9";
  case VP56_CODEC_VP09:
    return "vp09";
  default:
    return "unknown";
  }
}

const char *vp56_strategy_name(vp56_strategy_id strategy) {
  switch (strategy) {
  case VP56_STRATEGY_VP56_BRIDGE:
    return "vp56-bridge";
  case VP56_STRATEGY_VP09_DIRECT:
    return "vp09-direct";
  default:
    return "h264-direct";
  }
}

static void set_movflags(vp56_strategy *strategy, int truncation_safe) {
  if (truncation_safe) {
    copy_text(strategy->movflags, sizeof(strategy->movflags),
              "+faststart+frag_keyframe+empty_moov+default_base_moof");
  } else {
    copy_text(strategy->movflags, sizeof(strategy->movflags), "+faststart");
  }
}

int vp56_resolve_export_strategy(const vp56_request *request,
                                 vp56_strategy *strategy) {
  vp56_codec_id parsed_codec = VP56_CODEC_UNKNOWN;
  int vp56_available = 0;
  int vp9_available = 0;
  int truncation_safe = 0;

  if (!request || !strategy) {
    return -1;
  }

  vp56_parse_codec_name(request->requested_codec, &parsed_codec);
  vp56_available = request->vp56_encoder_available != 0;
  vp9_available = request->vp9_encoder_available != 0;
  truncation_safe = request->truncation_safe != 0;

  memset(strategy, 0, sizeof(*strategy));
  strategy->parsed_codec = parsed_codec;

  if (vp56_is_family_codec(parsed_codec)) {
    if (vp56_available) {
      strategy->strategy = VP56_STRATEGY_VP56_BRIDGE;
      copy_text(strategy->primary_encoder, sizeof(strategy->primary_encoder), "vp6f");
      copy_text(strategy->secondary_encoder, sizeof(strategy->secondary_encoder),
                "libx264");
      copy_text(strategy->mp4_video_tag, sizeof(strategy->mp4_video_tag), "avc1");
      copy_text(strategy->rationale, sizeof(strategy->rationale),
                "VP56 request with encoder available: using vp6f bridge then H.264 "
                "for MP4 interoperability.");
    } else if (vp9_available) {
      strategy->strategy = VP56_STRATEGY_VP09_DIRECT;
      copy_text(strategy->primary_encoder, sizeof(strategy->primary_encoder),
                "libvpx-vp9");
      copy_text(strategy->mp4_video_tag, sizeof(strategy->mp4_video_tag), "vp09");
      copy_text(strategy->rationale, sizeof(strategy->rationale),
                "VP56 requested but encoder unavailable: reinterpreting to VP9 with "
                "vp09 tag for cross-platform gatekeepers.");
    } else {
      strategy->strategy = VP56_STRATEGY_H264_DIRECT;
      copy_text(strategy->primary_encoder, sizeof(strategy->primary_encoder),
                "libx264");
      copy_text(strategy->mp4_video_tag, sizeof(strategy->mp4_video_tag), "avc1");
      copy_text(strategy->rationale, sizeof(strategy->rationale),
                "VP56 requested but unavailable and no VP9 encoder: fallback to "
                "H.264 MP4.");
    }
  } else if (parsed_codec == VP56_CODEC_VP9 || parsed_codec == VP56_CODEC_VP09) {
    if (vp9_available) {
      strategy->strategy = VP56_STRATEGY_VP09_DIRECT;
      copy_text(strategy->primary_encoder, sizeof(strategy->primary_encoder),
                "libvpx-vp9");
      copy_text(strategy->mp4_video_tag, sizeof(strategy->mp4_video_tag), "vp09");
      copy_text(strategy->rationale, sizeof(strategy->rationale),
                "VP9/vp09 request with encoder available.");
    } else {
      strategy->strategy = VP56_STRATEGY_H264_DIRECT;
      copy_text(strategy->primary_encoder, sizeof(strategy->primary_encoder),
                "libx264");
      copy_text(strategy->mp4_video_tag, sizeof(strategy->mp4_video_tag), "avc1");
      copy_text(strategy->rationale, sizeof(strategy->rationale),
                "VP9 requested but encoder unavailable: fallback to H.264 MP4.");
    }
  } else {
    strategy->strategy = VP56_STRATEGY_H264_DIRECT;
    copy_text(strategy->primary_encoder, sizeof(strategy->primary_encoder), "libx264");
    copy_text(strategy->mp4_video_tag, sizeof(strategy->mp4_video_tag), "avc1");
    copy_text(strategy->rationale, sizeof(strategy->rationale),
              "No VP56/VP9 token found: default H.264 MP4 strategy.");
  }

  set_movflags(strategy, truncation_safe);
  return 0;
}
