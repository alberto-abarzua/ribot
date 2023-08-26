import PropTypes from 'prop-types';

const MoveAxis = ({ label, pose, setPose, step = 10 }) => {
    const value = pose[label]; // Extract the value for the specific axis

    const upValue = () => {
        setPose(prev => ({
            ...prev,
            [label]: prev[label] + step,
        }));
    };

    const downValue = () => {
        setPose(prev => ({
            ...prev,
            [label]: prev[label] - step,
        }));
    };
    return (
        <div className="flex w-40 flex-col justify-center rounded bg-slate-200 p-2">
            <div className="w-full pb-2 text-center text-lg font-bold uppercase">{label}</div>
            <div className=" flex flex-col space-y-3">
                <button className="w-full rounded bg-slate-400 p-2" onClick={upValue}>
                    +
                </button>
                <input
                    className="w-full appearance-none rounded bg-white p-2 text-center"
                    type="text"
                    readOnly // Make the input read-only since the value is controlled by the buttons
                    value={value.toFixed(2)}
                ></input>
                <button className="w-full rounded bg-slate-400 p-2" onClick={downValue}>
                    -
                </button>
            </div>
        </div>
    );
};

MoveAxis.propTypes = {
    label: PropTypes.string.isRequired,
    pose: PropTypes.shape({
        x: PropTypes.number,
        y: PropTypes.number,
        z: PropTypes.number,
        roll: PropTypes.number,
        pitch: PropTypes.number,
        yaw: PropTypes.number,
    }).isRequired,
    setPose: PropTypes.func.isRequired,
    step: PropTypes.number,
};

export default MoveAxis;
