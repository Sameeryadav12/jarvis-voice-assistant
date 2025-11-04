cmake_minimum_required(VERSION 3.20)
project(jarvis_native)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Add pybind11
add_subdirectory(pybind11)

# Source files
set(SOURCES
    bindings.cpp
    audio_endpoint.cpp
    windows_focus.cpp
)

# Create Python module
pybind11_add_module(jarvis_native ${SOURCES})

# Windows-specific settings
if(WIN32)
    target_compile_definitions(jarvis_native PRIVATE UNICODE _UNICODE)
    target_link_libraries(jarvis_native PRIVATE 
        ole32 
        oleaut32
        user32
        kernel32
    )
endif()

# Set output directory
set_target_properties(jarvis_native PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/../../../"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/../../../"
)

# Installation
install(TARGETS jarvis_native LIBRARY DESTINATION .)





