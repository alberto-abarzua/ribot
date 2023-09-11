'use client';
import MoveAction from '@/components/actions/MoveAction';
import SleepAction from '@/components/actions/SleepAction';
import ToolAction from '@/components/actions/ToolAction';
import ToolBar from '@/components/actions/ToolBar';
import ArmSimulation from '@/components/ArmSimulation/ArmSimulation';
import ArmStatus from '@/components/controls/ArmStatus';
import AxisControls from '@/components/controls/AxisControls';
import SideNav from '@/components/general/layout/SideNav';
import api from '@/utils/api';
import ActionContainer from '@/components/actions/ActionContainer';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

import { useEffect, useState } from 'react';
export default function Home() {
    const [currentPose, setCurrentPose] = useState({
        x: 0,
        y: 0,
        z: 0,
        roll: 0,
        pitch: 0,
        yaw: 0,
    });
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchCurrentPose = async () => {
            const response = await api.get('/move/pose/current/');
            setCurrentPose(response.data);
        };

        fetchCurrentPose();
        setIsLoading(false);
    }, []);

    useEffect(() => {
        const updateCurrentPose = async () => {
            await api.post('/move/pose/move/', currentPose);
        };
        if (isLoading) {
            return;
        }
        updateCurrentPose();
    }, [currentPose, isLoading]);

    return (
        <DndProvider backend={HTML5Backend}>
            <div className="box-border flex h-full">
                <div className="flex h-full w-full flex-col  lg:w-1/12 ">
                    <SideNav></SideNav>
                </div>
                <div className="flex h-full w-full flex-col items-center bg-white px-10 lg:w-5/12 ">
                    <div className="flex h-full w-4/5 p-0 m-0">
                        
                        <ActionContainer></ActionContainer>
                    </div>
                </div>

                <div className="box-border flex h-full w-full flex-col bg-slate-50 lg:w-6/12">
                    <ArmSimulation></ArmSimulation>

                    <ArmStatus
                        currentPose={currentPose}
                        setCurrentPose={setCurrentPose}
                    ></ArmStatus>

                    <AxisControls
                        currentPose={currentPose}
                        setCurrentPose={setCurrentPose}
                    ></AxisControls>
                </div>
            </div>
        </DndProvider>
    );
}
