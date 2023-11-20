import actionListReducer from '@/redux/ActionListSlice';
import armPoseReducer from '@/redux/ArmPoseSlice';
import activityReducer from '@/redux/ActivitySlice';
import rootSaga from '@/redux/sagas';
import { configureStore } from '@reduxjs/toolkit';
import createSagaMiddleware from 'redux-saga';

const sagaMiddleware = createSagaMiddleware();

const store = configureStore({
    reducer: {
        armPose: armPoseReducer,
        actionList: actionListReducer,
        activity: activityReducer,
    },
    middleware: getDefaultMiddleware => getDefaultMiddleware().prepend(sagaMiddleware),
});

sagaMiddleware.run(rootSaga);

export default store;
