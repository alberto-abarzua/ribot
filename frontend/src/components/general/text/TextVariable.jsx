import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';

const TextVariable = ({ label, value: propValue, setValue, disabled = false }) => {
    const [value, setLocalValue] = useState(propValue);

    useEffect(() => {
        setLocalValue(propValue);
    }, [propValue]);

    const onBlur = () => {
        let newValue = value;
        if (typeof newValue === 'number') {
            newValue = parseFloat(newValue.toFixed(2));
            setValue(newValue);
        } else if (/^\d+(\.\d+)?$/.test(newValue)) {
            newValue = parseFloat(newValue);
            setValue(newValue);
        }
    };

    const onChangeFunc = e => {
        setLocalValue(e.target.value);
    };

    return (
        <div className="flex h-10 w-auto items-center justify-end gap-2.5 px-2 py-1.5">
            <div className="w-fit whitespace-nowrap text-xs font-normal">{label}</div>
            <div className="flex h-7 w-16 items-center justify-center gap-2.5 rounded-md bg-gray-50 shadow">
                <input
                    type="text"
                    value={typeof value === 'number' ? value.toFixed(2) : value}
                    onChange={onChangeFunc}
                    onBlur={onBlur}
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
