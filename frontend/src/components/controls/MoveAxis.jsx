import PropTypes from 'prop-types';

const MoveAxis = ({ label, value, setValue, step_amount = 10 }) => {
    const step_float = parseFloat(step_amount);

    const upValue = () => {
        setValue(step_float);
    };

    const downValue = () => {
        setValue(-step_float);
    };

    return (
        <div className="inline-flex h-36 w-24 flex-col items-center justify-start gap-2 px-1">
            <div className="text-base font-bold text-black">{label}</div>
            <button
                onClick={upValue}
                className="flex h-7 w-20 flex-col items-center justify-center gap-2.5 rounded bg-slate-400 p-2.5 text-white shadow hover:bg-slate-600"
            >
                +
            </button>
            <div className="inline-flex h-6 w-16 cursor-default items-center justify-center gap-2.5 rounded-md bg-gray-200 shadow">
                <div className="w-12 select-none text-center text-xs font-normal text-black">
                    {value.toFixed(2)}
                </div>
            </div>
            <button
                onClick={downValue}
                className="flex h-7  w-20 flex-col items-center justify-center gap-2.5 rounded-sm bg-slate-400 p-2.5 text-white shadow hover:bg-slate-600"
            >
                -
            </button>
        </div>
    );
};

MoveAxis.propTypes = {
    label: PropTypes.string.isRequired,
    value: PropTypes.number.isRequired,
    setValue: PropTypes.func.isRequired,
    step_amount: PropTypes.number,
};

export default MoveAxis;
