import DragIndicatorIcon from '@mui/icons-material/DragIndicator';

import PropTypes from 'prop-types';

const SleepAction = ({ icon, children, className }) => {
    return (
        <div
            className={
                ' flex items-center justify-center space-x-4 rounded-md px-6 py-3 text-white shadow ' +
                className
            }
        >
            <div className="flex flex-1 items-center justify-start ">{icon}</div>

            {children}
            <div className="flex items-center justify-start ">
                <DragIndicatorIcon className="text-4xl"></DragIndicatorIcon>
            </div>
        </div>
    );
};

SleepAction.propTypes = {
    icon: PropTypes.element.isRequired,
    children: PropTypes.element.isRequired,
    className: PropTypes.string,
};

export default SleepAction;
