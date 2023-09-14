import armPoseReducer from '@/redux/ArmPose';
import { configureStore } from '@reduxjs/toolkit';

const store = configureStore({
    reducer: {
        armPose: armPoseReducer,
    },
});

export default store;
