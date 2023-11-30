import ActionsPanel from '@/components/actions/ActionsPanel';
import ArmSimulation from '@/components/armsimulation/ArmSimulation';
import ArmStatus from '@/components/controls/ArmStatus';
import ControlPanel from '@/components/controls/ControlPanel';
import SideNav from '@/components/general/layout/SideNav';
import Providers from '@/components/general/providers/Providers';
import ActivityBox from '@/components/general/tutorial/ActivityBox';
import { Toaster } from '@/components/ui/toaster';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { useSearchParams } from 'react-router-dom';

export default function Home() {
    const [searchParams] = useSearchParams();
    const runActivity = searchParams.get('activity') === 'true' || false;

    return (
        <Providers>
            {runActivity && <ActivityBox />}

            <div className="box-border flex h-screen">
                <div className="relative flex h-full flex-col lg:w-16">
                    <SideNav />
                </div>

                <PanelGroup direction="horizontal">
                    <Panel minSizePercentage={30} defaultSizePercentage={40}>
                        <ActionsPanel />
                    </Panel>

                    <PanelResizeHandle className="relative flex h-full w-3 flex-col items-center justify-center">
                        <div className=" h-full w-[1px] bg-gray-600 opacity-70 "> </div>
                    </PanelResizeHandle>

                    <Panel minSizePercentage={40}>
                        <PanelGroup direction="vertical">
                            <Panel minSizePercentage={20}>
                                <div className="relative h-full w-full ">
                                    <ArmSimulation />
                                    <div className="absolute right-0 top-0">
                                        <ArmStatus />
                                    </div>
                                </div>
                            </Panel>
                            <PanelResizeHandle className="relative flex h-3 w-full flex-col items-center justify-center">
                                <div className=" h-[1px] w-full bg-gray-600 opacity-70 "> </div>
                            </PanelResizeHandle>
                            <Panel minSizePercentage={30}>
                                <ControlPanel />
                            </Panel>
                        </PanelGroup>
                    </Panel>
                </PanelGroup>
            </div>
            <Toaster />
        </Providers>
    );
}
