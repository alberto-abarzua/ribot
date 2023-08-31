'use client';
import ArmSimulation from '@/components/ArmSimulation/ArmSimulation';
import ArmStatus from '@/components/controls/ArmStatus';
import AxisControls from '@/components/controls/AxisControls';
import HomeButton from '@/components/controls/HomeButton';
import api from '@/utils/api';
import TextVariable from '@/components/general/text/TextVariable';
import TextVariableInfo from '@/components/general/text/TextVariableInfo';
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
        <div className="h-full flex-col items-end justify-end">
            <ArmSimulation></ArmSimulation>
            <div className="flex w-full flex-col bg-gray-200 px-10 py-10 lg:w-1/2 ">
                <div className="flex flex-row flex-wrap items-center space-x-2">
                    <ArmStatus status={currentPose}></ArmStatus>
                </div>
                <AxisControls
                    currentPose={currentPose}
                    setCurrentPose={setCurrentPose}
                ></AxisControls>
                <div className="flex flex-row">
                    <div className="w-1/3">
                        <HomeButton className></HomeButton>
                    </div>
                </div>
            </div>
            <TextVariable
                label="X"
                value={currentPose.x}
                setValue={value => setCurrentPose(prev => ({ ...prev, x: value }))}
            ></TextVariable>
            <TextVariableInfo
                label="X"
                value={currentPose.x}
                setValue={value => setCurrentPose(prev => ({ ...prev, x: value }))}
                infoText={'Current value of the X coordinate'}
            ></TextVariableInfo>
        </div>
    );
}
