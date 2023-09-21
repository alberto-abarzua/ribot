import { actionListActions } from '@/redux/ActionListSlice';
import { MoveActionObj, ToolActionObj, SleepActionObj } from '@/utils/actions';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import BuildIcon from '@mui/icons-material/Build';
import GamesIcon from '@mui/icons-material/Games';
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

    return (
        <div className="mx-auto inline-flex h-14 w-64 items-start justify-start overflow-hidden rounded-bl-md rounded-br-md bg-gray-100 shadow">
            <div
                className="flex h-14 shrink grow basis-0 items-center justify-center gap-2.5 bg-slate-500 hover:bg-slate-600"
                onClick={addMoveAction}
            >
                <div className="relative flex h-10 w-10 items-center justify-center text-3xl text-white">
                    <GamesIcon className="text-3xl"></GamesIcon>
                </div>
            </div>

            <div
                className="flex h-14 shrink grow basis-0 items-center justify-center gap-2.5 bg-rose-400 hover:bg-rose-500"
                onClick={addSleepAction}
            >
                <div className="relative flex h-10 w-10 items-center justify-center text-3xl text-white">
                    <BedtimeIcon className="text-3xl"></BedtimeIcon>
                </div>
            </div>
            <div
                className="flex h-14 shrink grow basis-0 items-center justify-center gap-2.5 bg-yellow-200 hover:bg-yellow-300"
                onClick={addToolAction}
            >
                <div className="relative flex h-10 w-10 items-center justify-center text-3xl text-white">
                    <BuildIcon className="text-3xl"></BuildIcon>
                </div>
            </div>
            <div className="flex w-11 items-center justify-center gap-2.5 self-stretch bg-zinc-400 hover:bg-zinc-500">
                <div className="relative flex h-6 w-6 items-center justify-center text-3xl text-white">
                    <MoreVertIcon className="text-3xl"> </MoreVertIcon>
                </div>
            </div>
        </div>
    );
};

export default ToolBar;
