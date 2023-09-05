import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import SettingsIcon from '@mui/icons-material/Settings';
const SideNav = () => {
    return (
        <div className="relative h-full w-28 bg-gray-100">
            <div className="absolute left-[18px] top-[25px] h-20 w-20">
                <div className="absolute left-0 top-0 flex h-20 w-20 items-center justify-center rounded-full bg-zinc-300">
                    <PrecisionManufacturingIcon className="text-5xl"></PrecisionManufacturingIcon>
                </div>
            </div>
            <div className="absolute bottom-0 flex w-full flex-col items-center space-y-10 pb-3">
                <InfoOutlinedIcon className="text-5xl"></InfoOutlinedIcon>
                <SettingsIcon className="text-5xl"></SettingsIcon>
            </div>
        </div>
    );
};

export default SideNav;
