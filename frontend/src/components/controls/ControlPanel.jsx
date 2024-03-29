import AxisControls from '@/components/controls/AxisControls';
import JointsControls from '@/components/controls/JointsControls';
import InfoHover from '@/components/general/text/InfoHover';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import api from '@/utils/api';
import { ControllerStatus } from '@/utils/arm_enums';
import { Bolt } from '@mui/icons-material';
import DangerousIcon from '@mui/icons-material/Dangerous';
import HomeIcon from '@mui/icons-material/Home';
import OtherHousesIcon from '@mui/icons-material/OtherHouses';
import React, { useState } from 'react';
import { useSelector } from 'react-redux';

const ControlPanel = () => {
    const call_home = async () => {
        await api.post('/move/home/');
    };

    const call_stop_movement = async () => {
        await api.post('/settings/stop/');
    };

    const status = useSelector(state => state.armPose.status);
    const isHomed = useSelector(state => state.armPose.isHomed);

    const [showAxisControls, setShowAxisControls] = useState(false);
    let controlContent = null;
    if (status == ControllerStatus.NOT_STARTED || status == ControllerStatus.WAITING_CONNECTION) {
        controlContent = (
            <div className="flex  h-full items-center justify-center ">
                <Card className="m-auto w-fit">
                    <CardHeader>
                        <CardTitle>Waiting for arm!</CardTitle>
                        <CardDescription>Make sure the robot arm is powered on</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col items-center justify-center">
                        <Bolt className=" mx-auto text-5xl text-slate-800"></Bolt>
                    </CardContent>
                </Card>
            </div>
        );
    } else if (!isHomed) {
        controlContent = (
            <div className="flex h-full items-center justify-center ">
                <Card className="m-auto w-fit">
                    <CardHeader>
                        <CardTitle>Arm is not homed!</CardTitle>
                        <CardDescription>Please Press Home Arm</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col items-center justify-center">
                        <OtherHousesIcon className=" mx-auto text-5xl text-slate-800"></OtherHousesIcon>
                    </CardContent>
                </Card>
            </div>
        );
    } else {
        controlContent = (
            <div className="h-full w-full overflow-scroll">
                {showAxisControls ? <AxisControls /> : <JointsControls />}
            </div>
        );
    }

    return (
        <div className="flex h-full w-full flex-col bg-slate-50">
            <div className="mx-2 mt-2 flex flex-col gap-y-4 rounded-lg bg-slate-200 p-4">
                <h1 className="mx-2 text-2xl font-bold">Control Panel</h1>
                <div className="flex flex-row items-center ">
                    <div className="flex items-center gap-x-3 rounded-lg bg-white px-4 py-2">
                        <Label htmlFor="control-toggle " className="mr-4 whitespace-nowrap text-lg">
                            <InfoHover text="Toggle between controlling coordinates + raw-pitch-yaw and individual joints" />
                            {'X-Y-Z ⥄   Joint Controls'}
                        </Label>
                        <Switch
                            className="scale-125 transform"
                            id="control-toggle"
                            checked={showAxisControls}
                            onCheckedChange={() => setShowAxisControls(!showAxisControls)}
                        />
                    </div>

                    <div className="ml-auto flex w-fit items-center gap-x-3">
                        <TooltipProvider>
                            <Tooltip delayDuration={300}>
                                <TooltipTrigger>
                                    <Button onClick={call_home}>
                                        <HomeIcon className=" text-xl" /> Home Arm
                                    </Button>
                                </TooltipTrigger>

                                <TooltipContent>
                                    <p>Sets the default position </p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>

                        <TooltipProvider>
                            <Tooltip delayDuration={300}>
                                <TooltipTrigger>
                                    <Button onClick={call_stop_movement} variant="destructive">
                                        <DangerousIcon className="text" /> Stop
                                    </Button>
                                </TooltipTrigger>

                                <TooltipContent>
                                    <p>Stop all movements</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    </div>
                </div>
            </div>
            {controlContent}
        </div>
    );
};

export default ControlPanel;
