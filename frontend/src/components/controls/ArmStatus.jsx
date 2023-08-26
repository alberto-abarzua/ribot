import PropTypes from 'prop-types';

const ArmStatus = ({ status }) => {
    // status should have x,y,z, roll pitch, yaw

    return (
        <div className="w-full rounded-lg bg-gray-100 p-4">
            <h3 className="mb-2 text-lg font-medium">Arm Status</h3>
            <div className="flex flex-col items-center md:flex-row">
                <div className="flex flex-1 space-x-2 self-center">
                    <label htmlFor="x-input" className="self-center text-gray-700">
                        X:
                    </label>
                    <input
                        type="text"
                        id="x-input"
                        value={status.x.toFixed(2)}
                        readOnly
                        className="w-full rounded-lg bg-gray-200 px-2 py-1 "
                    />
                </div>
                <div className="flex flex-1 space-x-2 self-center">
                    <label htmlFor="y-input" className="self-center text-gray-700">
                        Y:
                    </label>
                    <input
                        type="text"
                        id="y-input"
                        value={status.y.toFixed(2)}
                        readOnly
                        className="w-full rounded-lg bg-gray-200 px-2 py-1 "
                    />
                </div>
                <div className="flex flex-1 space-x-2 self-center">
                    <label htmlFor="z-input" className="self-center text-gray-700">
                        Z:
                    </label>
                    <input
                        type="text"
                        id="z-input"
                        value={status.z.toFixed(2)}
                        readOnly
                        className="w-full rounded-lg bg-gray-200 px-2 py-1 "
                    />
                </div>
                <div className="flex flex-1 space-x-2 self-center">
                    <label htmlFor="roll-input" className="self-center text-gray-700">
                        Roll:
                    </label>
                    <input
                        type="text"
                        id="roll-input"
                        value={status.roll.toFixed(2)}
                        readOnly
                        className="w-full rounded-lg bg-gray-200 px-2 py-1 "
                    />
                </div>
                <div className="flex flex-1 space-x-2 self-center">
                    <label htmlFor="pitch-input" className="self-center text-gray-700">
                        Pitch:
                    </label>
                    <input
                        type="text"
                        id="pitch-input"
                        value={status.pitch.toFixed(2)}
                        readOnly
                        className="w-full rounded-lg bg-gray-200 px-2 py-1 "
                    />
                </div>
                <div className="flex flex-1 space-x-2 self-center">
                    <label htmlFor="yaw-input" className="self-center text-gray-700">
                        Yaw:
                    </label>
                    <input
                        type="text"
                        id="yaw-input"
                        value={status.yaw.toFixed(2)}
                        readOnly
                        className="w-full rounded-lg bg-gray-200 px-2 py-1"
                    />
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
};

export default ArmStatus;
