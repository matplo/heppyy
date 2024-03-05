add_compile_options(${FASTJET_CXXFLAGS})

set(MODULE_NAME fjext)
set(MODULE ${PROJECT_NAME}_${MODULE_NAME})
set(NAME_LIB ${MODULE})

message(STATUS "${Magenta}Module: ${MODULE}${ColourReset}")

include_directories(${CMAKE_CURRENT_SOURCE_DIR})
file(GLOB SOURCES_LIB ${CMAKE_CURRENT_SOURCE_DIR}/*.cxx)
message(STATUS "SOURCES: ${SOURCES_LIB}")
string(REPLACE ".cxx" ".hh" HEADERS_LIB "${SOURCES_LIB}")

add_library(${NAME_LIB} SHARED ${SOURCES_LIB})

target_include_directories(${NAME_LIB} PUBLIC ${FASTJET_DIR}/include)
target_link_libraries(${NAME_LIB} PUBLIC ${FASTJET_LIBS} -lRecursiveTools -lLundPlane)

install_targets_custom()
