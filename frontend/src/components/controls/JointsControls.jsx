import MoveAxis from '@/components/controls/MoveAxis';
import TextVariableInfo from '@/components/general/text/TextVariableInfo';
import api from '@/utils/api';

import { useState } from 'react';
import { useSelector } from 'react-redux';

const JointsControls = () => {
    const currentAngles = useSelector(state => state.armPose.currentAngles);
    const [angleStep, setAngleStep] = useState(0.1);

    const callSetAngle = (index, value) => {
        api.post('/move/joint/relative/', { joint_idx: index, joint_value: value });
    };

    const callHomeJoint = index => {
        api.post('/move/home_joint/', { joint_idx: index });
    };

    return (
        <div className="flex w-fit flex-wrap items-center gap-4 p-4">
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
                </div>{' '}
                <div className="flex flex-row justify-center gap-2">
                    {' '}
                    {currentAngles.map((_, index) => (
                        <div className="flex flex-col items-center justify-center " key={index}>
                            <MoveAxis
                                label={`Joint ${index + 1}`}
                                value={currentAngles[index]}
                                setValue={value => {
                                    callSetAngle(index, value);
                                }}
                                step_amount={angleStep}
                            ></MoveAxis>
                            <button
                                className="w-fit rounded-md bg-green-500 px-3 py-2 text-white hover:bg-green-700"
                                onClick={() => callHomeJoint(index)}
                            >
                                Home
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default JointsControls;
