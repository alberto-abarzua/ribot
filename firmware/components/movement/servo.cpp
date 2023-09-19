#include "movement.h"

#ifdef ESP_PLATFORM

static const char *TAG = "example";

// Please consult the datasheet of your servo before changing the following
// parameters
#define SERVO_MIN_PULSEWIDTH_US 500   // Minimum pulse width in microsecond
#define SERVO_MAX_PULSEWIDTH_US 2500  // Maximum pulse width in microsecond
#define SERVO_MIN_DEGREE -90          // Minimum angle
#define SERVO_MAX_DEGREE 90           // Maximum angle

#define SERVO_TIMEBASE_RESOLUTION_HZ 1000000  // 1MHz, 1us per tick
#define SERVO_TIMEBASE_PERIOD 20000           // 20000 ticks, 20ms

void Servo::hardware_setup() {
    ESP_LOGI(TAG, "Create timer and operator");
    mcpwm_timer_handle_t timer = NULL;

    mcpwm_timer_config_t timer_config;
    timer_config.group_id = 0;
    timer_config.clk_src = MCPWM_TIMER_CLK_SRC_DEFAULT;
    timer_config.resolution_hz = SERVO_TIMEBASE_RESOLUTION_HZ;
    timer_config.period_ticks = SERVO_TIMEBASE_PERIOD;
    timer_config.count_mode = MCPWM_TIMER_COUNT_MODE_UP;

    ESP_ERROR_CHECK(mcpwm_new_timer(&timer_config, &timer));

    mcpwm_oper_handle_t oper = NULL;

    mcpwm_operator_config_t operator_config;
    operator_config.group_id =
        0;  // operator must be in the same group to the timer
    ESP_ERROR_CHECK(mcpwm_new_operator(&operator_config, &oper));

    ESP_LOGI(TAG, "Connect timer and operator");
    ESP_ERROR_CHECK(mcpwm_operator_connect_timer(oper, timer));

    ESP_LOGI(TAG, "Create comparator and generator from the operator");
    this->comparator = NULL;
    mcpwm_comparator_config_t comparator_config;
    comparator_config.flags.update_cmp_on_tez = true;

    ESP_ERROR_CHECK(
        mcpwm_new_comparator(oper, &comparator_config, &this->comparator));

    mcpwm_gen_handle_t generator = NULL;
    mcpwm_generator_config_t generator_config;
    generator_config.gen_gpio_num = this->pin;
    ESP_ERROR_CHECK(mcpwm_new_generator(oper, &generator_config, &generator));

    // set the initial compare value, so that the servo will spin to the center
    // position

    ESP_ERROR_CHECK(mcpwm_comparator_set_compare_value(
        this->comparator, this->angle_to_compare(0)));

    ESP_LOGI(TAG, "Set generator action on timer and compare event");
    // go high on counter empty
    ESP_ERROR_CHECK(mcpwm_generator_set_action_on_timer_event(
        generator, MCPWM_GEN_TIMER_EVENT_ACTION(MCPWM_TIMER_DIRECTION_UP,
                                                MCPWM_TIMER_EVENT_EMPTY,
                                                MCPWM_GEN_ACTION_HIGH)));
    // go low on compare threshold
    ESP_ERROR_CHECK(mcpwm_generator_set_action_on_compare_event(
        generator,
        MCPWM_GEN_COMPARE_EVENT_ACTION(
            MCPWM_TIMER_DIRECTION_UP, this->comparator, MCPWM_GEN_ACTION_LOW)));

    ESP_LOGI(TAG, "Enable and start timer");
    ESP_ERROR_CHECK(mcpwm_timer_enable(timer));
    ESP_ERROR_CHECK(mcpwm_timer_start_stop(timer, MCPWM_TIMER_START_NO_STOP));
}

void Servo::hardware_step(int8_t step_dir) {
    float current_angle_rads = this->get_current_angle();
    int32_t current_angle_degs = current_angle_rads * 180 / PI;
    ESP_ERROR_CHECK(mcpwm_comparator_set_compare_value(
        this->comparator, this->angle_to_compare(current_angle_degs)));
}

#else

void Servo::hardware_setup() {}

void Servo::hardware_step(int8_t) {}

#endif

Servo::Servo(int8_t pin) {
    this->homed = true;
    this->pin = pin;
}
Servo::~Servo() {
    if (this->end_stop != nullptr) {
        delete this->end_stop;
    }
}

bool Servo::home() { return true; }

uint32_t Servo::angle_to_compare(int32_t angle) {
    return (angle - SERVO_MIN_DEGREE) *
               (SERVO_MAX_PULSEWIDTH_US - SERVO_MIN_PULSEWIDTH_US) /
               (SERVO_MAX_DEGREE - SERVO_MIN_DEGREE) +
           SERVO_MIN_PULSEWIDTH_US;
}
