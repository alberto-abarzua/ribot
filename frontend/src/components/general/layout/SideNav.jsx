import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import SettingsIcon from '@mui/icons-material/Settings';
const SideNav = () => {
    return (
        <div className="fixed h-full w-28 bg-gray-100">
            <div className="absolute left-[18px] top-[25px] h-20 w-20">
                <div className="relative left-0 top-0 flex h-20 w-20 items-center justify-center rounded-full bg-zinc-300">
                    <PrecisionManufacturingIcon className="scale-150 transform"></PrecisionManufacturingIcon>
                </div>
            </div>

            <div className="absolute bottom-4 flex w-full flex-col items-center space-y-10 pb-3">
                <InfoOutlinedIcon className="scale-150 transform"></InfoOutlinedIcon>
                <SettingsIcon className="scale-150 transform"></SettingsIcon>
            </div>
        </div>
    );
};

export default SideNav;
