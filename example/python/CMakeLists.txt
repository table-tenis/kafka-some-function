cmake_minimum_required(VERSION 3.5)
project(producer)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall -pthread")
set(CMAKE_CXX_STANDARD 17)
find_package(spdlog REQUIRED)
include_directories(${PROJECT_SOURCE_DIR})

file(GLOB SOURCES ${PROJECT_SOURCE_DIR}/producer.cpp)


add_executable(${PROJECT_NAME} ${SOURCES})

target_include_directories(${PROJECT_NAME} PUBLIC /usr/include/librdkafka)
add_library(rdkafka SHARED IMPORTED)
set_target_properties(rdkafka PROPERTIES IMPORTED_LOCATION "/usr/lib/x86_64-linux-gnu/librdkafka++.so")
target_link_libraries(${PROJECT_NAME} rdkafka)
# target_link_libraries(${PROJECT_NAME} -lrdkafka)