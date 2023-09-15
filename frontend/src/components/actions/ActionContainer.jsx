import ToolBar from '@/components/actions/ToolBar';
import { BaseActionObj } from '@/utils/actions';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

import { useSelector } from 'react-redux';

const ActionContainer = () => {
    const actionListSerialized = useSelector(state => state.actionList.actions);
    const actionList = actionListSerialized.map(action => BaseActionObj.fromSerializable(action));

    // const armPose = useSelector(state => state.armPose);

    // const runActions = () => {
    //     //TODO: run actions
    // };

    return (
        <div className="relative flex  h-full w-full flex-col space-y-4 px-2">
            <ToolBar></ToolBar>

            {actionList.map(action => action.render())}

            <div className="absolute -right-20 bottom-10 flex h-14 w-fit cursor-pointer items-center justify-center rounded-md bg-green-400 px-2 hover:bg-green-500">
                <div className="text-lg text-white"> Run</div>
                <PlayArrowIcon className="text-4xl text-white"></PlayArrowIcon>
            </div>
        </div>
    );
};

export default ActionContainer;
