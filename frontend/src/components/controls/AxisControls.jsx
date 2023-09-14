import MoveAxis from '@/components/controls/MoveAxis';
import TextVariableInfo from '@/components/general/text/TextVariableInfo';
import { armPoseActions } from '@/redux/ArmPose';

import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';

const AxisControls = () => {
    const [coordsStep, setCoordsStep] = useState(10);
    const [anglesStep, setAnglesStep] = useState(0.1);
    const [toolStep, setToolStep] = useState(0.1);

    const dispatch = useDispatch();
    const currentPose = useSelector(state => state.armPose);

    return (
        <div className="flex flex-wrap items-center gap-4 p-4">
            <div className="flex flex-1 flex-col rounded-md bg-slate-200 p-4 shadow-md">
                <div>
                    <h3 className="mb-2 text-lg font-medium">Coordinates Control</h3>
                </div>
                <div className="w-2/3">
                    <TextVariableInfo
                        label="Step Size"
                        value={coordsStep}
                        setValue={setCoordsStep}
                        infoText={'The amount the arm moves for coordinate changes'}
                    ></TextVariableInfo>
                </div>
                <div className="flex flex-row justify-center">
                    <MoveAxis
                        label="X"
                        value={currentPose.x}
                        setValue={value => dispatch(armPoseActions.updateX(value))}
                        step={coordsStep}
                    ></MoveAxis>
                    <MoveAxis
                        label="Y"
                        value={currentPose.y}
                        setValue={value => dispatch(armPoseActions.updateY(value))}
                        step={coordsStep}
                    ></MoveAxis>
                    <MoveAxis
                        label="Z"
                        value={currentPose.z}
                        setValue={value => dispatch(armPoseActions.updateZ(value))}
                        step={coordsStep}
                    ></MoveAxis>
                </div>
            </div>

            <div className="flex flex-1 flex-col rounded-md bg-slate-200 p-4 shadow-md">
                <div>
                    <h3 className="mb-2 text-lg font-medium">Angles Control</h3>
                </div>
                <div className="w-2/3">
                    <TextVariableInfo
                        label="Step Size"
                        value={anglesStep}
                        setValue={setAnglesStep}
                        infoText={'The amount the arm moves for coordinate changes'}
                    ></TextVariableInfo>
                </div>

                <div className="flex flex-row justify-center">
                    <MoveAxis
                        label="Roll"
                        value={currentPose.roll}
                        setValue={value => dispatch(armPoseActions.updateRoll(value))}
                        step={anglesStep}
                    ></MoveAxis>
                    <MoveAxis
                        label="Pitch"
                        value={currentPose.pitch}
                        setValue={value => dispatch(armPoseActions.updatePitch(value))}
                        step={anglesStep}
                    ></MoveAxis>
                    <MoveAxis
                        label="Yaw"
                        value={currentPose.yaw}
                        setValue={value => dispatch(armPoseActions.updateYaw(value))}
                        step={anglesStep}
                    ></MoveAxis>
                </div>
            </div>
            <div className="flex flex-col  rounded-md bg-slate-200 p-4 shadow-md ">
                <div>
                    <h3 className="mb-2 text-lg font-medium">Tool Control</h3>
                </div>
                <div className="w-2/3">
                    <TextVariableInfo
                        label="Step Size"
                        value={toolStep}
                        setValue={setToolStep}
                        infoText={'The amount the arm moves for coordinate changes'}
                    ></TextVariableInfo>
                </div>

                <div className="flex flex-row justify-center">
                    <MoveAxis
                        label="Tool Value"
                        value={currentPose.toolValue}
                        setValue={value => dispatch(armPoseActions.updateToolValue(value))}
                        step={toolStep}
                    ></MoveAxis>
                </div>
            </div>
        </div>
    );
};

export default AxisControls;
