import LogoSVG from '@/assets/logo.svg';
import Tutorial from '@/components/general/layout/Tutorial';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { useState } from 'react';

const SideNav = () => {
    const [showTutorial, setShowTutorial] = useState(false);

    const toggleTutorial = () => {
        setShowTutorial(prev => !prev);
    };

    return (
        <>
            <div className="fixed z-40 h-full w-16 bg-gray-100">
                <div className="relative left-0 top-0 mx-auto mt-8 flex h-12 w-14 items-center justify-center rounded-full bg-slate-700">
                    <img src={LogoSVG} alt="logo" className="w-20"></img>
                </div>

                <div
                    onClick={toggleTutorial}
                    className="absolute bottom-10 flex w-full flex-col items-center space-y-10 pb-3"
                >
                    <InfoOutlinedIcon className="scale-[2] transform cursor-pointer text-sky-700 hover:scale-[2.1] hover:text-sky-800"></InfoOutlinedIcon>
                </div>
            </div>

            {showTutorial && <Tutorial toggleShow={toggleTutorial}></Tutorial>}
        </>
    );
};

export default SideNav;
