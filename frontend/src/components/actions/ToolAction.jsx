import BuildIcon from '@mui/icons-material/Build';

import { useState } from 'react';

import TextVariable from '../general/text/TextVariable';
import BaseAction from './BaseAction';

const ToolAction = () => {
    const [toolValue, setToolValue] = useState({
        timeout: 0,
    });

    return (
        <BaseAction className={'bg-yellow-200'} icon={<BuildIcon className="text-6xl"></BuildIcon>}>
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-slate-200 p-2  shadow">
                        <TextVariable
                            label="Tool (%)"
                            value={toolValue.timeout}
                            setValue={value => setToolValue(prev => ({ ...prev, timeout: value }))}
                            disabled={true}
                        />
                    </div>
                </div>
            </div>
        </BaseAction>
    );
};

export default ToolAction;
