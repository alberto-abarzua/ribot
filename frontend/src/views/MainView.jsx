import ActionsPanel from '@/components/actions/ActionsPanel';
import ArmSimulation from '@/components/armsimulation/ArmSimulation';
import ArmStatus from '@/components/controls/ArmStatus';
import ControlPanel from '@/components/controls/ControlPanel';
import ActivityBox from '@/components/general/tutorial/ActivityBox';
import SideNav from '@/components/general/layout/SideNav';
import Providers from '@/components/general/providers/Providers';
import { Toaster } from '@/components/ui/toaster';

export default function Home() {
    return (
        <Providers>
            <ActivityBox></ActivityBox>
            <div className="box-border flex h-screen">
                <div className="relative flex h-full flex-col lg:w-16 ">
                    <SideNav></SideNav>
                </div>

                <div className="flex h-full w-full flex-col items-center lg:w-6/12 ">
                    <ActionsPanel></ActionsPanel>
                </div>
                <div className="relative box-border flex h-full w-full flex-col items-start justify-start bg-slate-50 lg:w-6/12">
                    <div className="relative flex h-1/2 w-full">
                        <ArmSimulation></ArmSimulation>
                        <div className="absolute right-0">
                            <ArmStatus></ArmStatus>
                        </div>
                    </div>
                    <div className="relative flex h-1/2 w-full">
                        <ControlPanel></ControlPanel>
                    </div>
                </div>
            </div>
            <Toaster></Toaster>
        </Providers>
    );
}
