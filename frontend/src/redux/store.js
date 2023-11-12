import actionListReducer from '@/redux/ActionListSlice';
import armPoseReducer from '@/redux/ArmPoseSlice';
import rootSaga from '@/redux/sagas';
import { configureStore } from '@reduxjs/toolkit';
import createSagaMiddleware from 'redux-saga';

const saveState = state => {
    try {
        const serializedState = JSON.stringify(state);
        localStorage.setItem('state', serializedState);
    } catch (e) {
        console.warn('Failed to save state:', e);
    }
};
const debounce = (func, wait) => {
    let lastCallTime;

    return function (...args) {
        const now = Date.now();
        if (!lastCallTime || now - lastCallTime >= wait) {
            lastCallTime = now;
            func.apply(this, args);
        }
    };
};

const saveStateDebounced = debounce(saveState, 1000);

const localStorageMiddleware = store => next => action => {
    const result = next(action);
    saveStateDebounced(store.getState());
    return result;
};

const loadState = () => {
    try {
        const serializedState = localStorage.getItem('state');
        if (serializedState === null) {
            return undefined; // No saved state, use initial state
        }
        return JSON.parse(serializedState);
    } catch (e) {
        return undefined; // Errors should lead to using initial state
    }
};

const sagaMiddleware = createSagaMiddleware();

const preloadedState = loadState();

const store = configureStore({
    reducer: {
        armPose: armPoseReducer,
        actionList: actionListReducer,
    },
    middleware: getDefaultMiddleware =>
        getDefaultMiddleware().prepend(sagaMiddleware, localStorageMiddleware),
    preloadedState,
});

sagaMiddleware.run(rootSaga);

export default store;
