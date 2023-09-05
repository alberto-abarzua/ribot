import BedtimeIcon from '@mui/icons-material/Bedtime';
import TextVariable from '../general/text/TextVariable';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import BaseAction from './BaseAction';
import { useState } from 'react';

const SleepAction = () => {
    const [sleepValue, setsleepValue] = useState({
        timeout: 0,
    });

    return (
        <BaseAction
            className={'bg-rose-400'}
            icon={<BedtimeIcon className="text-6xl"></BedtimeIcon>}
        >
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-slate-200 p-2  shadow">
                        <TextVariable
                            label="Timeout (s)"
                            value={sleepValue.timeout}
                            setValue={value =>
                                setCurrentPose(prev => ({ ...prev, timeout: value }))
                            }
                        />
                    </div>
                </div>
            </div>
        </BaseAction>
    );
};

export default SleepAction;
