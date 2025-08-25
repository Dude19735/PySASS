cmake_minimum_required(VERSION 3.23)
set(CMAKE_CUDA_COMPILER "/usr/local/cuda/bin/nvcc")
project(kernel LANGUAGES C CXX CUDA)

# 1650 => 75, 3080 => 87
set(TARGET_PATH "/../benchmark_binaries/")

find_package(CUDAToolkit REQUIRED)
set(RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")
set(LIBRARY_OUTPUT_PATH  "${CMAKE_BINARY_DIR}")

include_directories("/usr/local/cuda-12.8/include" "/usr/include")
add_subdirectory(src)
add_subdirectory(tests)

# set(kernel_archs "50" "52" "53" "60" "61" "62" "70")
set(kernel_archs "72" "75" "80" "86" "90" "100" "120")

# This loop builds the binaries for template_3600k
foreach(k ${kernel_archs})
   message("===== ${k} =====")

   set(nn "template_3600k_${k}.bin")
   add_executable(${nn} src/template_3600k.cu)
   target_link_libraries(${nn} CUDA::cudart)
   target_link_libraries(${nn} CUDA::cuda_driver)
   set_property(TARGET ${nn} PROPERTY CUDA_ARCHITECTURES ${k})
   set_property(TARGET ${nn} PROPERTY CXX_STANDARD 20)
   add_custom_command(
        TARGET ${nn} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
                ${CMAKE_CURRENT_BINARY_DIR}/${nn}
                ${CMAKE_CURRENT_BINARY_DIR}${TARGET_PATH}${nn})
endforeach()