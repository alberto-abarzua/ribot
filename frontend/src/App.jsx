import instanciatorApi from '@/utils/instanciator_api';
import MainView from '@/views/MainView';
import { Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';

function isMobileDevice() {
    return /Android|webOS|iPhone|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function App() {
    const [loading, setLoading] = useState(true);
    const [searchParams] = useSearchParams();
    const [denied, setDenied] = useState(true);

    useEffect(() => {
        console.log('useEffect triggered');
        if (isMobileDevice()) {
            setDenied(true);
            setLoading(false);
            return;
        }

        const getBackendInfo = async () => {
            console.log('getBackendInfo function called');
            let envBackendUrl = import.meta.env.VITE_BACKEND_URL;
            console.log('VITE_BACKEND_URL:', envBackendUrl);
            window.localStorage.removeItem('backendUrl');

            if (envBackendUrl === undefined || envBackendUrl === 'no_backend') {
                console.log('Fetching backend URL from API');
                const access_token = searchParams.get('access_token');
                try {
                    const response = await instanciatorApi.get('/backend_url/', {
                        params: { token: access_token },
                    });
                    console.log('Response from API:', response);
                    const { backend_port } = response.data;

                    const backend_url = `${import.meta.env.VITE_INSTANCIATOR_URL}/s${backend_port}`;
                    window.localStorage.setItem('backendUrl', backend_url);
                    console.log('Backend URL saved to local storage from API:', backend_url);
                    if (backend_port === undefined) {
                        console.log('Backend port is undefined');
                        setDenied(true);
                    }
                    setDenied(false);
                } catch (error) {
                    console.log('Error fetching backend URL from API');
                    setDenied(true);
                    console.log(error);
                }
            } else {
                console.log('Saving env variable to local storage:', envBackendUrl);
                window.localStorage.setItem('backendUrl', envBackendUrl);
                setDenied(false);
            }
            // sleep to make the loading viual
            await new Promise(resolve => setTimeout(resolve, 1000));
            setLoading(false);
        };

        getBackendInfo().catch(console.error);
    }, [searchParams]);

    if (loading) {
        return (
            <div className="flex h-screen flex-col items-center justify-center">
                <Loader2 className="h-20 w-20 animate-spin text-orange-400" />
                <p className="text-2xl italic text-gray-500">Prepping!</p>
            </div>
        );
    }
    if (denied) {
        return (
            <div className="flex h-screen flex-col items-center justify-center">
                <p className="text-2xl  text-gray-800">Access denied!</p>
                <p className="text-center italic text-gray-500">
                    You do not have permision or are using a mobile device (This is intended for PC
                    use only)
                </p>
            </div>
        );
    }

    return <MainView />;
}

export default App;
