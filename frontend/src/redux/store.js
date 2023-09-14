import { configureStore } from '@reduxjs/toolkit';
import armPoseReducer from '@/redux/ArmPose';

const store = configureStore({
    reducer: {
        armPose: armPoseReducer,
    },
});

export default store;
