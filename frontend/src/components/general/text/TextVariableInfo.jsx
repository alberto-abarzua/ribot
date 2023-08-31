import PropTypes from 'prop-types';

import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

const TextVariableInfo = ({ label, value, setValue, infoText }) => {
    const onChangeFunc = e => {
        if (setValue) {
            setValue(e.target.value);
        }
    };
    return (
        <div className="inline-flex h-10 w-36 items-center justify-start gap-0.5 px-2 py-1.5">
            <div className="relative flex items-center justify-start">
                <div className="text-xs font-normal text-black">{label}</div>
                <div className={'group relative'}>
                    <InfoOutlinedIcon className=" relative -top-1 cursor-pointer text-lg text-gray-800 group-hover:text-blue-400"></InfoOutlinedIcon>
                    <div className="absolute -top-14 left-0 z-20 hidden whitespace-nowrap rounded-md bg-gray-50 px-3 py-2 group-hover:flex">
                        {infoText}
                    </div>

                    <div className="absolute -top-12 left-4  z-10 hidden h-10 w-4 rotate-[60deg] bg-gray-50 px-1 py-2 group-hover:block"></div>
                </div>
                :
            </div>
            <div className="flex h-7 w-16 items-center justify-center gap-2.5 rounded-md bg-gray-50 shadow">
                <div onChange={onChangeFunc} className="text-xs font-normal text-black">
                    {value}
                </div>
            </div>
        </div>
    );
};

TextVariableInfo.propTypes = {
    label: PropTypes.string.isRequired,
    value: PropTypes.number.isRequired,
    setValue: PropTypes.func,
};

export default TextVariableInfo;
