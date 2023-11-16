import axios from 'axios';


const api = axios.create({
    withCredentials: true,
    baseURL: window.localStorage.getItem('backendUrl'),
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
