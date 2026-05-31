cmake_minimum_required(VERSION 3.16)
project(vp56_community_lib C)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

add_library(vp56_community STATIC
  src/vp56_community.c
)
target_include_directories(vp56_community PUBLIC include)

add_executable(vp56_probe_demo tools/vp56_probe_demo.c)
target_link_libraries(vp56_probe_demo PRIVATE vp56_community)
target_include_directories(vp56_probe_demo PRIVATE include)

add_executable(vp56_community_tests tests/test_vp56_community.c)
target_link_libraries(vp56_community_tests PRIVATE vp56_community)
target_include_directories(vp56_community_tests PRIVATE include)

enable_testing()
add_test(NAME vp56_community_tests COMMAND vp56_community_tests)
