const ArmSimulation = () => {
    const simulation_url = process.env.NEXT_PUBLIC_ARM_SIMULATION_URL;
    const websocket_port =
        process.env.NEXT_PUBLIC_ARM_SIMULATION_WEBSOCKET_PORT;
    const websocket_host =
        process.env.NEXT_PUBLIC_ARM_SIMULATION_WEBSOCKET_HOST;
    return (
        <div className="h-1/2 w-1/2 relative">
            <iframe
                src={`${simulation_url}/game.html?ip=${websocket_host}&port=${websocket_port}`}
                className="absolute h-full w-full border-none top-0 left-0"
            ></iframe>
        </div>
    );
};

export default ArmSimulation;
