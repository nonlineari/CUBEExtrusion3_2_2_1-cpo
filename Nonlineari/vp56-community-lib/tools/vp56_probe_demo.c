#include "vp56_community.h"

#include <stdio.h>

int main(int argc, char **argv) {
  vp56_request request;
  vp56_strategy strategy;
  const char *codec = argc > 1 ? argv[1] : "libxVP56";
  int vp56_available = argc > 2 ? (argv[2][0] == '1') : 0;
  int vp9_available = argc > 3 ? (argv[3][0] == '1') : 1;
  int trunc_safe = argc > 4 ? (argv[4][0] == '1') : 1;

  request.requested_codec = codec;
  request.vp56_encoder_available = vp56_available;
  request.vp9_encoder_available = vp9_available;
  request.truncation_safe = trunc_safe;

  if (vp56_resolve_export_strategy(&request, &strategy) != 0) {
    fprintf(stderr, "Failed to resolve strategy.\n");
    return 1;
  }

  printf("requested_codec=%s\n", codec);
  printf("parsed_codec=%s\n", vp56_codec_name(strategy.parsed_codec));
  printf("strategy=%s\n", vp56_strategy_name(strategy.strategy));
  printf("primary_encoder=%s\n", strategy.primary_encoder);
  printf("secondary_encoder=%s\n", strategy.secondary_encoder);
  printf("mp4_video_tag=%s\n", strategy.mp4_video_tag);
  printf("movflags=%s\n", strategy.movflags);
  printf("rationale=%s\n", strategy.rationale);
  return 0;
}
