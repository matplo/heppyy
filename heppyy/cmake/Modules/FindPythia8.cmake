# - Find CGAL
# Find the PYTHIA8 includes and client library
# This module defines
#  PYTHIA8_INCLUDE_DIR, where to find PseudoJet.hh
#  PYTHIA8_LIBRARIES, the libraries needed to use CGAL.
#  PYTHIA8_FOUND, If false, do not try to use CGAL.

if (NOT PYTHIA8_DIR)
  find_program ( PYTHIA8CONFIG pythia8-config PATHS $ENV{PYTHIA8_DIR}/bin ${PYTHIA8_DIR}/bin)
  if (NOT EXISTS ${PYTHIA8CONFIG})
    set(PYTHIA8_DIR "${CMAKE_HEPPY_DIR}/external/pythia8/pythia8-current")
    message(STATUS "Setting PYTHIA8_DIR to ${PYTHIA8_DIR}")
  endif(NOT EXISTS ${PYTHIA8CONFIG})
endif(NOT PYTHIA8_DIR)

if(PYTHIA8_INCLUDE_DIR AND PYTHIA8_LIBRARIES)
   set(PYTHIA8_FOUND TRUE)
else(PYTHIA8_INCLUDE_DIR AND PYTHIA8_LIBRARIES)
  message(STATUS "Looking for Pythia8 with pythia8-config...")
  find_program ( PYTHIA8CONFIG pythia8-config PATHS $ENV{PYTHIA8_DIR}/bin ${PYTHIA8_DIR}/bin)
  if (EXISTS ${PYTHIA8CONFIG})
    message(STATUS "Using pythia8-config at ${PYTHIA8CONFIG}")
    execute_process ( COMMAND ${PYTHIA8CONFIG} --prefix WORKING_DIRECTORY /tmp OUTPUT_VARIABLE PYTHIA8_DIR OUTPUT_STRIP_TRAILING_WHITESPACE )
    execute_process ( COMMAND ${PYTHIA8CONFIG} --cxxflags WORKING_DIRECTORY /tmp OUTPUT_VARIABLE PYTHIA8_CXXFLAGS OUTPUT_STRIP_TRAILING_WHITESPACE )

    # Convert string to list (this is crucial!)
    separate_arguments(PYTHIA8_CXXFLAGS)

    execute_process ( COMMAND ${PYTHIA8CONFIG} --ldflags WORKING_DIRECTORY /tmp OUTPUT_VARIABLE PYTHIA8_LDFLAGS OUTPUT_STRIP_TRAILING_WHITESPACE )
    execute_process ( COMMAND ${PYTHIA8CONFIG} --includedir WORKING_DIRECTORY /tmp OUTPUT_VARIABLE PYTHIA8_INCLUDE_DIR OUTPUT_STRIP_TRAILING_WHITESPACE )
    set(PYTHIA8_LIBRARIES ${PYTHIA8_LDFLAGS})
    # set(PYTHIA8_INCLUDE_DIR ${PYTHIA8_CXXFLAGS})
  else()
    message(STATUS "${Yellow}Pythia8 search requires pythia8-config in \$PATH${ColourReset}")
  endif()
  get_filename_component(PYTHIA8_DIR ${PYTHIA8_INCLUDE_DIR} DIRECTORY)
  string(REPLACE "-I" "" PYTHIA8_DIR ${PYTHIA8_DIR})
  mark_as_advanced(PYTHIA8_INCLUDE_DIR PYTHIA8_LIBRARIES PYTHIA8_DIR)
endif(PYTHIA8_INCLUDE_DIR AND PYTHIA8_LIBRARIES)

include(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(Pythia8 DEFAULT_MSG PYTHIA8_DIR PYTHIA8_INCLUDE_DIR PYTHIA8_LIBRARIES)

if(NOT PYTHIA8_FOUND)
  message(STATUS "${Yellow}Pythia8 not found - some of the functionality will be missing.${ColourReset}")
elseif(PYTHIA8_FOUND)
  message(STATUS "Found Pythia8: ${PYTHIA8_DIR}")
  message(STATUS "Pythia8 include directory: ${PYTHIA8_INCLUDE_DIR}")
  message(STATUS "Pythia8 libraries: ${PYTHIA8_LIBRARIES}")
  message(STATUS "Pythia8 cxxflags: ${PYTHIA8_CXXFLAGS}")
  set(PYTHIA8_INCLUDE_DIRS ${PYTHIA8_INCLUDE_DIR})
  set(PYTHIA8_LIBRARIES ${PYTHIA8_LIBRARIES})
  set(PYTHIA8_CXX_FLAGS ${PYTHIA8_CXXFLAGS})
  mark_as_advanced(PYTHIA8_INCLUDE_DIRS PYTHIA8_LIBRARIES PYTHIA8_CXX_FLAGS)
endif(NOT PYTHIA8_FOUND)
