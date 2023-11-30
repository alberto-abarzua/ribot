import MoveAxis from '@/components/controls/MoveAxis';
import TextVariableInfo from '@/components/general/text/TextVariableInfo';
import api from '@/utils/api';
import { useState } from 'react';
import { useSelector } from 'react-redux';

const ToolControls = () => {
    const currentPoseTool = useSelector(state => state.armPose.toolValue);
    const moveTool = amount => {
        console.log('Moving tool by: ' + amount);
        api.post('/move/tool/relative/', { toolValue: amount });
    };

    const [toolStep, setToolStep] = useState(10);

    return (
        <div className="flex flex-col  rounded-md bg-slate-200 p-2 shadow-md ">
            <div className="flex flex-col justify-between">
                <h3 className="mb-2 text-lg font-medium">Tool Control</h3>
                <TextVariableInfo
                    label="Step Size"
                    value={toolStep}
                    setValue={setToolStep}
                    infoText={'The amount the tool will move (not precise)'}
                ></TextVariableInfo>
            </div>
            <div className="flex flex-row justify-center">
                <MoveAxis
                    label="Tool Value"
                    value={currentPoseTool}
                    setValue={value => moveTool(value)}
                    step_amount={toolStep}
                ></MoveAxis>
            </div>
        </div>
    );
};

export default ToolControls;
