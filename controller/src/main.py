from control.controller import ArmController
import time
if __name__ == "__main__":
    controller = ArmController()
    controller.start()
    while not controller.is_ready:
        pass
    
    controller.home(wait = True)

    controller.move_to_angles([0, 0, 0, 2, 0, 0])

    controller.move_to_angles([0, 2, 0, 2, 0, 0])

    while True:
        pass
