import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    x: 0,
    y: 0,
    z: 0,
    roll: 0,
    pitch: 0,
    yaw: 0,
    connected: false,
    toolValue: 0,
    isHomed: false,
    status: 0,
    moveQueueSize: 0,
    currentAngles: [0, 0, 0, 0, 0, 0],
};

const armPoseSlice = createSlice({
    name: 'armPose',
    initialState,
    reducers: {
        updateCurrent(state, action) {
            if (state.x !== action.payload.x) {
                state.x = action.payload.x;
            }
            if (state.y !== action.payload.y) {
                state.y = action.payload.y;
            }
            if (state.z !== action.payload.z) {
                state.z = action.payload.z;
            }
            if (state.roll !== action.payload.roll) {
                state.roll = action.payload.roll;
            }
            if (state.pitch !== action.payload.pitch) {
                state.pitch = action.payload.pitch;
            }
            if (state.yaw !== action.payload.yaw) {
                state.yaw = action.payload.yaw;
            }
            if (state.toolValue !== action.payload.toolValue) {
                state.toolValue = action.payload.toolValue;
            }
            if (state.isHomed !== action.payload.isHomed) {
                state.isHomed = action.payload.isHomed;
            }
            if (state.moveQueueSize !== action.payload.moveQueueSize) {
                state.moveQueueSize = action.payload.moveQueueSize;
            }
            if (state.currentAngles !== action.payload.currentAngles) {
                state.currentAngles = action.payload.currentAngles;
            }
            if (state.connected !== action.payload.connected) {
                state.connected = action.payload.connected;
            }
            if (state.status !== action.payload.status) {
                state.status = action.payload.status;
            }
        },
    },
});

export const armPoseActions = armPoseSlice.actions;
export default armPoseSlice.reducer;
