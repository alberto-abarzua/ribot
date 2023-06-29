from control.controller import ArmController
from utils.prints import console

if __name__ == "__main__":
    controller = ArmController()
    controller.start()
    healthy = controller.health_check()
    if healthy:
        controller.home()
        console.print("homing agaion", style="error")
        controller.home()

        controller.move_to_angles([0, 0, 0, 2, 0, 0])

        controller.move_to_angles([0, 2, 0, 2, 0, 0])

        controller.move_to_angles([0, 0, 0, 0, 0, 0])

    while True:
        pass
