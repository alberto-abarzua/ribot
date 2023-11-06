import { ActionTypes } from '@/utils/actions';
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    actions: [], // array actions
    byId: {}, // hash table with all actions by id
};

// Action
// {
//    id,
//    value,
//    type,
//    parentId,
//    valid,
//    running,
// }

const getParentList = (state, action) => {
    const { parentId } = action;
    if (parentId === null) {
        return state.actions;
    }
    return state.byId[parentId].value;
};

const actionListSlice = createSlice({
    name: 'actionList',
    initialState,
    reducers: {
        moveAction: (state, action) => {
            const { refActionId, targetActionId, before } = action.payload;
            console.log(
                'Moving action ',
                refActionId % 1000,
                ' to ',
                targetActionId % 1000,
                ' before ',
                before
            );
            // refaction is the action being moved
            // targetAction is the action that refAction is being moved to

            const refAction = state.byId[refActionId];
            const targetAction = state.byId[targetActionId];

            const refActionList = getParentList(state, refAction);
            const targetActionList = getParentList(state, targetAction);

            // remove refAction from refActionList

            const refActionIndex = refActionList.findIndex(action => action.id === refAction.id);

            if (refActionIndex !== -1) {
                refActionList.splice(refActionIndex, 1);
            }

            // insert refAction into targetActionList
            const targetActionIndex = targetActionList.findIndex(
                action => action.id === targetAction.id
            );
            const insertIndex = before ? targetActionIndex : targetActionIndex + 1;
            targetActionList.splice(insertIndex, 0, refAction);

            const targetActionParentList = getParentList(state, targetAction);
            const refActionParentList = getParentList(state, refAction);

            if (targetActionParentList !== refActionParentList) {
                refAction.parentId = targetAction.parentId;
            }
            state.byId[refActionId] = refAction;
        },

        addAction: (state, action) => {
            const { type, parentId, value } = action.payload;
            // if parentId is undefined
            const newAction = {
                id: Date.now(),
                type,
                parentId,
                value,
                valid: true,
                running: false,
            };
            state.byId[newAction.id] = newAction;

            if (parentId !== null) {
                state.byId[parentId].value.push(newAction);
            } else {
                state.actions.push(newAction);
            }
        },

        deleteAction: (state, action) => {
            const { actionId } = action.payload;
            const actionToDelete = state.byId[actionId];
            const actionList = getParentList(state, actionToDelete);
            const actionIndex = actionList.findIndex(action => action.id === actionId);
            if (actionIndex !== -1) {
                actionList.splice(actionIndex, 1);
            }
            delete state.byId[actionId];
        },

        duplicateAction: (state, action) => {
            const { actionId } = action.payload;
            const actionToDuplicate = state.byId[actionId];

            const actionList = getParentList(state, actionToDuplicate);

            const actionIndex = actionList.findIndex(action => action.id === actionId);
            const newAction = {
                ...actionToDuplicate,
                id: Date.now(),
            };
            actionList.splice(actionIndex + 1, 0, newAction);
            state.byId[newAction.id] = newAction;
        },

        setValidStatus: (state, action) => {
            const { actionId, valid } = action.payload;
            state.byId[actionId].valid = valid;
        },

        setRunningStatus: (state, action) => {
            const { actionId, running } = action.payload;
            state.byId[actionId].running = running;
        },

        setActionValue: (state, action) => {
            const { actionId, value } = action.payload;
            state.byId[actionId].value = value;
        },
        pushActionToValue: (state, action) => {
            const { actionId, actionToAddId } = action.payload;
            // make sure the action type is actionset
            const targetAction = state.byId[actionId];
            if (targetAction.type !== ActionTypes.ACTIONSET) {
                console.error('pushActionToValue: action type is not actionset');
                return;
            }
            const ActionToAdd = state.byId[actionToAddId];

            targetAction.value.push(ActionToAdd);
            // delete actionToAdd from its old location
            const actionList = getParentList(state, ActionToAdd);
            const actionIndex = actionList.findIndex(action => action.id === actionToAddId);
            if (actionIndex !== -1) {
                actionList.splice(actionIndex, 1);
            }
            // update parentId

            ActionToAdd.parentId = targetAction.id;
        },

        clearActionList: state => {
            state.actions = [];
            state.byId = {};
        },
    },
});

export const actionListActions = actionListSlice.actions;
export default actionListSlice.reducer;
