import { armPoseActions } from '@/redux/ArmPoseSlice';
import api from '@/utils/api';
import instanciatorApi from '@/utils/instanciator_api';
import { call, put, delay, all } from 'redux-saga/effects';

function* fetchApiData() {
    try {
        // if in the server return

        let instanciatorUrl = import.meta.env.VITE_INSTANCIATOR_URL;
        console.log('instanciatorUrl', instanciatorUrl);

        if (instanciatorUrl && instanciatorUrl !== 'undefined') {
            try {
                yield call(instanciatorApi.get, '/health_check/');
            } catch (error) {
            }
        }
        const response = yield call(api.get, '/settings/status/?degrees=true');
        yield put(armPoseActions.updateCurrent(response.data));
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}



function* watchFetchApiData() {
    while (true) {
        yield call(fetchApiData);
        yield delay(400); // Wait for 200ms before the next loop iteration
    }
}

export default function* rootSaga() {
    yield all([
        watchFetchApiData(), // Starts the watchFetchApiData task in the background
    ]);
}
