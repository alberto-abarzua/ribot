const ArmSimulation = () => {
    return (
        <div className="h-1/2 w-1/2 relative">
            <div className="absolute top-0 left-0 text-3xl text-gray-900 bg-gray-100 px-3 py-5 rounded shadow-sm shadow-slate-600 z-10">Arm simulation</div>
            <iframe
                src="http://localhost:8080/game.html?ip=localhost&port=65433"
                className="absolute h-full w-full border-none top-0 left-0"
            ></iframe>
        </div>
    );
};

export default ArmSimulation;
