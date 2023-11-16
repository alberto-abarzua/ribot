import instanciatorApi from '@/utils/instanciator_api';
import MainView from '@/views/MainView';
import { useEffect } from 'react';

function App() {
    useEffect(() => {
        console.log('useEffect triggered'); // Log when useEffect is triggered

        const getBackendInfo = async () => {
            console.log('getBackendInfo function called'); // Log at the start of getBackendInfo
            let envBackendUrl = import.meta.env.VITE_BACKEND_URL;
            console.log('VITE_BACKEND_URL:', envBackendUrl); // Log the environment variable

            if (envBackendUrl === undefined || envBackendUrl === 'no_backend') {
                console.log('Fetching backend URL from API'); // Log when fetching from API
                const response = await instanciatorApi.get('/backend_url/');
                console.log('Response from API:', response); // Log the response from the API
                const { backend_url } = response.data;
                window.localStorage.setItem('backendUrl', backend_url);
                console.log('Backend URL saved to local storage from API:', backend_url);
            } else {
                console.log('Saving env variable to local storage:', envBackendUrl); // Log when saving from env variable
                window.localStorage.setItem('backendUrl', envBackendUrl);
            }
        };

        getBackendInfo().catch(console.error); // Call getBackendInfo and catch any errors
    }, []);

    return <MainView />;
}

export default App;
