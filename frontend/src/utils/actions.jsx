import ActionSet from '@/components/actions/ActionSet';
import MoveAction from '@/components/actions/MoveAction';
import SleepAction from '@/components/actions/SleepAction';
import ToolAction from '@/components/actions/ToolAction';
import { actionListActions } from '@/redux/ActionListSlice';
import api from '@/utils/api';

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
        try {
            await api.post('/move/pose/', pose);
        } catch (err) {
            console.log(err);
        }
    },
    [ActionTypes.SLEEP]: async action => {
        let duration = action.value.duration;
        const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
        const duration_ms = duration * 1000;
        await sleep(duration_ms);
    },
    [ActionTypes.TOOL]: async action => {
        let target = {
            toolValue: action.value.toolValue,
            wait: true,
        };
        try {
            await api.post('/move/tool/', target);
        } catch (err) {
            console.log(err);
        }
    },
    [ActionTypes.ACTIONSET]: async (action, dispatch) => {
        for (let subAction of action.value) {
            dispatch(actionListActions.setRunningStatus({ actionId: subAction.id, running: true }));
            await runAction(subAction, dispatch);
            dispatch(
                actionListActions.setRunningStatus({ actionId: subAction.id, running: false })
            );
        }
    },
};

const runAction = async (action, dispatch) => {
    const handler = actionHandlers[action.type];
    if (handler) {
        await handler(action, dispatch);
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

    return Component ? (
        <Component key={action.id} id={action.id} action={action}></Component>
    ) : null;
};

const getActionForDownload = action => {
    const stringifiedAction = JSON.stringify(action);
    const newAction = JSON.parse(stringifiedAction);
    const remover_helper = action => {
        delete action.id;
        delete action.parentId;
        delete action.running;
        delete action.valid;
        if (action.type === ActionTypes.ACTIONSET) {
            action.value.forEach(subAction => {
                remover_helper(subAction);
            });
        }
    };
    remover_helper(newAction);
    return newAction;
};

export { ActionTypes, getActionForDownload, runAction, renderAction };
