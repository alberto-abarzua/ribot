import axios from 'axios';

const api = axios.create({
    withCredentials: true,
});

api.interceptors.request.use(
    config => {
        // Retrieve the baseURL from localStorage for every request
        const baseURL = window.localStorage.getItem('backendUrl');
        if (baseURL) {
            config.baseURL = baseURL;
        }

        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

export default api;

