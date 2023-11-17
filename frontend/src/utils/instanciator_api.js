import axios from 'axios';

let instanciatorUrl = import.meta.env.VITE_INSTANCIATOR_URL;

console.log('instanciatorUrl: ', instanciatorUrl);
const instanciatorApi = axios.create({
    baseURL: instanciatorUrl,
    withCredentials: true,
});

instanciatorApi.interceptors.request.use(
    config => {
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

export default instanciatorApi;
