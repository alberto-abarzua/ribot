import { createSlice } from '@reduxjs/toolkit';

import update from 'immutability-helper';
const initialState = {
    actions: [],
};

const actionListSlice = createSlice({
    name: 'actionList',
    initialState,
    reducers: {
        addAction(state, action) {
            action.payload.index = state.actions.length;
            state.actions.push(action.payload);
        },
        updateValueByIndex(state, action) {
            state.actions[action.payload.index].value = action.payload.value;
        },
        moveInList(state, action) {
            let dragIndex = action.payload.dragIndex;
            let hoverIndex = action.payload.hoverIndex;
            const updatedList = update(state.actions, {
                $splice: [
                    [dragIndex, 1],
                    [hoverIndex, 0, state.actions[dragIndex]],
                ],
            });

            state.actions = updatedList;
            for (let i = 0; i < state.actions.length; i++) {
                state.actions[i].index = i;
            }
        },
        deleteAction(state, action) {
            state.actions.splice(action.payload, 1);
            for (let i = 0; i < state.actions.length; i++) {
                state.actions[i].index = i;
            }
        },
        setRunningStatus(state, action) {
            state.actions[action.payload].running = true;
            //set all other to false
            for (let i = 0; i < state.actions.length; i++) {
                if (i !== action.payload) {
                    state.actions[i].running = false;
                }
            }
        },
        cleanRunningStatus(state) {
            for (let i = 0; i < state.actions.length; i++) {
                state.actions[i].running = false;
            }
        },
    },
});

export const actionListActions = actionListSlice.actions;
export default actionListSlice.reducer;
