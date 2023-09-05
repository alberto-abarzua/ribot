import TextVariable from '../general/text/TextVariable';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import BuildIcon from '@mui/icons-material/Build';
import BaseAction from './BaseAction';
import { useState } from 'react';

const ToolAction = () => {
    const [sleepValue, setsleepValue] = useState({
        timeout: 0,
    });

    return (
        <BaseAction className={'bg-yellow-200'} icon={<BuildIcon className="text-6xl"></BuildIcon>}>
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-slate-200 p-2  shadow">
                        <TextVariable
                            label="Tool (%)"
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

export default ToolAction;
