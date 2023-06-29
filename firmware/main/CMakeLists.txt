if(DEFINED IDF_TARGET)
    idf_component_register(SRCS "main.cpp" 
    INCLUDE_DIRS "."
    REQUIRES ${requires})
endif()

