import api from "@/utils/api"

const HomeButton = () => {
    const call_home = async () => {
        await api.post("/move/home/");
    }

    return (
        <div>
            <button className="bg-green-500 rounded p-2 w-full" onClick={call_home}> Home </button>
        </div>
    );

};

export default HomeButton;