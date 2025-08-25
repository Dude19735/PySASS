cmake_minimum_required (VERSION 3.22)

set(MODULE_NAME_1 "_sass_values")
set(MODULE_NAME_2 "_cpp_faster")
set(PROJECT_NAME "py_sass_ext")
project (${PROJECT_NAME} LANGUAGES CXX)

if (NOT SKBUILD)
  set(CMAKE_CXX_STANDARD 23)
  set(CMAKE_CXX_STANDARD_REQUIRED YES)

  # src: https://nanobind.readthedocs.io/en/latest/building.html
  set(DEV_MODULE Development.Module)
  set(PYTHON_VERSION 3.12)
  find_package(Python ${PYTHON_VERSION} COMPONENTS Interpreter ${DEV_MODULE} REQUIRED)
  find_package(OpenMP REQUIRED)

  if (NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "MinSizeRel" "RelWithDebInfo")
  endif()

  add_compile_options(-std=c++23 -fopenmp)
  add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../nanobind ${CMAKE_BINARY_DIR}/nanobind)
  add_subdirectory(src)
  add_subdirectory(tests)
  # include_directories(${Python_INCLUDE_DIRS})
  # message("======================== ${Python_INCLUDE_DIRS}")

  ##########################################################################################################
  # build modules
  add_executable(test tests/tests.cpp)
  target_compile_definitions(test PRIVATE $<$<CONFIG:Debug>:_DEBUG=1>) # this actually works (adds _DEBUG=1 if the setting is debug mode)
  target_include_directories(test PRIVATE Python)

  add_executable(utils_tests tests/utils_tests.cpp)
  target_compile_definitions(test PRIVATE $<$<CONFIG:Debug>:_DEBUG=1>) # this actually works (adds _DEBUG=1 if the setting is debug mode)

  add_executable(to_vector tests/to_vector.cpp)
  target_compile_definitions(to_vector PRIVATE $<$<CONFIG:Debug>:_DEBUG=1>) # this actually works (adds _DEBUG=1 if the setting is debug mode)

  add_executable(mod2_test tests/mod2_tests.cpp)
  target_compile_definitions(mod2_test PRIVATE $<$<CONFIG:Debug>:_DEBUG=1>) # this actually works (adds _DEBUG=1 if the setting is debug mode)
  target_include_directories(mod2_test PRIVATE Python)
  target_include_directories(mod2_test PRIVATE external/nanobind/include)

  add_executable(so src/so.cpp)
  target_compile_definitions(so PRIVATE $<$<CONFIG:Debug>:_DEBUG=1>) # this actually works (adds _DEBUG=1 if the setting is debug mode)
  target_include_directories(so PRIVATE Python)

  add_executable(enc_dom tests/enc_dom.cpp external/lz4/lz4.cpp)
  target_compile_definitions(enc_dom PRIVATE $<$<CONFIG:Debug>:_DEBUG=1>) # this actually works (adds _DEBUG=1 if the setting is debug mode)
  target_include_directories(enc_dom PRIVATE Python)
  target_include_directories(enc_dom PRIVATE external/nanobind/include)
  target_link_libraries(enc_dom PRIVATE OpenMP::OpenMP_CXX)

  nanobind_add_module("${MODULE_NAME_1}" NOMINSIZE LTO src/module_main_1.cpp external/lz4/lz4.cpp)
  target_include_directories("${MODULE_NAME_1}" PRIVATE Python)
  target_link_libraries("${MODULE_NAME_1}" PRIVATE OpenMP::OpenMP_CXX)

  nanobind_add_module("${MODULE_NAME_2}" NOMINSIZE LTO src/module_main_2.cpp)
  target_include_directories("${MODULE_NAME_2}" PRIVATE Python)
else()
  set(CMAKE_CXX_STANDARD 23)
  set(CMAKE_CXX_STANDARD_REQUIRED YES)

  # https://nanobind.readthedocs.io/en/latest/packaging.html
  # Try to import all Python components potentially needed by nanobind
  find_package(Python 3.12 
    REQUIRED COMPONENTS Interpreter Development.Module
    OPTIONAL_COMPONENTS Development.SABIModule)

  # Import nanobind through CMake's find_package mechanism
  find_package(nanobind CONFIG REQUIRED)

  # Other requirements
  find_package(OpenMP REQUIRED)
  if(OpenMP_FOUND)
      set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
      set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
  endif()

  # We are now ready to compile the actual extension module
  nanobind_add_module("${MODULE_NAME_1}" STABLE_ABI NOMINSIZE LTO src/module_main_1.cpp external/lz4/lz4.cpp)
  nanobind_add_stub(
    "${MODULE_NAME_1}_stub"
    MODULE "${MODULE_NAME_1}"
    OUTPUT "${MODULE_NAME_1}.pyi"
    PYTHON_PATH $<TARGET_FILE_DIR:${MODULE_NAME_1}>
    DEPENDS "${MODULE_NAME_1}"
    MARKER_FILE py.typed
  )

  nanobind_add_module("${MODULE_NAME_2}" STABLE_ABI LTO src/module_main_2.cpp)
  nanobind_add_stub(
    "${MODULE_NAME_2}_stub"
    MODULE "${MODULE_NAME_2}"
    OUTPUT "${MODULE_NAME_2}.pyi"
    PYTHON_PATH $<TARGET_FILE_DIR:${MODULE_NAME_2}>
    DEPENDS "${MODULE_NAME_2}"
  )

  # Install directive for scikit-build-core
  install(TARGETS "${MODULE_NAME_1}" LIBRARY DESTINATION ${PROJECT_NAME})
  install(TARGETS "${MODULE_NAME_2}" LIBRARY DESTINATION ${PROJECT_NAME})
  install(
    FILES 
      "${CMAKE_BINARY_DIR}/${MODULE_NAME_1}.pyi" 
      "${CMAKE_BINARY_DIR}/${MODULE_NAME_2}.pyi" 
      "${CMAKE_BINARY_DIR}/py.typed" 
    DESTINATION ${PROJECT_NAME})

endif()
