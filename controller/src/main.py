from control.controller import ArmController, Settings

if __name__ == "__main__":
    controller = ArmController()
    controller.start()
    healthy = controller.health_check()
    if healthy:
        controller.home()
        controller.set_setting_joints(Settings.SPEED_RAD_PER_S, 0.2)

        while True:
            zero = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            thirty = [30 * 3.14 / 180 for _ in range(6)]

            controller.move_to_angles(zero)

            controller.move_to_angles(thirty)

            controller.move_to_angles(zero)

    while True:
        pass
