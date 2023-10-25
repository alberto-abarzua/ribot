import DangerousIcon from '@mui/icons-material/Dangerous';
import HomeIcon from '@mui/icons-material/Home';
import OtherHousesIcon from '@mui/icons-material/OtherHouses';

import React, { useState } from 'react';

import AxisControls from '@/components/controls/AxisControls';
import JointsControls from '@/components/controls/JointsControls';
import InfoHover from '@/components/general/text/InfoHover';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import api from '@/utils/api';
import { useSelector } from 'react-redux';
import { ControllerStatus } from '@/utils/arm_enums';

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { Bolt } from '@mui/icons-material';

const ControlPanel = () => {
    const call_home = async () => {
        await api.post('/move/home/');
    };

    const call_stop_movement = async () => {
        await api.post('/settings/stop/');
    };
    const status = useSelector(state => state.armPose.status);
    const isHomed = useSelector(state => state.armPose.isHomed);

    const [showAxisControls, setShowAxisControls] = useState(true);
    let controlContent = null;
    if (status == ControllerStatus.NOT_STARTED || status == ControllerStatus.WAITING_CONNECTION) {
        controlContent = (
            <div className="flex h-full items-center justify-center ">
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
        controlContent = showAxisControls ? <AxisControls /> : <JointsControls />;
    }

    return (
        <div className="flex h-full w-full flex-col bg-slate-50">
            <div className="flex flex-row items-center rounded-lg bg-slate-200 p-4 ">
                <div className="flex items-center gap-x-3 rounded-lg bg-white px-4 py-2">
                    <Label htmlFor="control-toggle " className="mr-4 whitespace-nowrap text-lg">
                        <InfoHover text="Toggle between Axis and Joint controls" />
                        Axis-Joint Controls{' '}
                    </Label>
                    <Switch
                        className="scale-125 transform"
                        id="control-toggle"
                        checked={showAxisControls}
                        onCheckedChange={() => setShowAxisControls(!showAxisControls)}
                    />
                </div>

                <div className="ml-auto flex w-fit items-center gap-x-3">
                    <Button onClick={call_home}>
                        <HomeIcon className=" text-xl" /> Home Arm
                    </Button>
                    <Button onClick={call_stop_movement} variant="destructive">
                        <DangerousIcon className="text" /> Stop
                    </Button>
                </div>
            </div>
            {controlContent}
            <JointsControls />
        </div>
    );
};

export default ControlPanel;
