import BedtimeIcon from '@mui/icons-material/Bedtime';
import TextVariable from '../general/text/TextVariable';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';

import { useState } from 'react';

const SleepAction = ({ icon, children, className }) => {
    const [sleepValue, setsleepValue] = useState({
        timeout: 0,
    });

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

export default SleepAction;
