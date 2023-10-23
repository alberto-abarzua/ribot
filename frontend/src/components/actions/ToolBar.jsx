import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { actionListActions } from '@/redux/ActionListSlice';
import { MoveActionObj, ToolActionObj, SleepActionObj } from '@/utils/actions';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import BuildIcon from '@mui/icons-material/Build';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize';
import GamesIcon from '@mui/icons-material/Games';
import LayersClearIcon from '@mui/icons-material/LayersClear';
import MoreVertIcon from '@mui/icons-material/MoreVert';

import { useDispatch, useSelector } from 'react-redux';

const ToolBar = () => {
    const dispatch = useDispatch();
    const actionList = useSelector(state => state.actionList.actions);

    const currentPose = useSelector(state => state.armPose);

    const addMoveAction = () => {
        let index = actionList.length;
        let value = {
            x: currentPose.x,
            y: currentPose.y,
            z: currentPose.z,
            roll: currentPose.roll,
            pitch: currentPose.pitch,
            yaw: currentPose.yaw,
        };
        let obj = new MoveActionObj(value, index);
        dispatch(actionListActions.addAction(obj.toSerializable()));
    };

    const addSleepAction = () => {
        let index = actionList.length;
        let value = {
            duration: 2,
        };
        let obj = new SleepActionObj(value, index);
        dispatch(actionListActions.addAction(obj.toSerializable()));
    };

    const addToolAction = () => {
        let index = actionList.length;
        let value = {
            toolValue: currentPose.toolValue,
        };
        let obj = new ToolActionObj(value, index);
        dispatch(actionListActions.addAction(obj.toSerializable()));
    };

    const clearActionList = () => {
        dispatch(actionListActions.clearActionList());
    };

    const elements = [
        {
            name: 'Move',
            icon: GamesIcon,
            onClick: addMoveAction,
            bgColor: 'bg-action-move',
            hoverColor: 'hover:bg-action-move-hover',
            helpText: 'Move Action: Move to a pose',
        },
        {
            name: 'Sleep',
            icon: BedtimeIcon,
            onClick: addSleepAction,
            bgColor: 'bg-action-sleep',
            hoverColor: 'hover:bg-action-sleep-hover',
            helpText: 'Sleep Action: Pause movement',
        },
        {
            name: 'Tool',
            icon: BuildIcon,
            onClick: addToolAction,
            bgColor: 'bg-action-tool',
            hoverColor: 'hover:bg-action-tool-hover',
            helpText: 'Tool Action: Change tool value',
        },
        {
            name: 'Custom',
            icon: DashboardCustomizeIcon,
            onClick: addToolAction,
            bgColor: 'bg-action-custom',
            hoverColor: 'hover:bg-action-custom-hover',
            helpText: 'Action Set: Set of actions',
        },
    ];

    return (
        <div className="fixed  z-40 mx-auto inline-flex h-14  items-start justify-start overflow-hidden rounded-bl-md rounded-br-md bg-gray-100 shadow">
            {elements.map((action, index) => (
                <>
                    <TooltipProvider>
                        <Tooltip delayDuration={300}>
                            <TooltipTrigger>
                                <div
                                    key={index}
                                    className={`flex h-14 w-20 shrink grow basis-0 items-center justify-center gap-2.5 ${action.bgColor} ${action.hoverColor}`}
                                    onClick={action.onClick}
                                >
                                    <div className="relative flex h-10 w-10 items-center justify-center text-3xl text-white">
                                        <action.icon className="text-3xl"></action.icon>
                                    </div>
                                </div>
                            </TooltipTrigger>

                            <TooltipContent>
                                <p>{action.helpText} </p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                </>
            ))}

            <DropdownMenu>
                <DropdownMenuTrigger
                    as="button"
                    className="flex w-11 items-center justify-center gap-2.5 self-stretch bg-zinc-400 hover:bg-zinc-500"
                >
                    <div className="relative flex h-6 w-6 items-center justify-center text-3xl text-white">
                        <MoreVertIcon className="text-3xl" />
                    </div>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="bg-slate-50">
                    <DropdownMenuLabel> More Options </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                        className="cursor-pointer"
                        onClick={() => {
                            clearActionList();
                        }}
                    >
                        <div className="flex items-center justify-center gap-2.5">
                            <LayersClearIcon className="text-xl text-red-700" />
                            <p className="text-lg">Clear all actions</p>
                        </div>
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        </div>
    );
};

export default ToolBar;
