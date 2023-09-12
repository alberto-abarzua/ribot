import ToolBar from '@/components/actions/ToolBar';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

import update from 'immutability-helper';
import { useCallback, useState } from 'react';

import MoveAction from './MoveAction';
import SleepAction from './SleepAction';
import ToolAction from './ToolAction';

const ActionContainer = () => {
    const [actions, setActions] = useState([
        {
            id: 1,
            action_type: 'move',
            value: {
                x: 0,
                y: 0,
                z: 0,
                roll: 0,
                pitch: 0,
                yaw: 0,
            },
        },
        {
            id: 2,
            action_type: 'sleep',
            value: {
                duration: 0,
            },
        },
        {
            id: 3,
            action_type: 'tool',
            value: {
                tool: '100',
            },
        },
    ]);

    const moveInListAction = useCallback((dragIndex, hoverIndex) => {
        setActions(prevActions =>
            update(prevActions, {
                $splice: [
                    [dragIndex, 1],
                    [hoverIndex, 0, prevActions[dragIndex]],
                ],
            })
        );
    }, []);

    const renderAction = (action, index) => {
        if (action.action_type === 'move') {
            return (
                <MoveAction
                    key={action.id}
                    index={index}
                    id={action.id}
                    moveInListAction={moveInListAction}
                    value={action.value} // Adjusted this line
                ></MoveAction>
            );
        } else if (action.action_type === 'sleep') {
            return (
                <SleepAction
                    key={action.id}
                    index={index}
                    id={action.id}
                    value={action.value} // Adjusted this line
                    moveInListAction={moveInListAction}
                ></SleepAction>
            );
        } else if (action.action_type === 'tool') {
            return (
                <ToolAction
                    key={action.id}
                    index={index}
                    id={action.id}
                    value={action.value} // Adjusted this line
                    moveInListAction={moveInListAction}
                ></ToolAction>
            );
        }
    };

    return (
        <div className="relative flex  h-full w-full flex-col space-y-4 px-2">
            <ToolBar></ToolBar>
            {actions.map((action, i) => renderAction(action, i))}

            <div className="absolute -right-20 bottom-10 flex h-14 w-fit cursor-pointer items-center justify-center rounded-md bg-green-400 px-2 hover:bg-green-500">
                <div className="text-lg text-white"> Run</div>
                <PlayArrowIcon className="text-4xl text-white"></PlayArrowIcon>
            </div>
        </div>
    );
};

export default ActionContainer;
