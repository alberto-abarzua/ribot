import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import PropTypes from 'prop-types';

const InfoHover = ({ text }) => {
    return (
        <TooltipProvider>
            <Tooltip delayDuration={300}>
                <TooltipTrigger>
                    <InfoOutlinedIcon className="text-lg text-blue-400" />
                </TooltipTrigger>

                <TooltipContent>{text}</TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
};

InfoHover.propTypes = {
    text: PropTypes.string.isRequired,
};

export default InfoHover;
