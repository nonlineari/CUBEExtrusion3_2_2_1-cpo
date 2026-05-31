#ifndef VP56_COMMUNITY_H
#define VP56_COMMUNITY_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>

typedef enum vp56_codec_id {
  VP56_CODEC_UNKNOWN = 0,
  VP56_CODEC_VP5,
  VP56_CODEC_VP6,
  VP56_CODEC_VP6A,
  VP56_CODEC_VP6F,
  VP56_CODEC_VP9,
  VP56_CODEC_VP09
} vp56_codec_id;

typedef enum vp56_strategy_id {
  VP56_STRATEGY_H264_DIRECT = 0,
  VP56_STRATEGY_VP09_DIRECT,
  VP56_STRATEGY_VP56_BRIDGE
} vp56_strategy_id;

typedef struct vp56_request {
  const char *requested_codec;
  int vp56_encoder_available;
  int vp9_encoder_available;
  int truncation_safe;
} vp56_request;

typedef struct vp56_strategy {
  vp56_strategy_id strategy;
  vp56_codec_id parsed_codec;
  char primary_encoder[32];
  char secondary_encoder[32];
  char mp4_video_tag[8];
  char movflags[96];
  char rationale[224];
} vp56_strategy;

int vp56_parse_codec_name(const char *value, vp56_codec_id *out_codec);
int vp56_is_family_codec(vp56_codec_id codec);
const char *vp56_codec_name(vp56_codec_id codec);
const char *vp56_strategy_name(vp56_strategy_id strategy);
int vp56_resolve_export_strategy(const vp56_request *request,
                                 vp56_strategy *strategy);

#ifdef __cplusplus
}
#endif

#endif
