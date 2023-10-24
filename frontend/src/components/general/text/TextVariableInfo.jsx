import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import TextVariable from '@/components/general/text/TextVariable';
import PropTypes from 'prop-types';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

const TextVariableInfo = ({ label, value, setValue, infoText, disabled = false }) => {
    return (
        <div className="flex ">
            <TooltipProvider>
                <Tooltip delayDuration={300}>
                    <TooltipTrigger>
                        <InfoOutlinedIcon className="relative left-2 text-lg text-blue-400" />
                    </TooltipTrigger>

                    <TooltipContent>{infoText}</TooltipContent>
                </Tooltip>
            </TooltipProvider>
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
