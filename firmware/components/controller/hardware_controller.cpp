
#include "controller.h"

#ifdef ESP_PLATFORM

static EventGroupHandle_t s_wifi_event_group;

#define WIFI_CONNECTED_BIT BIT0
#define WIFI_FAIL_BIT BIT1

static const char* TAG = "wifi station";

static int s_retry_num = 0;

static void event_handler(void* arg, esp_event_base_t event_base,
                          int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (event_base == WIFI_EVENT &&
               event_id == WIFI_EVENT_STA_DISCONNECTED) {
        if (s_retry_num < 10) {
            esp_wifi_connect();
            s_retry_num++;
            ESP_LOGI(TAG, "retry to connect to the AP");
        } else {
            xEventGroupSetBits(s_wifi_event_group, WIFI_FAIL_BIT);
        }
        ESP_LOGI(TAG, "connect to the AP fail");
    } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*)event_data;
        ESP_LOGI(TAG, "got ip:" IPSTR, IP2STR(&event->ip_info.ip));
        s_retry_num = 0;
        xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
    }
}

void wifi_init_sta(void) {
    s_wifi_event_group = xEventGroupCreate();

    ESP_ERROR_CHECK(esp_netif_init());

    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));

    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        WIFI_EVENT, ESP_EVENT_ANY_ID, &event_handler, NULL, &instance_any_id));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(
        IP_EVENT, IP_EVENT_STA_GOT_IP, &event_handler, NULL, &instance_got_ip));

    wifi_config_t wifi_config;
    memset(&wifi_config, 0, sizeof(wifi_config_t));

    // Set the specific fields
    strcpy((char*)wifi_config.sta.ssid, WIFI_SSID);
    strcpy((char*)wifi_config.sta.password, WIFI_PASSWORD);
    wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;
    wifi_config.sta.pmf_cfg.capable = true;
    wifi_config.sta.pmf_cfg.required = false;
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());

    ESP_LOGI(TAG, "wifi_init_sta finished.");

    EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group,
                                           WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
                                           pdFALSE, pdFALSE, portMAX_DELAY);

    if (bits & WIFI_CONNECTED_BIT) {
        ESP_LOGI(TAG, "connected to ap SSID:%s password:%s", WIFI_SSID,
                 WIFI_PASSWORD);
    } else if (bits & WIFI_FAIL_BIT) {
        ESP_LOGI(TAG, "Failed to connect to SSID:%s, password:%s", WIFI_SSID,
                 WIFI_PASSWORD);
    } else {
        ESP_LOGE(TAG, "UNEXPECTED EVENT");
    }

    ESP_ERROR_CHECK(esp_event_handler_instance_unregister(
        IP_EVENT, IP_EVENT_STA_GOT_IP, instance_got_ip));
    ESP_ERROR_CHECK(esp_event_handler_instance_unregister(
        WIFI_EVENT, ESP_EVENT_ANY_ID, instance_any_id));
    vEventGroupDelete(s_wifi_event_group);
}

void nvs_init() {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES ||
        ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
}

bool Controller::hardware_setup() {
    std::cout << "Setting up hardware" << std::endl;
    nvs_init();
    wifi_init_sta();

    return true;
}

void run_delay(uint32_t delay_ms) { vTaskDelay(pdMS_TO_TICKS(delay_ms)); }

uint64_t get_current_time_microseconds() {
    TickType_t ticks = xTaskGetTickCount();
    return static_cast<uint64_t>(ticks) * (1000000 / configTICK_RATE_HZ);
}

bool Joint::hardware_step(uint8_t step_dir) {
    gpio_set_level(static_cast<gpio_num_t>(this->dir_pin), step_dir);
    gpio_set_level(static_cast<gpio_num_t>(this->step_pin), 1);
    ets_delay_us(this->min_pulse_width);
    gpio_set_level(static_cast<gpio_num_t>(this->step_pin), 0);
    return true;
}

bool Joint::hardware_end_stop_read() {
    // In a real implementation this would be a digital read

    if (std::abs(this->current_angle - this->homing_offset) < 0.1) {
        return true;
    }
    return false;
}

void Controller::step_target_fun() {
    // Add this task to the task watchdog
    esp_task_wdt_add(NULL);

    while (this->stop_flag == false) {
        esp_task_wdt_reset();
        this->step();
        // Feed the task watchdog
        esp_task_wdt_reset();
        run_delay(10);
    }
    esp_task_wdt_delete(NULL);
}
// Static member function
static void step_target_fun_adapter(void* pvParameters) {
    Controller* instance = static_cast<Controller*>(pvParameters);
    instance->step_target_fun();
}

void Controller::run_step_task() {
    xTaskCreate(&step_target_fun_adapter, "step_task", 2048, this,
                configMAX_PRIORITIES - 1, NULL);
}

void task_add() { esp_task_wdt_add(NULL); }

void task_feed() { esp_task_wdt_reset(); }

void task_end() { esp_task_wdt_delete(NULL); }

void Controller::stop_step_task() {}
#else

void task_add() {}

void task_feed() {}

void task_end() {}

bool Controller::hardware_setup() {
    std::cout << "Setting up hardware" << std::endl;
    return true;
}

bool Joint::hardware_step(uint8_t step_dir) { return step_dir < 100; }
bool Joint::hardware_end_stop_read() {
    // In a real implementation this would be a digital read

    if (std::abs(this->current_angle - this->homing_offset) < 0.1) {
        return true;
    }
    return false;
}
void run_delay(uint32_t delay_ms) {
    std::this_thread::sleep_for(std::chrono::milliseconds(delay_ms));
}

uint64_t get_current_time_microseconds() {
    auto now = std::chrono::system_clock::now().time_since_epoch();
    return std::chrono::duration_cast<std::chrono::microseconds>(now).count();
}

void Controller::step_target_fun() {
    while (this->stop_flag == false) {
        this->step();
    }
}

void Controller::run_step_task() {
    this->step_thread =new  std::thread(&Controller::step_target_fun, this);
    this->step_thread->detach();
}

void Controller::stop_step_task() { this->step_thread->join(); }
#endif
