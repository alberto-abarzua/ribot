const MoveAxis = ({ label, pose, setPose ,step=10}) => {
    const value = pose[label]; // Extract the value for the specific axis
  
    const upValue = () => {
      setPose((prev) => ({
        ...prev,
        [label]: prev[label] + step,
      }));
    };
  
    const downValue = () => {
      setPose((prev) => ({
        ...prev,
        [label]: prev[label] - step,
      }));
    };
    return (
      <div className="flex flex-col justify-center bg-slate-200 rounded p-2 w-40">
        <div className="w-full text-center text-lg pb-2 font-bold uppercase">
          {label}
        </div>
        <div className=" flex flex-col space-y-3">
          <button className="bg-slate-400 rounded p-2 w-full" onClick={upValue}>
            +
          </button>
          <input
            className="bg-white rounded p-2 w-full text-center appearance-none"
            type="text"
            readOnly // Make the input read-only since the value is controlled by the buttons
            value={value.toFixed(2)}
          ></input>
          <button className="bg-slate-400 rounded p-2 w-full" onClick={downValue}>
            -
          </button>
        </div>
      </div>
    );
  };
  
  export default MoveAxis;
  