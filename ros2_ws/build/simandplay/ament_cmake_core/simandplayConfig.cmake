# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_simandplay_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED simandplay_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(simandplay_FOUND FALSE)
  elseif(NOT simandplay_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(simandplay_FOUND FALSE)
  endif()
  return()
endif()
set(_simandplay_CONFIG_INCLUDED TRUE)

# output package information
if(NOT simandplay_FIND_QUIETLY)
  message(STATUS "Found simandplay: 0.1.0 (${simandplay_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'simandplay' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${simandplay_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(simandplay_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${simandplay_DIR}/${_extra}")
endforeach()
