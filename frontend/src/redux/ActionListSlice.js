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
//    name,
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
            let { refActionId, targetActionId, before } = action.payload;

            // refaction is the action being moved
            // targetAction is the action that refAction is being moved to

            let refAction = state.byId[refActionId];
            const targetAction = state.byId[targetActionId];

            if (!refAction) {
                const { type, value } = action.payload;
                const newAction = {
                    id: refActionId,
                    type,
                    parentId: targetAction.parentId,
                    value,
                    valid: true,
                    running: false,
                };
                state.byId[newAction.id] = newAction;
                refAction = newAction;
                refActionId = newAction.id;
                //updte the parent list
                const parentList = getParentList(state, refAction);
                parentList.push(refAction);
            }

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

            // Deep clone the action
            let newAction = JSON.parse(JSON.stringify(actionToDuplicate));

            // Helper function to generate a unique ID

            // Recursively update id, parentId, and state.byId
            let id_offset = 0;
            const updateHelper = (actionToUpdate, newParentId) => {
                const newId = Date.now() + id_offset;
                id_offset++;
                actionToUpdate.id = newId;
                actionToUpdate.parentId = newParentId;
                state.byId[newId] = actionToUpdate;
                if (actionToUpdate.type === ActionTypes.ACTIONSET) {
                    for (let subactionToUpdate of actionToUpdate.value) {
                        updateHelper(subactionToUpdate, newId);
                    }
                }
            };

            updateHelper(newAction, actionToDuplicate.parentId);

            actionList.splice(actionIndex + 1, 0, newAction);
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

        setActionName: (state, action) => {
            const { actionId, name } = action.payload;
            state.byId[actionId].name = name;
        },

        pushActionToValue: (state, action) => {
            let { actionId, actionToAddId } = action.payload;

            let targetList = state.actions;
            let targetActionId = null;
            if (actionId) {
                targetList = state.byId[actionId].value;
                targetActionId = actionId;
            }

            let actionToAdd = state.byId[actionToAddId];

            // check if actionToAdd exits

            if (!actionToAdd) {
                const { type, value } = action.payload;
                const newAction = {
                    id: actionToAddId,
                    type,
                    parentId: targetActionId,
                    value,
                    valid: true,
                    running: false,
                };

                state.byId[newAction.id] = newAction;

                actionToAdd = newAction;
                actionToAddId = newAction.id;
                targetList.push(actionToAdd);
            } else {
                targetList.push(actionToAdd);

                // delete actionToAdd from its old location
                const actionList = getParentList(state, actionToAdd);
                const actionIndex = actionList.findIndex(action => action.id === actionToAddId);
                if (actionIndex !== -1) {
                    actionList.splice(actionIndex, 1);
                }
                // update parentId

                actionToAdd.parentId = targetActionId;
            }
        },

        clearActionList: state => {
            state.actions = [];
            state.byId = {};
        },
    },
});

export const actionListActions = actionListSlice.actions;
export default actionListSlice.reducer;
