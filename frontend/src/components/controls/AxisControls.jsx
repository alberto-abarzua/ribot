import MoveAxis from "@/components/controls/MoveAxis";


const AxisControls = ({currentPose, setCurrentPose}) => {

    return (
        <div className="flex flex-row space-x-1 ">
                        <MoveAxis
                            label="x"
                            pose={currentPose}
                            setPose={setCurrentPose}
                        ></MoveAxis>
                        <MoveAxis
                            label="y"
                            pose={currentPose}
                            setPose={setCurrentPose}
                        ></MoveAxis>
                        <MoveAxis
                            label="z"
                            pose={currentPose}
                            setPose={setCurrentPose}
                        ></MoveAxis>
                        <MoveAxis
                            label="roll"
                            pose={currentPose}
                            setPose={setCurrentPose}
                            step={0.1}
                        ></MoveAxis>
                        <MoveAxis
                            label="pitch"
                            pose={currentPose}
                            setPose={setCurrentPose}
                            step={0.1}
                        ></MoveAxis>
                        <MoveAxis
                            label="yaw"
                            pose={currentPose}
                            setPose={setCurrentPose}
                            step={0.1}
                        ></MoveAxis>
                    </div>
    )

};

export default AxisControls;
