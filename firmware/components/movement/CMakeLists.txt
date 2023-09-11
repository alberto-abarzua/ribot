idf_component_register(SRCS "movement.cpp" "servo.cpp" "endstops.cpp" "stepper.cpp"
                       INCLUDE_DIRS "include"
                       REQUIRES utils driver
                       )