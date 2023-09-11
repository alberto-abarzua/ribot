idf_component_register(SRCS "controller.cpp" "joint.cpp" "tool.cpp"
                       INCLUDE_DIRS "include"
                       REQUIRES arm_client esp_event esp_wifi nvs_flash driver esp_timer utils movement
                       )