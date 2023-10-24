import React, { useState } from 'react';
import AxisControls from '@/components/controls/AxisControls';
import JointsControls from '@/components/controls/JointsControls';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

const ControlPanel = () => {
    const [showAxisControls, setShowAxisControls] = useState(true);

    return (
        <div className="flex flex-col w-full bg-slate-50">
            <div className="flex m-4 items-center p-4 rounded-lg bg-slate-200 w-fit">
                <Label htmlFor= 'control-toggle ' className = 'text-lg mr-4' > Axis Control </Label>
                <Switch
                    className = 'transform scale-125'
                    id = 'control-toggle'
                    checked={showAxisControls} 
                    onCheckedChange={() => setShowAxisControls(!showAxisControls)}
                />
            </div>
            {showAxisControls ? <AxisControls /> : <JointsControls />}
        </div>
    );
};

export default ControlPanel;
