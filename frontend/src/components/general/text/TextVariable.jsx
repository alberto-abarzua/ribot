import PropTypes from 'prop-types';

const TextVariable = ({ label, value, setValue }) => {
    const onChangeFunc = e => {
        if (setValue) {
            setValue(e.target.value);
        }
    };
    return (
        <div className="inline-flex h-10 w-36 items-center justify-start gap-2.5 px-2 py-1.5">
            <div className="text-xs font-normal text-black">{label}</div>
            <div className="flex h-7 w-16 items-center justify-center gap-2.5 rounded-md bg-gray-50 shadow">
                <div className="text-xs font-normal text-black" onChange={onChangeFunc}>
                    {value}
                </div>
            </div>
        </div>
    );
};

TextVariable.propTypes = {
    label: PropTypes.string.isRequired,
    value: PropTypes.number.isRequired,
    setValue: PropTypes.func,
};

export default TextVariable;
