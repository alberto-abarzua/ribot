import ActionSet from '@/components/actions/ActionSet';
import MoveAction from '@/components/actions/MoveAction';
import SleepAction from '@/components/actions/SleepAction';
import ToolAction from '@/components/actions/ToolAction';
import api from '@/utils/api';
import update from 'immutability-helper';

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

const clearActionList = actionList => {
    actionList.length = 0;
};

const updatePosition = (actionList, hoverId, dragId) => {
    let dragIndex = getById(actionList, dragId).index;
    let hoverIndex = getById(actionList, hoverId).index;

    const updatedList = update(actionList, {
        $splice: [
            [dragIndex, 1],
            [hoverIndex, 0, getById(actionList, dragId)],
        ],
    });

    for (let i = 0; i < updatedList.length; i++) {
        updatedList[i].index = i;
    }

    actionList = updatedList;
};

const addAction = (actionList, type, value) => {
    let new_action = {
        id: Date.now(),
        index: 0,
        type: type,
        value: value,
        valid: false,
        running: false,
    };
    actionList.push(new_action);
};

const deleteAction = (actionList, id) => {
    const index = actionList.findIndex(action => action.id === id);
    if (index === -1) {
        return;
    }
    actionList.splice(index, 1);
};

const duplicateAction = (actionList, id) => {
    let action = getById(actionList, id);

    let new_action = {
        id: Date.now(),
        index: action.index + 1,
        type: action.type,
        value: action.value,
        valid: false,
        running: false,
    };
    actionList.splice(action.index + 1, 0, new_action);
    for (let i = action.index + 2; i < actionList.length; i++) {
        actionList[i].index = i;
    }
};

const renderAction = (action, actionList, setActionList) => {
    const components = {
        [ActionTypes.MOVE]: MoveAction,
        [ActionTypes.SLEEP]: SleepAction,
        [ActionTypes.TOOL]: ToolAction,
        [ActionTypes.ACTIONSET]: ActionSet,
    };

    const Component = components[action.type];

    return Component ? (
        <Component
            key={action.id}
            index={action.index}
            id={action.id}
            value={action.value}
            actionList={actionList}
            setActionList={setActionList}
        ></Component>
    ) : null;
};

const getById = actionList => {
    return id => {
        return actionList.find(action => action.id === id);
    };
};

const idInList = actionList => {
    return id => {
        return actionList.some(action => action.id === id);
    };
};

export {
    ActionTypes,
    addAction,
    runAction,
    renderAction,
    getById,
    idInList,
    deleteAction,
    duplicateAction,
    clearActionList,
    updatePosition,
};
