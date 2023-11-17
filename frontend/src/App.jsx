import instanciatorApi from '@/utils/instanciator_api';
import MainView from '@/views/MainView';
import { Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';

function App() {
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        console.log('useEffect triggered');

        const getBackendInfo = async () => {
            console.log('getBackendInfo function called');
            let envBackendUrl = import.meta.env.VITE_BACKEND_URL;
            console.log('VITE_BACKEND_URL:', envBackendUrl);
            window.localStorage.removeItem('backendUrl');

            if (envBackendUrl === undefined || envBackendUrl === 'no_backend') {
                console.log('Fetching backend URL from API');
                const response = await instanciatorApi.get('/backend_url/');
                console.log('Response from API:', response);
                const { backend_port } = response.data;

                const backend_url = `${import.meta.env.VITE_INSTANCIATOR_URL}/s${backend_port}`;
                window.localStorage.setItem('backendUrl', backend_url);
                console.log('Backend URL saved to local storage from API:', backend_url);
            } else {
                console.log('Saving env variable to local storage:', envBackendUrl);
                window.localStorage.setItem('backendUrl', envBackendUrl);
            }
            // sleep to make the loading viual
            await new Promise(resolve => setTimeout(resolve, 1000));
            setLoading(false);
        };

        getBackendInfo().catch(console.error);
    }, []);

    if (loading) {
        return (
            <div className="flex h-screen flex-col items-center justify-center">
                <Loader2 className="h-20 w-20 animate-spin text-orange-400" />
                <p className="text-2xl italic text-gray-500">Prepping!</p>
            </div>
        );
    }

    return <MainView />;
}

export default App;
