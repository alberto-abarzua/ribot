import MoveAxis from '@/components/controls/MoveAxis';
import ToolControls from '@/components/controls/ToolControls';
import TextVariableInfo from '@/components/general/text/TextVariableInfo';
import { useToast } from '@/components/ui/use-toast';
import api from '@/utils/api';
import { useState } from 'react';
import { useSelector } from 'react-redux';

const AxisControls = () => {
    const { toast } = useToast();
    const [coordsStep, setCoordsStep] = useState(10);
    const [anglesStep, setAnglesStep] = useState(10);

    const currentPose = useSelector(state => state.armPose);

    const moveArm = async (field, amount) => {
        let base = {
            x: 0,
            y: 0,
            z: 0,
            roll: 0,
            pitch: 0,
            yaw: 0,
        };
        base[field] = amount;
        try {
            await api.post('/move/pose/relative/', base);
        } catch (e) {
            console.log(e);
            toast({
                variant: 'destructive',
                title: 'Position out of bounds!',
                description: 'The position you are trying to move to is out of bounds.',
            });
        }
    };

    return (
        <div className="flex flex-wrap items-center gap-2 p-2">
            <div className="flex flex-1 flex-col rounded-md bg-slate-200 p-2 shadow-md">
                <div className="flex justify-between ">
                    <h3 className="mb-2text-lg font-medium">Coordinates Control</h3>

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
                        setValue={value => moveArm('x', value)}
                        step_amount={coordsStep}
                    ></MoveAxis>
                    <MoveAxis
                        label="Y"
                        value={currentPose.y}
                        setValue={value => moveArm('y', value)}
                        step_amount={coordsStep}
                    ></MoveAxis>
                    <MoveAxis
                        label="Z"
                        value={currentPose.z}
                        setValue={value => moveArm('z', value)}
                        step_amount={coordsStep}
                    ></MoveAxis>
                </div>
            </div>

            <div className="flex flex-1 flex-col rounded-md bg-slate-200 p-2 shadow-md">
                <div className="flex justify-between ">
                    <h3 className="mb-2 text-lg font-medium">Angles Control</h3>
                    <TextVariableInfo
                        label="Step Size"
                        value={anglesStep}
                        setValue={setAnglesStep}
                        infoText={'The amount the arm moves for tool angle changes'}
                    ></TextVariableInfo>
                </div>

                <div className="flex flex-row justify-center">
                    <MoveAxis
                        label="Roll"
                        value={currentPose.roll}
                        setValue={value => moveArm('roll', value)}
                        step_amount={anglesStep}
                    ></MoveAxis>
                    <MoveAxis
                        label="Pitch"
                        value={currentPose.pitch}
                        setValue={value => moveArm('pitch', value)}
                        step_amount={anglesStep}
                    ></MoveAxis>
                    <MoveAxis
                        label="Yaw"
                        value={currentPose.yaw}
                        setValue={value => moveArm('yaw', value)}
                        step_amount={anglesStep}
                    ></MoveAxis>
                </div>
            </div>

            <div className="flex flex-row justify-center">
                <ToolControls></ToolControls>
            </div>
        </div>
    );
};

export default AxisControls;
