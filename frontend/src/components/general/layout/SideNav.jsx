import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import SettingsIcon from '@mui/icons-material/Settings';
const SideNav = () => {
    return (
        <div className="fixed h-full w-16 bg-gray-100">
            <div className="relative left-0 top-0 mx-auto mt-8 flex h-12 w-14 items-center justify-center rounded-full bg-slate-700">
                <PrecisionManufacturingIcon className="scale-125 transform text-white"></PrecisionManufacturingIcon>
            </div>

            <div className="absolute bottom-4 flex w-full flex-col items-center space-y-10 pb-3">
                <InfoOutlinedIcon className="scale-150 transform cursor-pointer text-slate-900"></InfoOutlinedIcon>
                <SettingsIcon className="scale-150 transform"></SettingsIcon>
            </div>
        </div>
    );
};

export default SideNav;
