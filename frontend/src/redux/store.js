import actionListReducer from '@/redux/ActionListSlice';
import armPoseReducer from '@/redux/ArmPoseSlice';
import { configureStore } from '@reduxjs/toolkit';
const store = configureStore({
    reducer: {
        armPose: armPoseReducer,
        actionList: actionListReducer,
    },
});

export default store;
