import ToolBar from '@/components/actions/ToolBar';
import { BaseActionObj } from '@/utils/actions';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';

import { useState, useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';

const ActionContainer = () => {
    const actionListSerialized = useSelector(state => state.actionList.actions);
    const actionList = actionListSerialized.map(action => BaseActionObj.fromSerializable(action));
    const [running, setRunning] = useState(false);
    const armPose = useSelector(state => state.armPose);

    const runningRef = useRef(false);

    useEffect(() => {
        runningRef.current = running;

        const runActions = async () => {
            console.log('running actions');
            for (const action of actionList) {
                if (!runningRef.current) {
                    console.log('stopped running actions');
                    break;
                }
                await action.run(armPose);
            }
            console.log('finished running actions');
            setRunning(false);
        };

        if (running) {
            runActions();
        }
    }, [running, actionList, armPose]);

    let play_or_stop = null;
    if (running) {
        play_or_stop = (
            <div
                className="absolute bottom-10 right-0 z-20 flex h-14 w-fit cursor-pointer items-center justify-center rounded-md bg-red-400 px-2 hover:bg-red-500"
                onClick={() => setRunning(prev => !prev)}
            >
                <StopIcon className="text-3xl text-white" />
                <div className="text-lg text-white"> Stop</div>
            </div>
        );
    } else {
        play_or_stop = (
            <div
                className="absolute bottom-10 right-0 z-20 flex h-14 w-fit cursor-pointer items-center justify-center rounded-md bg-green-400 px-2 hover:bg-green-500"
                onClick={() => setRunning(prev => !prev)}
            >
                <PlayArrowIcon className="text-3xl text-white" />
                <div className="text-lg text-white"> Run</div>
            </div>
        );
    }

    return (
        <div className="relative m-0 flex h-full max-h-screen w-full flex-col items-center space-y-4 ">
            <ToolBar />
            <div className="flex h-full max-h-screen w-full flex-col items-center gap-4 overflow-y-auto">
                {actionList.map(action => action.render())}
            </div>
            {play_or_stop}
        </div>
    );
};

export default ActionContainer;
