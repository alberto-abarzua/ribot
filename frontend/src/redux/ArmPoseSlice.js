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
        updateCurrentIsHomed(state, action) {
            state.isHomed = action.payload;
        },
        updateCurrentMoveQueueSize(state, action) {
            state.moveQueueSize = action.payload;
        },
        updateCurrentConnected(state, action) {
            state.connected = action.payload;
        },

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

// export const { updateX, updateY, updateZ, updateRoll, updatePitch, updateYaw, updateToolValue } = armPoseSlice.actions;
export const armPoseActions = armPoseSlice.actions;
export default armPoseSlice.reducer;
