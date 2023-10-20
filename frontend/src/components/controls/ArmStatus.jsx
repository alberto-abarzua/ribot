import PrimaryButton from '@/components/general/buttons/PrimaryButton';
import TextVariable from '@/components/general/text/TextVariable';
import api from '@/utils/api';

import { useSelector } from 'react-redux';

import WarningButton from '../general/buttons/WarningButton';

const ArmStatus = () => {
    const call_home = async () => {
        await api.post('/move/home/');
    };

    const call_stop_movement = async () => {
        await api.post('/settings/stop/');
    };
    const currentPose = useSelector(state => state.armPose);

    return (
        <div className="m-4 rounded-md  bg-slate-200  p-4  shadow-md">
            <h3 className="mb-2 text-lg font-medium">Arm Status</h3>
            <div className="flex flex-col items-center md:flex-row">
                <div className="flex flex-col">
                    <TextVariable label="X" value={currentPose.x} />
                    <TextVariable label="Y" value={currentPose.y} />
                    <TextVariable label="Z" value={currentPose.z} />
                    <TextVariable label="Tool" value={currentPose.toolValue} />
                </div>

                <div className="flex flex-col items-end justify-end">
                    <TextVariable label="Roll" value={currentPose.roll} />
                    <TextVariable label="Pitch" value={currentPose.pitch} />
                    <TextVariable label="Yaw" value={currentPose.yaw} />
                </div>
                <div className="flex w-full  items-end justify-end">
                    <PrimaryButton className="mr-10" onClick={call_home}>
                        Home Arm
                    </PrimaryButton>
                    <WarningButton onClick={call_stop_movement}>STOP</WarningButton>
                </div>
            </div>
        </div>
    );
};

export default ArmStatus;
