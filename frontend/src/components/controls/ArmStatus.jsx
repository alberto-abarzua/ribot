import PrimaryButton from '@/components/general/buttons/PrimaryButton';
import TextVariable from '@/components/general/text/TextVariable';
import api from '@/utils/api';
import AddHomeIcon from '@mui/icons-material/AddHome';
import DoneAllIcon from '@mui/icons-material/DoneAll';
import NearbyErrorIcon from '@mui/icons-material/NearbyError';
import { ControllerStatus } from '@/utils/arm_enums';

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
    const isHomed = currentPose.isHomed;
    const armStatus = currentPose.status;

    let status = {
        label: '',
        color: '',
        icon: null,
    };

    if (armStatus === ControllerStatus.NOT_STARTED) {
        status.label = 'Not Started';
        status.color = 'bg-red-200';
        status.icon = NearbyErrorIcon;
    } else if (armStatus === ControllerStatus.WAITING_CONNECTION) {
        status.label = 'Waiting Connection';
        status.color = 'bg-yellow-200';
        status.icon = NearbyErrorIcon;
    } else if (armStatus === ControllerStatus.RUNNING) {
        if (!isHomed) {
            status.label = 'Not Homed';
            status.color = 'bg-yellow-200';
            status.icon = AddHomeIcon;
        } else {
            status.label = 'Ready';
            status.color = 'bg-green-200';
            status.icon = DoneAllIcon;
        }
    } else if (armStatus === ControllerStatus.STOPPED) {
        status.label = 'Stopped';
        status.color = 'bg-red-200';
        status.icon = NearbyErrorIcon;
    }

    return (
        <div className="m-4 flex flex-col rounded-md  bg-slate-200  p-2  shadow-md">
            <div className="mb-1 flex w-full items-center justify-center self-center ">
                <h2 className="mr-2 flex-nowrap whitespace-nowrap text-xl font-medium">
                    Arm Status
                </h2>

                <div
                    className={
                        'flex w-full items-center justify-center self-end rounded-full px-2 py-1 ' +
                        status.color
                    }
                >
                    <status.icon className="mr-2 text-lg" />
                    <h3 className=" text-lg font-medium">{status.label}</h3>
                </div>
            </div>
            <div className="flex flex-col items-center justify-center md:flex-row">
                <div className="flex flex-col items-end justify-start">
                    <TextVariable label="Roll" disabled={true} value={currentPose.roll} />
                    <TextVariable label="Pitch" disabled={true} value={currentPose.pitch} />
                    <TextVariable label="Yaw" disabled={true} value={currentPose.yaw} />
                </div>
                <div className="flex flex-col items-end justify-end">
                    <TextVariable label="X" disabled={true} value={currentPose.x} />
                    <TextVariable label="Y" disabled={true} value={currentPose.y} />
                    <TextVariable label="Z" disabled={true} value={currentPose.z} />
                    <TextVariable label="Tool" disabled={true} value={currentPose.toolValue} />
                </div>
            </div>
            <div className="flex w-full  items-end justify-end">
                <PrimaryButton onClick={call_home}>Home Arm</PrimaryButton>
                <WarningButton onClick={call_stop_movement}>STOP</WarningButton>
            </div>
        </div>
    );
};

export default ArmStatus;
