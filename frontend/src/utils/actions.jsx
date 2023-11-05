import ActionSet from '@/components/actions/ActionSet';
import MoveAction from '@/components/actions/MoveAction';
import SleepAction from '@/components/actions/SleepAction';
import ToolAction from '@/components/actions/ToolAction';
import api from '@/utils/api';
import { generateUniqueId } from '@/utils/idManager';

const ActionTypes = {
    MOVE: 'move',
    SLEEP: 'sleep',
    TOOL: 'tool',
    ACTIONSET: 'actionset',
};

const actionHandlers = {
    [ActionTypes.MOVE]: async action => {
        let pose = {
            x: action.value.x,
            y: action.value.y,
            z: action.value.z,
            roll: action.value.roll,
            pitch: action.value.pitch,
            yaw: action.value.yaw,
            wait: true,
        };
        await api.post('/move/pose/move/', pose);
    },
    [ActionTypes.SLEEP]: async action => {
        let duration = action.value.duration;
        await action.sleep(duration);
    },
    [ActionTypes.TOOL]: async action => {
        let target = {
            toolValue: action.value.toolValue,
            wait: true,
        };
        await api.post('/move/tool/move/', target);
    },
    [ActionTypes.ACTIONSET]: async action => {
        for (let subAction of action.value) {
            await subAction.run();
        }
    },
};

const runAction = async action => {
    const handler = actionHandlers[action.type];
    if (handler) {
        await handler(action);
    } else {
        throw new Error('Invalid action type');
    }
};

const renderAction = action => {
    const components = {
        [ActionTypes.MOVE]: MoveAction,
        [ActionTypes.SLEEP]: SleepAction,
        [ActionTypes.TOOL]: ToolAction,
        [ActionTypes.ACTIONSET]: ActionSet,
    };

    const Component = components[action.type];

    return Component ? <Component key={action.id} id={action.id}></Component> : null;
};

export { ActionTypes, runAction, renderAction };
