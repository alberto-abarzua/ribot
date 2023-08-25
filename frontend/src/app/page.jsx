"use client";
import ArmSimulation from "@/components/ArmSimulation/ArmSimulation";
import { useEffect, useState } from "react";
import api from "@/utils/api";
import ArmStatus from "@/components/controls/ArmStatus";
import AxisControls from "@/components/controls/AxisControls";
import HomeButton from "@/components/controls/HomeButton";
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
            const response = await api.get("/move/pose/current/");
            setCurrentPose(response.data);
        };

        fetchCurrentPose();
        setIsLoading(false);
    }, []);

    useEffect(() => {
        const updateCurrentPose = async () => {
            await api.post("/move/pose/move/", currentPose);
        };
        if (isLoading) {
            return;
        }
        updateCurrentPose();
    }, [currentPose]);

    return (
        <div className="h-full flex-col justify-end items-end">
            <ArmSimulation></ArmSimulation>
                <div className="flex-col flex bg-gray-200 py-10 px-10 w-full lg:w-1/2 ">
                    <div className="flex-row flex-wrap flex space-x-2 items-center">
                        <ArmStatus status={currentPose}></ArmStatus>
                    </div>
                    <AxisControls
                        currentPose={currentPose}
                        setCurrentPose={setCurrentPose}
                    ></AxisControls>
                    <div className="flex flex-row">
                        <div className = "w-1/3">
                            <HomeButton className></HomeButton>
                        </div>
                    </div>
                </div>
        </div>
    );
}
