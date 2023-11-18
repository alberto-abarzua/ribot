import { armPoseActions } from '@/redux/ArmPoseSlice';
import api from '@/utils/api';
import instanciatorApi from '@/utils/instanciator_api';
import { call, put, delay, all } from 'redux-saga/effects';

function* callHealthCheck() {
    try {
        let instanciatorUrl = import.meta.env.VITE_INSTANCIATOR_URL;
        console.log('instanciatorUrl', instanciatorUrl);

        if (instanciatorUrl && instanciatorUrl !== 'undefined') {
            try {
                yield call(instanciatorApi.get, '/health_check/');
            } catch (error) {}
        }
    } catch (error) {
        console.error('Error calling healthcheck', error);
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

function* watchCallHealthCheck() {
    while (true) {
        yield call(callHealthCheck);

        yield delay(1000 * 60);
    }
}

function* watchFetchApiData() {
    while (true) {
        yield call(fetchApiData);
        yield delay(400);
    }
}

export default function* rootSaga() {
    yield all([watchFetchApiData(), watchCallHealthCheck()]);

}
