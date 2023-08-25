

const ArmStatus = ({ status }) => {
    // status should have x,y,z, roll pitch, yaw
    
    return (
        <div className="bg-gray-100 p-4 rounded-lg w-full">
            <h3 className="text-lg font-medium mb-2">Arm Status</h3>
            <div className="flex flex-col items-center md:flex-row">
                <div className="flex-1 flex space-x-2 self-center">
                    <label htmlFor="x-input" className="text-gray-700 self-center">X:</label>
                    <input type="text" id="x-input" value={status.x.toFixed(2)} readOnly className="bg-gray-200 px-2 py-1 rounded-lg w-full " />
                </div>
                <div className="flex-1 flex space-x-2 self-center">
                    <label htmlFor="y-input" className="text-gray-700 self-center">Y:</label>
                    <input type="text" id="y-input" value={status.y.toFixed(2)} readOnly className="bg-gray-200 px-2 py-1 rounded-lg w-full " />
                </div>
                <div className="flex-1 flex space-x-2 self-center">
                    <label htmlFor="z-input" className="text-gray-700 self-center">Z:</label>
                    <input type="text" id="z-input" value={status.z.toFixed(2)} readOnly className="bg-gray-200 px-2 py-1 rounded-lg w-full " />
                </div>
                <div className="flex-1 flex space-x-2 self-center">
                    <label htmlFor="roll-input" className="text-gray-700 self-center">Roll:</label>
                    <input type="text" id="roll-input" value={status.roll.toFixed(2)} readOnly className="bg-gray-200 px-2 py-1 rounded-lg w-full " />
                </div>
                <div className="flex-1 flex space-x-2 self-center">
                    <label htmlFor="pitch-input" className="text-gray-700 self-center">Pitch:</label>
                    <input type="text" id="pitch-input" value={status.pitch.toFixed(2)} readOnly className="bg-gray-200 px-2 py-1 rounded-lg w-full " />
                </div>
                <div className="flex-1 flex space-x-2 self-center">
                    <label htmlFor="yaw-input" className="text-gray-700 self-center">Yaw:</label>
                    <input type="text" id="yaw-input" value={status.yaw.toFixed(2)} readOnly className="bg-gray-200 px-2 py-1 rounded-lg w-full" />
                </div>
            </div>
        </div>
    )
}
export default ArmStatus;