cmake_minimum_required(VERSION 3.16)
project(ecu C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

add_library(ecu SHARED
    src/ecu.c
    src/idle.c
    src/fuel_cut.c
    src/ect_diag.c
    src/shift.c)
target_include_directories(ecu PUBLIC include)
target_compile_options(ecu PRIVATE -Wall -Wextra -Werror)
