import api from '@/utils/api';
import { useEffect, useState } from 'react';

const ArmSimulation = () => {
    const [websocketPort, setWebsocketPort] = useState(null);
    const [websocketHost, setWebsocketHost] = useState(null);
    const [simulationUrl, setSimulationUrl] = useState(null);
    const [websocketProtocol, setWebsocketProtocol] = useState(null);
    const [valid, setValid] = useState(false);

    useEffect(() => {
        const getWebsocketInfo = async () => {
            const response = await api.get('/settings/websocket_info/');
            const { websocket_port } = response.data;
            setWebsocketPort(websocket_port || null);
            setWebsocketHost(import.meta.env.VITE_ARM_SIMULATION_WEBSOCKET_HOST || null);
            setSimulationUrl(import.meta.env.VITE_ARM_SIMULATION_URL || null);

            if (window.location.protocol === 'https:') {
                setWebsocketHost(prev => `${prev}/w${websocket_port}`);
                setWebsocketProtocol('wss');
            } else {
                setWebsocketProtocol('ws');
            }
            setValid(true);
        };
        getWebsocketInfo();
    }, [websocketPort, websocketHost, simulationUrl, websocketProtocol]);

    const srcUrl = `${simulationUrl}/game.html?ip=${websocketHost}&port=${websocketPort}&protocol=${websocketProtocol}`;
    return (
        <div className="relative h-full w-full">
            {valid ? (
                <>
                    <iframe
                        src={srcUrl}
                        className="absolute left-0 top-0 h-full w-full cursor-none border-none"
                    ></iframe>
                    <div className="absolute inset-0 bg-transparent"></div>
                </>
            ) : (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
                    <div className="text-2xl text-gray-500">Loading...</div>
                </div>
            )}
        </div>
    );
};

export default ArmSimulation;
