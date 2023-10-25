import InfoHover from './InfoHover';
import TextVariable from '@/components/general/text/TextVariable';
import PropTypes from 'prop-types';

const TextVariableInfo = ({ label, value, setValue, infoText, disabled = false }) => {
    return (
        <div className="flex items-center ">
            <div className="relative left-2">
                <InfoHover text={infoText} />
            </div>
            <TextVariable label={label} value={value} setValue={setValue} disabled={disabled} />
        </div>
    );
};

TextVariableInfo.propTypes = {
    label: PropTypes.string.isRequired,
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    setValue: PropTypes.func,
    infoText: PropTypes.string.isRequired,
    disabled: PropTypes.bool,
};

export default TextVariableInfo;
