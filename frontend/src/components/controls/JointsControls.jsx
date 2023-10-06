import MoveAxis from '@/components/controls/MoveAxis';
import TextVariableInfo from '@/components/general/text/TextVariableInfo';
import api from '@/utils/api';
import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';

const JointsControls = () => {
    const currentAngles = useSelector(state => state.armPose.currentAngles);
    console.log(currentAngles);
    const [angles, setAngles] = useState(currentAngles);
    const [angleStep, setAngleStep] = useState(0.1);

    const callSetAngle = (index, value) => {
        api.post('/move/joint/',{joint_idx: index, joint_value: value});
    };

    const callHomeJoint = (index) => {
        api.post('/move/home_joint/',{joint_idx: index});
    };

    return (
        <div className="flex flex-wrap items-center gap-4 p-4">
            <div className="flex flex-1 flex-col rounded-md bg-slate-200 p-4 shadow-md">
                <div>
                    <h3 className="mb-2 text-lg font-medium">Joint Controls</h3>
                </div>
                <div className="w-2/3">
                    <TextVariableInfo
                        label="Step Size"
                        value={angleStep}
                        setValue={setAngleStep}
                        infoText={'The amount the arm moves for coordinate changes'}
                    ></TextVariableInfo>
                </div>
                <div className="flex flex-row justify-center">
                    {angles.map((angle, index) => (
                        <div key={index}>
                            <MoveAxis
                                label={`Joint ${index + 1}`}
                                value={currentAngles[index]}
                                setValue={value => {
                                    const newAngles = [...angles];
                                    newAngles[index] = value;
                                    setAngles(newAngles);
                                    callSetAngle(index, value);
                                }}
                                step_amount={angleStep}
                            ></MoveAxis>
                            <button onClick={() => callHomeJoint(index)}>Home</button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default JointsControls;
