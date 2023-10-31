import { createSlice } from '@reduxjs/toolkit';
import { generateUniqueId } from '@/utils/idManager';
import { getById } from '@/utils/actions';

import update from 'immutability-helper';
const initialState = {
    actions: [],
};

const actionListSlice = createSlice({
    name: 'actionList',
    initialState,
    reducers: {
        // New Action Operations

        addAction(state, action) {
            let new_action = {
                value: action.payload.value,
                type: action.payload.type,
                id: generateUniqueId(),
                index: state.actions.length,
                running: false,
                parent: -1,
                valid: true,
            };
            state.actions.push(new_action);
        },

        // Existing Action Operations

        clearActionList(state) {
            state.actions = [];
        },

        updateValueById(state, action) {
            getById(state.actions, action.payload.id).value = action.payload.value;
        },

        moveInList(state, action) {
            let dragId = action.payload.dragId;
            let hoverId = action.payload.hoverId;
            let dragIndex = getById(state.actions, dragId).index;
            let hoverIndex = getById(state.actions, hoverId).index;
            const updatedList = update(state.actions, {
                $splice: [
                    [dragIndex, 1],
                    [hoverIndex, 0, getById(state.actions, dragId)],
                ],
            });

            state.actions = updatedList;
            for (let i = 0; i < state.actions.length; i++) {
                state.actions[i].index = i;
            }
        },

        duplicateAction(state, action) {
            let id = action.payload;
            let newAction = getById(state.actions, id);
            newAction = JSON.parse(JSON.stringify(newAction));
            newAction.id = generateUniqueId();
            state.actions.push(newAction);
        },

        deleteAction(state, action) {
            let id = action.payload;
            let index = getById(state.actions, id).index;
            state.actions.splice(index, 1);
            for (let i = 0; i < state.actions.length; i++) {
                state.actions[i].index = i;
            }
        },

        // Action Status

        setRunningStatus(state, action) {
            let id = action.payload;
            getById(state.actions, id).running = true;
            for (let i = 0; i < state.actions.length; i++) {
                if (state.actions[i].id !== id) {
                    state.actions[i].running = false;
                }
            }
        },

        cleanRunningStatus(state) {
            for (let i = 0; i < state.actions.length; i++) {
                state.actions[i].running = false;
            }
        },
        setValidStatus(state, action) {
            let id = action.payload.id;
            getById(state.actions, id).valid = action.payload.valid;
        },
    },
});

export const actionListActions = actionListSlice.actions;
export default actionListSlice.reducer;
