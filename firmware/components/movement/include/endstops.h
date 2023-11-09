
#ifndef ENDSTOPS_H
#define ENDSTOPS_H

#include <stdint.h>

#include <cstdint>

#include "utils.h"

#ifdef ESP_PLATFORM
#include "driver/mcpwm_prelude.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#endif

class EndStop {
   protected:
    int8_t pin;
    char* name = nullptr;

   public:
    EndStop(int8_t pin);
    EndStop(int8_t pin, const char* name);
    void print_state();
    virtual ~EndStop();
    virtual void hardware_setup() = 0;
    virtual bool hardware_read_state() = 0;
};

class HallEffectSensor : public EndStop {
   private:
   public:
    HallEffectSensor(int8_t pin);
    ~HallEffectSensor();
    void hardware_setup() override;
    bool hardware_read_state() override;
};

class DummyEndStop : public EndStop {
   private:
    float* current_angle = nullptr;

   public:
    DummyEndStop(int8_t pin, float* current_angle);
    ~DummyEndStop();
    void hardware_setup() override;
    bool hardware_read_state() override;
};

class NoneEndStop : public EndStop {
   private:
   public:
    NoneEndStop();
    ~NoneEndStop();
    void hardware_setup() override;
    bool hardware_read_state() override;
};

#endif
