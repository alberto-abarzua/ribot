import axios from 'axios';

let backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
if (backendUrl && backendUrl.startsWith('"') && backendUrl.endsWith('"')) {
    backendUrl = backendUrl.slice(1, -1);
}

const api = axios.create({
    baseURL: backendUrl,
});

api.interceptors.request.use(
    config => {
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

export default api;
