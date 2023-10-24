const ControllerStatus = {
    NOT_STARTED: 0,
    WAITING_CONNECTION: 1,
    RUNNING: 2,
    STOPPED: 3,
};

const ControllerSettings = {
    HOMING_DIRECTION: 1,
    SPEED_RAD_PER_S: 5,
    STEPS_PER_REV_MOTOR_AXIS: 9,
    CONVERSION_RATE_AXIS_JOINTS: 13,
    HOMING_OFFSET_RADS: 17,
};

export { ControllerStatus, ControllerSettings };
