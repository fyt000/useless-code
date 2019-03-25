project(teststuff)

cmake_minimum_required(VERSION 3.11)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_CXX_COMPILER $ENV{CXX})
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "-Wall -Werror -Wextra -Wunreachable-code -Wuninitialized")

set(THREADS_PREFER_PTHREAD_FLAG ON)
set(Boost_USE_STATIC_LIBS ON)

find_package(Boost 1.68.0 REQUIRED COMPONENTS system context coroutine log regex)
find_package(Threads REQUIRED)

file(GLOB SRC_LIST src/*.cpp)

add_executable(test-cpp ${SRC_LIST})

set(LINK_LIBS 
    Boost::system
    Boost::context
    Boost::coroutine
    Boost::log
    Boost::regex
    Threads::Threads)

target_link_libraries(test-cpp ${LINK_LIBS})
