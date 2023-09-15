import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    x: 0,
    y: 0,
    z: 0,
    roll: 0,
    pitch: 0,
    yaw: 0,
    toolValue: 0,
    isHomed: false,
    moveQueueSize: 0,
    toMove: {
        x: 0,
        y: 0,
        z: 0,
        roll: 0,
        pitch: 0,
        yaw: 0,
        toolValue: 0,
    },
};

const armPoseSlice = createSlice({
    name: 'armPose',
    initialState,
    reducers: {
        updateX(state, action) {
            state.toMove.x = action.payload;
        },
        updateY(state, action) {
            state.toMove.y = action.payload;
        },
        updateZ(state, action) {
            state.toMove.z = action.payload;
        },
        updateRoll(state, action) {
            state.toMove.roll = action.payload;
        },
        updatePitch(state, action) {
            state.toMove.pitch = action.payload;
        },
        updateYaw(state, action) {
            state.toMove.yaw = action.payload;
        },
        updateToolValue(state, action) {
            state.toMove.toolValue = action.payload;
        },

        update(state, action) {
            state.toMove.x = action.payload.x;
            state.toMove.y = action.payload.y;
            state.toMove.z = action.payload.z;
            state.toMove.roll = action.payload.roll;
            state.toMove.pitch = action.payload.pitch;
            state.toMove.yaw = action.payload.yaw;
            state.toMove.toolValue = action.payload.toolValue;
        },

        updateCurrentX(state, action) {
            state.x = action.payload;
        },
        updateCurrentY(state, action) {
            state.y = action.payload;
        },
        updateCurrentZ(state, action) {
            state.z = action.payload;
        },
        updateCurrentRoll(state, action) {
            state.roll = action.payload;
        },
        updateCurrentPitch(state, action) {
            state.pitch = action.payload;
        },
        updateCurrentYaw(state, action) {
            state.yaw = action.payload;
        },
        updateCurrentToolValue(state, action) {
            state.toolValue = action.payload;
        },
        updateCurrent(state, action) {
            state.x = action.payload.x;
            state.y = action.payload.y;
            state.z = action.payload.z;
            state.roll = action.payload.roll;
            state.pitch = action.payload.pitch;
            state.yaw = action.payload.yaw;
            state.toolValue = action.payload.toolValue;
            state.isHomed = action.payload.isHomed;
            state.moveQueueSize = action.payload.isHomed;
        },
    },
});

// export const { updateX, updateY, updateZ, updateRoll, updatePitch, updateYaw, updateToolValue } = armPoseSlice.actions;
export const armPoseActions = armPoseSlice.actions;
export default armPoseSlice.reducer;
