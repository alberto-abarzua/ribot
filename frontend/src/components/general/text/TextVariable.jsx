import PropTypes from 'prop-types';

const TextVariable = ({ label, value, setValue, disabled = false }) => {
    const onChangeFunc = e => {
        if (setValue) {
            setValue(e.target.value);
        }
    };
    return (
        <div className="flex h-10 w-auto items-center justify-end gap-2.5 px-2 py-1.5">
            <div className="text-xs font-normal">{label}</div>
            <div className="flex h-7 w-16 items-center justify-center gap-2.5 rounded-md bg-gray-50 shadow">
                <input
                    type="text"
                    value={value.toFixed(2)}
                    onChange={onChangeFunc}
                    className="h-full w-full rounded-md text-center text-xs font-normal text-gray-800"
                    disabled={disabled}
                />
            </div>
        </div>
    );
};

TextVariable.propTypes = {
    label: PropTypes.string.isRequired,
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    setValue: PropTypes.func,
    disabled: PropTypes.bool,
};

export default TextVariable;
