#include "vp56_community.h"

#include <assert.h>
#include <string.h>

static void test_parser(void) {
  vp56_codec_id codec = VP56_CODEC_UNKNOWN;
  assert(vp56_parse_codec_name("libxVP56", &codec) == 0);
  assert(codec == VP56_CODEC_VP6F);

  assert(vp56_parse_codec_name("vp09", &codec) == 0);
  assert(codec == VP56_CODEC_VP09);

  assert(vp56_parse_codec_name("VP9", &codec) == 0);
  assert(codec == VP56_CODEC_VP9);
}

static void test_vp56_to_vp09_reinterpret(void) {
  vp56_request req;
  vp56_strategy out;

  req.requested_codec = "libxVP56";
  req.vp56_encoder_available = 0;
  req.vp9_encoder_available = 1;
  req.truncation_safe = 1;

  assert(vp56_resolve_export_strategy(&req, &out) == 0);
  assert(out.strategy == VP56_STRATEGY_VP09_DIRECT);
  assert(strcmp(out.primary_encoder, "libvpx-vp9") == 0);
  assert(strcmp(out.mp4_video_tag, "vp09") == 0);
  assert(strstr(out.movflags, "frag_keyframe") != NULL);
}

static void test_vp56_bridge(void) {
  vp56_request req;
  vp56_strategy out;

  req.requested_codec = "vp6f";
  req.vp56_encoder_available = 1;
  req.vp9_encoder_available = 1;
  req.truncation_safe = 0;

  assert(vp56_resolve_export_strategy(&req, &out) == 0);
  assert(out.strategy == VP56_STRATEGY_VP56_BRIDGE);
  assert(strcmp(out.primary_encoder, "vp6f") == 0);
  assert(strcmp(out.secondary_encoder, "libx264") == 0);
  assert(strcmp(out.movflags, "+faststart") == 0);
}

int main(void) {
  test_parser();
  test_vp56_to_vp09_reinterpret();
  test_vp56_bridge();
  return 0;
}
