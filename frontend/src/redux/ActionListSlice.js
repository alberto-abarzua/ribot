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
    },
});

export const actionListActions = actionListSlice.actions;
export default actionListSlice.reducer;
