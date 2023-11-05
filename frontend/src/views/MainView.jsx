
import ActionsPanel from '@/components/actions/ActionsPanel';
import ArmSimulation from '@/components/armsimulation/ArmSimulation';
import ArmStatus from '@/components/controls/ArmStatus';
import ControlPanel from '@/components/controls/ControlPanel';
import SideNav from '@/components/general/layout/SideNav';
import Providers from '@/components/general/providers/Providers';

export default function Home() {
    return (
        <Providers>
            <div className="box-border flex h-screen">
                <div className="relative flex h-full w-full flex-col lg:w-1/12 ">
                    <SideNav></SideNav>
                </div>

                <div className="flex h-full w-full flex-col items-center lg:w-5/12 ">
                    <ActionsPanel></ActionsPanel>
                </div>
                <div className="relative box-border flex h-full w-full flex-col items-start justify-start bg-slate-50 lg:w-6/12">
                    <div className="relative flex h-3/5 w-full">
                        <ArmSimulation></ArmSimulation>
                        <div className="absolute right-0">
                            <ArmStatus></ArmStatus>
                        </div>
                    </div>

                    <ControlPanel></ControlPanel>
                </div>
            </div>
        </Providers>
    );
}
