import BedtimeIcon from '@mui/icons-material/Bedtime';

import { useState } from 'react';

import TextVariable from '../general/text/TextVariable';
import BaseAction from './BaseAction';

const SleepAction = ({ ...props }) => {
    const [sleepValue, setsleepValue] = useState({
        timeout: 0,
    });

    return (
        <BaseAction
            className={'bg-rose-400'}
            icon={<BedtimeIcon className="text-6xl"></BedtimeIcon>}
            {...props}
        >
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-slate-200 p-2  shadow">
                        <TextVariable
                            label="Timeout (s)"
                            setValue={value => setsleepValue(prev => ({ ...prev, timeout: value }))}
                            value={sleepValue.timeout}
                            disabled={false}
                        />
                    </div>
                </div>
            </div>
        </BaseAction>
    );
};

export default SleepAction;
