import ToolBarElement from './ToolBarElement';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { actionListActions } from '@/redux/ActionListSlice';
import { ActionTypes } from '@/utils/actions';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import BuildIcon from '@mui/icons-material/Build';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize';
import GamesIcon from '@mui/icons-material/Games';
import LayersClearIcon from '@mui/icons-material/LayersClear';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { useDispatch, useSelector } from 'react-redux';

const ToolBar = () => {
    const dispatch = useDispatch();

    const currentPose = useSelector(state => state.armPose);

    const clearActionList = () => {
        dispatch(actionListActions.clearActionList());
    };

    const moveValue = {
        x: currentPose.x,
        y: currentPose.y,
        z: currentPose.z,
        roll: currentPose.roll,
        pitch: currentPose.pitch,
        yaw: currentPose.yaw,
    };

    const elements = [
        {
            name: 'Move',
            icon: GamesIcon,
            bgColor: 'bg-action-move',
            type: ActionTypes.MOVE,
            value: moveValue,
            hoverColor: 'hover:bg-action-move-hover',
            helpText: 'Move Addction: Move to a pose',
        },
        {
            name: 'Sleep',
            icon: BedtimeIcon,
            bgColor: 'bg-action-sleep',
            type: ActionTypes.SLEEP,
            value: { duration: 2 },
            hoverColor: 'hover:bg-action-sleep-hover',
            helpText: 'Sleep Action: Pause movement',
        },
        {
            name: 'Tool',
            icon: BuildIcon,
            bgColor: 'bg-action-tool',
            type: ActionTypes.TOOL,
            value: { toolValue: 0 },
            hoverColor: 'hover:bg-action-tool-hover',
            helpText: 'Tool Action: Change tool value',
        },
        {
            name: 'Custom',
            icon: DashboardCustomizeIcon,
            bgColor: 'bg-action-set',
            type: ActionTypes.ACTIONSET,
            value: [],
            hoverColor: 'hover:bg-action-set-hover',
            helpText: 'Action Set: Set of actions',
        },
    ];

    return (
        <div className="fixed  z-40 mx-auto inline-flex h-14  items-start justify-start overflow-hidden rounded-bl-md rounded-br-md bg-gray-100 shadow">
            {elements.map((element, index) => (
                <ToolBarElement key={index} element={element} />
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
