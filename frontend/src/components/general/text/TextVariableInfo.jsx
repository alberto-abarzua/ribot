import PropTypes from 'prop-types';

import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

const TextVariableInfo = ({ label, value, setValue, infoText }) => {
    const onChangeFunc = e => {
        if (setValue) {
            setValue(e.target.value);
        }
    };
    return (
        <div className="inline-flex h-10 w-auto items-center justify-end gap-0.5 px-2 py-1.5">
            <div className="relative flex items-center justify-start">
                <div className="text-xs font-normal ">{label}</div>
                <div className={'group relative'}>
                    <InfoOutlinedIcon className=" relative -top-1 cursor-pointer pl-1 text-blue-600 group-hover:text-blue-400"></InfoOutlinedIcon>
                    <div
                        className="absolute bottom-12 left-0 z-20 hidden w-40 flex-col-reverse rounded-md bg-gray-50 px-3 py-2 text-sm group-hover:flex"
                        style={{ maxWidth: '200px', wordWrap: 'break-word' }}
                    >
                        {infoText}
                    </div>

                    <div className="absolute -top-12 left-6  z-10 hidden h-10 w-4 rotate-[60deg] bg-gray-50 px-1 py-2 group-hover:block"></div>
                </div>
                :
            </div>
            <div className="flex h-7 w-16 items-center justify-center gap-2.5 rounded-md bg-gray-50 shadow">
                <input
                    type="text"
                    value={value}
                    onChange={onChangeFunc}
                    className="w-full text-center text-xs font-normal text-gray-800 "
                />
            </div>
        </div>
    );
};

TextVariableInfo.propTypes = {
    label: PropTypes.string.isRequired,
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    setValue: PropTypes.func,
};

export default TextVariableInfo;
