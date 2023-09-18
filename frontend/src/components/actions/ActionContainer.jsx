import ToolBar from '@/components/actions/ToolBar';
import { actionListActions } from '@/redux/ActionListSlice';
import { BaseActionObj } from '@/utils/actions';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';

import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';

const ActionContainer = () => {
    const dispatch = useDispatch();
    const actionListSerialized = useSelector(state => state.actionList.actions);
    const actionList = actionListSerialized.map(action => BaseActionObj.fromSerializable(action));
    const [running, setRunning] = useState(false);
    const armPose = useSelector(state => state.armPose);
    const runningRef = useRef(false);
    console.log('running', running);

    useEffect(() => {
        console.log('running changed', running);
        runningRef.current = running;
    }, [running]);

    const runActions = async () => {
        console.log('running actions');
        for (const action of actionList) {
            if (!runningRef.current) {
                console.log('stopped running actions');
                break;
            }
            console.log('running action', action);
            dispatch(actionListActions.setRunningStatus(action.index));
            await action.run(armPose);
        }
        console.log('finished running actions');
        dispatch(actionListActions.cleanRunningStatus());
        setRunning(false);
    };

    const handleClick = () => {
        setRunning(prev => !prev);
        runningRef.current = !runningRef.current;
        if (!running) {
            runActions();
        }
    };

    const play_or_stop = running ? (
        <div
            className="absolute bottom-10 right-0 z-20 flex h-14 w-fit cursor-pointer items-center justify-center rounded-md bg-red-400 px-2 hover:bg-red-500"
            onClick={handleClick}
        >
            <StopIcon className="text-3xl text-white" />
            <div className="text-lg text-white"> Stop</div>
        </div>
    ) : (
        <div
            className="absolute bottom-10 right-0 z-20 flex h-14 w-fit cursor-pointer items-center justify-center rounded-md bg-green-400 px-2 hover:bg-green-500"
            onClick={handleClick}
        >
            <PlayArrowIcon className="text-3xl text-white" />
            <div className="text-lg text-white"> Run</div>
        </div>
    );

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
