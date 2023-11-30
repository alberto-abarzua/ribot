import ActionContainer from '@/components/actions/ActionContainer';
import ToolBar from '@/components/actions/ToolBar';
import { Button } from '@/components/ui/button';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { actionListActions } from '@/redux/ActionListSlice';
import { runAction } from '@/utils/actions';
import byIdContext from '@/utils/byIdContext';
import AllInclusiveIcon from '@mui/icons-material/AllInclusive';
import LooksOneIcon from '@mui/icons-material/LooksOne';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';

const ActionPanel = () => {
    const { toast } = useToast();
    const dispatch = useDispatch();

    console.log('rendering action panel');
    const actionSlice = useSelector(state => state.actionList);

    const isHomed = useSelector(state => state.armPose.isHomed);

    const [loop, setLoop] = useState(false);

    const actionList = actionSlice.actions;
    const byId = actionSlice.byId;

    const [running, setRunning] = useState(false);
    const runningRef = useRef(false);

    useEffect(() => {
        runningRef.current = running;
    }, [running]);

    const runActions = async () => {
        for (let action of actionList) {
            if (!runningRef.current) return;

            action = byId[action.id];
            dispatch(actionListActions.setRunningStatus({ actionId: action.id, running: true }));
            if (!action.valid) {
                toast({
                    variant: 'destructive',
                    title: 'Error in action!',
                    description: 'The position you are trying to move to is out of bounds.',
                });
                break;
            }
            await runAction(action, dispatch);

            dispatch(actionListActions.setRunningStatus({ actionId: action.id, running: false }));
        }

        if (loop) {
            await runActions();
        }
        setRunning(false);
    };

    const handleClickPlayStop = () => {
        setRunning(prev => !prev);
        runningRef.current = !runningRef.current;
        if (!running) {
            runActions();
        }
    };

    const playSelectValueChange = value => {
        if (value === 'loop') {
            setLoop(true);
        }
        if (value === 'once') {
            setLoop(false);
        }
    };

    return (
        <byIdContext.Provider value={byId}>
            <div className="relative m-0 flex h-full max-h-screen w-full flex-col items-center space-y-4 ">
                <ToolBar />
                <div className="flex h-full max-h-screen w-full flex-col items-center gap-4 overflow-y-auto pt-14">
                    <ActionContainer actionList={actionList} />
                </div>
                <div className="absolute bottom-10 right-8 z-20">
                    {running ? (
                        <Button variant="destructive" onClick={handleClickPlayStop}>
                            <StopIcon className="text-3xl text-white" />
                            <div className="text-lg text-white"> Stop</div>
                        </Button>
                    ) : (
                        <Button onClick={handleClickPlayStop} disabled={!isHomed}>
                            <PlayArrowIcon className="text-3xl text-white" />
                            <div className="text-lg text-white"> Play</div>

                            <Select
                                onValueChange={playSelectValueChange}
                                value={loop ? 'loop' : 'once'}
                                className="border-red border bg-red-100"
                            >
                                <SelectTrigger className="relative left-4 border-none border-input bg-transparent  outline-none ring-transparent focus:border-none focus:outline-none  focus:ring-transparent ">
                                    <SelectValue placeholder="" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="loop">
                                        Loop
                                        <AllInclusiveIcon className="ml-1 scale-75 transform"></AllInclusiveIcon>
                                    </SelectItem>
                                    <SelectItem value="once">
                                        Once
                                        <LooksOneIcon className="ml-1 scale-75 transform"></LooksOneIcon>
                                    </SelectItem>
                                </SelectContent>
                            </Select>
                        </Button>
                    )}
                </div>
            </div>
        </byIdContext.Provider>
    );
};

export default ActionPanel;
