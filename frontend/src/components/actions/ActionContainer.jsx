import ToolBar from '@/components/actions/ToolBar';
import { actionListActions } from '@/redux/ActionListSlice';
import { BaseActionObj } from '@/utils/actions';
import ErrorIcon from '@mui/icons-material/Error';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Button } from '@/components/ui/button';

const ActionContainer = () => {
    const actionListSerialized = useSelector(state => state.actionList.actions);
    const actionList = actionListSerialized.map(action => BaseActionObj.fromSerializable(action));
    const armPose = useSelector(state => state.armPose);

    const [running, setRunning] = useState(false);
    const runningRef = useRef(false);

    const dispatch = useDispatch();

    let valid = true;

    for (const action of actionListSerialized) {
        if (!action.valid) {
            valid = false;
            break;
        }
    }

    useEffect(() => {
        runningRef.current = running;
    }, [running]);

    const runActions = async () => {
        for (const action of actionList) {
            if (!runningRef.current) {
                break;
            }
            dispatch(actionListActions.setRunningStatus(action.index));
            await action.run(armPose);
        }
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

    let play_or_stop = {
        icon: null,
        color: null,
        hoverColor: null,
        text: null,
    };
    if (valid) {
        if (running) {
            play_or_stop.icon = <StopIcon className="text-3xl text-white" />;
            play_or_stop.color = 'bg-red-400';
            play_or_stop.hoverColor = 'hover:bg-red-500';
            play_or_stop.text = 'Stop';
        } else {
            play_or_stop.icon = <PlayArrowIcon className="text-3xl text-white" />;
            play_or_stop.color = 'bg-green-400';
            play_or_stop.hoverColor = 'hover:bg-green-500';
            play_or_stop.text = 'Run';
        }
    } else {
        // error
        play_or_stop.icon = <ErrorIcon className="text-3xl text-white" />;
        play_or_stop.color = 'bg-orange-400';
        play_or_stop.hoverColor = 'hover:bg-orange-500';
        play_or_stop.text = 'Errors';
    }
    return (
        <div className="relative m-0 flex h-full max-h-screen w-full flex-col items-center space-y-4 ">
            <ToolBar />
            <div className="flex h-full max-h-screen w-full flex-col items-center gap-4 overflow-y-auto pt-14">
                {actionList.map(action => action.render())}
            </div>
            <div className="absolute bottom-10 right-8 z-20">
                <Button
                    color={play_or_stop.color}
                    hoverColor={play_or_stop.hoverColor}
                    onClick={handleClick}
                    disabled={!valid}
                >
                    {play_or_stop.icon}
                    <div className="text-lg text-white"> {play_or_stop.text}</div>
                </Button>
            </div>
        </div>
    );
};

export default ActionContainer;
