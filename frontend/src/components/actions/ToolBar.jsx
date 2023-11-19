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
import { ActionTypes, getActionForDownload } from '@/utils/actions';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import BuildIcon from '@mui/icons-material/Build';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize';
import DownloadIcon from '@mui/icons-material/Download';
import GamesIcon from '@mui/icons-material/Games';
import LayersClearIcon from '@mui/icons-material/LayersClear';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

const ToolBar = () => {
    const dispatch = useDispatch();
    const actionList = useSelector(state => state.actionList.actions);
    const byId = useSelector(state => state.actionList.byId);
    const [url, setUrl] = useState(null);

    useEffect(() => {
        let actionsForDownload = [];
        for (let action of actionList) {
            let updatedAction = byId[action.id];
            const actionForDownload = getActionForDownload(updatedAction);
            actionsForDownload.push(actionForDownload);
        }
        const stringified = JSON.stringify({ base: actionsForDownload });
        const blob = new Blob([stringified], { type: 'application/json' });
        setUrl(window.URL.createObjectURL(blob));
    }, [actionList, byId]);

    const currentPose = useSelector(state => state.armPose);

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
            hovercolor: 'hover:bg-action-move-hover',
            helpText: 'Move Addction: Move to a pose (Uses current pose as base)',
        },
        {
            name: 'Sleep',
            icon: BedtimeIcon,
            bgColor: 'bg-action-sleep',
            type: ActionTypes.SLEEP,
            value: { duration: 2 },
            hovercolor: 'hover:bg-action-sleep-hover',
            helpText: 'Sleep Action: Pause movement',
        },
        {
            name: 'Tool',
            icon: BuildIcon,
            bgColor: 'bg-action-tool',
            type: ActionTypes.TOOL,
            value: { toolValue: currentPose.toolValue },
            hovercolor: 'hover:bg-action-tool-hover',
            helpText: 'Tool Action: Will use current tool value',
        },
        {
            name: 'Custom',
            icon: DashboardCustomizeIcon,
            bgColor: 'bg-action-set',
            type: ActionTypes.ACTIONSET,
            value: [],
            hovercolor: 'hover:bg-action-set-hover',
            helpText: 'Action Set: Set of actions',
        },
    ];

    const clearActionList = () => {
        dispatch(actionListActions.clearActionList());
    };

    const menuItems = [
        {
            label: (
                <a className="w-full" href={url} download={`complete_list.json`}>
                    Download
                </a>
            ),
            icon: <DownloadIcon />,
            onClick: () => {},
        },
        { label: 'Clear All Actions', icon: <LayersClearIcon />, onClick: clearActionList },
    ];

    return (
        <div className="fixed  z-30 mx-auto inline-flex h-14  items-start justify-start overflow-hidden rounded-bl-md rounded-br-md bg-gray-100 shadow">
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
                <DropdownMenuContent className="w-40 bg-slate-50">
                    <DropdownMenuLabel> More Options </DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    {menuItems.map((item, index) => {
                        return (
                            <DropdownMenuItem onClick={item.onClick} key={index}>
                                <div className="flex w-full cursor-pointer items-center justify-between">
                                    {item.label}
                                    <div className="">{item.icon}</div>
                                </div>
                            </DropdownMenuItem>
                        );
                    })}
                </DropdownMenuContent>
            </DropdownMenu>
        </div>
    );
};

export default ToolBar;
