import LogoSVG from '@/assets/logo.svg';
import Tutorial from '@/components/general/tutorial/Tutorial';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { useState } from 'react';

const SideNav = () => {
    const [showTutorial, setShowTutorial] = useState(false);
    const [wasTutorialShown, setWasTutorialShown] = useState(false);

    const toggleTutorial = () => {
        setShowTutorial(prev => !prev);
        setWasTutorialShown(true);
    };

    return (
        <>
            <div className="fixed h-full w-16 bg-gray-100">
                <a href="https://ribot.dev">
                    <div className="relative left-0 top-0 mx-auto mt-8 flex h-12 w-14 items-center justify-center rounded-full bg-slate-700">
                        <img src={LogoSVG} alt="logo" className="w-20"></img>
                    </div>
                </a>

                <div
                    onClick={toggleTutorial}
                    className="absolute bottom-20 flex w-full scale-[2.1] transform flex-col items-center space-y-10 pb-3"
                >
                    <InfoOutlinedIcon
                        className={` transform cursor-pointer text-sky-700  hover:text-sky-800 ${
                            wasTutorialShown ? '' : 'animate-bounce'
                        } `}
                    ></InfoOutlinedIcon>
                </div>
            </div>

            {showTutorial && <Tutorial toggleShow={toggleTutorial}></Tutorial>}
        </>
    );
};

export default SideNav;
