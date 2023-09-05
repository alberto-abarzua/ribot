import MoveAxis from '@/components/controls/MoveAxis';
import TextVariableInfo from '@/components/general/text/TextVariableInfo';
import { useState } from 'react';
import PropTypes from 'prop-types';
const AxisControls = ({ currentPose, setCurrentPose }) => {
    const [coordsStep, setCoordsStep] = useState(10);
    const [anglesStep, setAnglesStep] = useState(0.1);

    return (
        <div className="flex items-center justify-center space-x-5  p-4">
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
                <div className="flex flex-row">
                    <MoveAxis label="x" pose={currentPose} setPose={setCurrentPose}></MoveAxis>
                    <MoveAxis label="y" pose={currentPose} setPose={setCurrentPose}></MoveAxis>
                    <MoveAxis label="z" pose={currentPose} setPose={setCurrentPose}></MoveAxis>
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

                <div className="flex flex-row">
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
            </div>
        </div>
    );
};

AxisControls.propTypes = {
    currentPose: PropTypes.shape({
        x: PropTypes.number,
        y: PropTypes.number,
        z: PropTypes.number,
        roll: PropTypes.number,
        pitch: PropTypes.number,
        yaw: PropTypes.number,
    }).isRequired,
    setCurrentPose: PropTypes.func.isRequired,
};

export default AxisControls;
