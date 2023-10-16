idf_component_register(SRCS "utils.cpp"
                       INCLUDE_DIRS "include"
                       REQUIRES esp_event esp_wifi nvs_flash esp_timer 
                       )
