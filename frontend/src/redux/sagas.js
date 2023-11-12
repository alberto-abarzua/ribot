import { armPoseActions } from '@/redux/ArmPoseSlice';
import api from '@/utils/api';
import { call, put, delay, all } from 'redux-saga/effects';

function* fetchApiData() {
    try {
        // if in the server return

        const response = yield call(api.get, '/settings/status/?degrees=true');
        yield put(armPoseActions.updateCurrent(response.data));
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function* watchFetchApiData() {
    while (true) {
        yield call(fetchApiData);
        yield delay(150); // Wait for 200ms before the next loop iteration
    }
}

export default function* rootSaga() {
    yield all([
        watchFetchApiData(), // Starts the watchFetchApiData task in the background
    ]);
}
