import PrimaryButton from '@/components/general/buttons/PrimaryButton';
import WarningButton from '@/components/general/buttons/WarningButton';
import TextVariable from '@/components/general/text/TextVariable';
import api from '@/utils/api';

import PropTypes from 'prop-types';

const ArmStatus = ({ setCurrentPose, currentPose }) => {
    const call_home = async () => {
        await api.post('/move/home/');
    };

    return (
        <div className="m-4 rounded-md  bg-slate-200  p-4  shadow-md">
            <h3 className="mb-2 text-lg font-medium">Arm Status</h3>
            <div className="flex flex-col items-center md:flex-row">
                <div className="flex flex-col">
                    <TextVariable
                        label="X"
                        value={currentPose.x}
                        setValue={value => setCurrentPose(prev => ({ ...prev, x: value }))}
                    />
                    <TextVariable
                        label="Y"
                        value={currentPose.y}
                        setValue={value => setCurrentPose(prev => ({ ...prev, y: value }))}
                    />
                    <TextVariable
                        label="Z"
                        value={currentPose.z}
                        setValue={value => setCurrentPose(prev => ({ ...prev, z: value }))}
                    />
                </div>

                <div className="flex flex-col items-end justify-end">
                    <TextVariable
                        label="Roll"
                        value={currentPose.roll}
                        setValue={value => setCurrentPose(prev => ({ ...prev, roll: value }))}
                    />
                    <TextVariable
                        label="Pitch"
                        value={currentPose.pitch}
                        setValue={value => setCurrentPose(prev => ({ ...prev, pitch: value }))}
                    />
                    <TextVariable
                        label="Yaw"
                        value={currentPose.yaw}
                        setValue={value => setCurrentPose(prev => ({ ...prev, yaw: value }))}
                    />
                </div>
                <div className="flex w-full  items-end justify-end">
                    <PrimaryButton className="mr-10" onClick={call_home}>
                        Home Arm
                    </PrimaryButton>
                    <WarningButton>Restart</WarningButton>
                </div>
            </div>
        </div>
    );
};
ArmStatus.propTypes = {
    status: PropTypes.shape({
        x: PropTypes.number.isRequired,
        y: PropTypes.number.isRequired,
        z: PropTypes.number.isRequired,
        roll: PropTypes.number.isRequired,
        pitch: PropTypes.number.isRequired,
        yaw: PropTypes.number.isRequired,
    }).isRequired,
    setCurrentPose: PropTypes.func.isRequired,
    currentPose: PropTypes.shape({
        x: PropTypes.number.isRequired,
        y: PropTypes.number.isRequired,
        z: PropTypes.number.isRequired,
        roll: PropTypes.number.isRequired,
        pitch: PropTypes.number.isRequired,
        yaw: PropTypes.number.isRequired,
    }).isRequired,
};

export default ArmStatus;
