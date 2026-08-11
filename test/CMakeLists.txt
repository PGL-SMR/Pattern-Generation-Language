cmake_minimum_required(VERSION 3.12)

project (dot)

file (GLOB_RECURSE test_SOURCES CONFIGURE_DEPENDS "${CMAKE_PROJECT_NAME}/*.c")
file (GLOB_RECURSE test_HEADERS CONFIGURE_DEPENDS "${CMAKE_PROJECT_NAME}/*.h")

set (test_INCLUDE_DIRS "")
foreach (_headerFile ${test_HEADERS})
    get_filename_component(_dir ${_headerFile} PATH)
    list (APPEND test_INCLUDE_DIRS ${_dir})
endforeach()
list (REMOVE_DUPLICATES test_INCLUDE_DIRS)

add_executable(test_${CMAKE_PROJECT_NAME} test_${CMAKE_PROJECT_NAME}.c ${test_SOURCES})
target_include_directories(test_${CMAKE_PROJECT_NAME} PRIVATE ${test_INCLUDE_DIRS})