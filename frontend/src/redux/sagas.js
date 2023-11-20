import { armPoseActions } from '@/redux/ArmPoseSlice';
import api from '@/utils/api';
import instanciatorApi from '@/utils/instanciator_api';
import { call, put, delay, all, select } from 'redux-saga/effects';
import { evaluateStepMap, activityActions } from '@/redux/ActivitySlice';

function* callHealthCheck() {
    try {
        let instanciatorUrl = import.meta.env.VITE_INSTANCIATOR_URL;

        if (instanciatorUrl && instanciatorUrl !== 'undefined') {
            try {
                yield call(instanciatorApi.get, '/health_check/');
            } catch (error) {
                console.error('Error calling instanciator healthcheck', error);
            }
        }
    } catch (error) {
        console.error('Error calling healthcheck', error);
    }
}

function* watchCallHealthCheck() {
    while (true) {
        yield call(callHealthCheck);

        yield delay(1000 * 60);
    }
}

function* storeState(state) {
    try {
        const serializedState = JSON.stringify(state);
        console.log('Saving state:')
        localStorage.setItem('state', serializedState);
    } catch (e) {
        console.warn('Failed to save state:', e);
    }
}

const selectAllState = state => state;

function* watchStoreState() {
    while (true) {
        const state = yield select(selectAllState);
        yield call(storeState, state);
        yield delay(1000 * 3);
    }
}

function* fetchApiData() {
    try {
        const response = yield call(api.get, '/settings/status/?degrees=true');
        yield put(armPoseActions.updateCurrent(response.data));
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function* watchFetchApiData() {
    while (true) {
        yield call(fetchApiData);
        yield delay(400);
    }
}

function* verifyActivitySteps() {
    const state = yield select(selectAllState);
    const steps = state.activity.steps;

    for (let step of steps) {
        if (!step.completion.done) {
            let stepDone = false;
            try {
                stepDone = evaluateStepMap[step.id](state);
            } catch (error) {
                console.error('Error evaluating step', error);
            }
            if (stepDone) {
                yield put(activityActions.setDone({ stepId: step.id }));
            }
            break;
        }
    }
}

function* watchVerifyActivitySteps() {
    while (true) {
        yield call(verifyActivitySteps);
        yield delay(1000);
    }
}

export default function* rootSaga() {
    yield all([
        watchFetchApiData(),
        watchCallHealthCheck(),
        watchStoreState(),
        watchVerifyActivitySteps(),
    ]);
}
