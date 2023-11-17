import api from '@/utils/api';
import { useEffect, useState } from 'react';
const ArmSimulation = () => {
    const [websocketPort, setWebsocketPort] = useState(0);

    const simulation_url = import.meta.env.VITE_ARM_SIMULATION_URL;
    let websocket_host = import.meta.env.VITE_ARM_SIMULATION_WEBSOCKET_HOST;

    useEffect(() => {
        const getWebsocketInfo = async () => {
            const response = await api.get('/settings/websocket_info/');
            const { websocket_port } = response.data;
            setWebsocketPort(websocket_port);
        };
        getWebsocketInfo();

        console.log('this is the websocket port');
        console.log(websocketPort, simulation_url, websocket_host);
    }, [simulation_url, websocketPort, websocket_host]);

    const protocol = websocket_host === 'localhost' ? 'ws' : 'wss';
    console.log('USING PROTOCOL', protocol);
    if (websocket_host !== 'localhost') {
        websocket_host = `${websocket_host}/w${websocketPort}`;
    }
    return (
        <div className="relative h-full w-full">
            <iframe
                src={`${simulation_url}/game.html?ip=${websocket_host}&port=${websocketPort}&protocol=${protocol}`}
                className="absolute left-0 top-0 h-full w-full cursor-none border-none"
            ></iframe>
            <div className="absolute inset-0 bg-transparent"></div>
        </div>
    );
};

export default ArmSimulation;
