import api from '@/utils/api';

const HomeButton = () => {
    const call_home = async () => {
        await api.post('/move/home/');
    };

    return (
        <div>
            <button className="w-full rounded shadow-md bg-green-500 p-2 hover:bg-green-300" onClick={call_home}>
                {' '}
                Home{' '}
            </button>
        </div>
    );
};

export default HomeButton;
