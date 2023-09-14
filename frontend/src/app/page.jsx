'use client';
import ActionContainer from '@/components/actions/ActionContainer';
import ArmSimulation from '@/components/ArmSimulation/ArmSimulation';
import ArmStatus from '@/components/controls/ArmStatus';
import AxisControls from '@/components/controls/AxisControls';
import SideNav from '@/components/general/layout/SideNav';
import api from '@/utils/api';
import { Provider } from 'react-redux';
import store from '@/redux/store';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

import { useEffect, useState ,useRef} from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { armPoseActions } from '@/redux/ArmPose';
export default function Home() {
    const dispatch = useDispatch();
    const currentPose = useSelector(state => state.armPose);
    const intervalIdRef = useRef();



    const fetchCurrentPose = async () => {
        const response = await api.get('/move/pose/current/');
        dispatch(armPoseActions.updateCurrentX(response.data.x));
        dispatch(armPoseActions.updateCurrentY(response.data.y));
        dispatch(armPoseActions.updateCurrentZ(response.data.z));
        dispatch(armPoseActions.updateCurrentRoll(response.data.roll));
        dispatch(armPoseActions.updateCurrentPitch(response.data.pitch));
        dispatch(armPoseActions.updateCurrentYaw(response.data.yaw));
        dispatch(armPoseActions.updateCurrentToolValue(response.data.toolValue));
    };

    const moveToPose = async () => {
        if (Object.values(currentPose.toMove).some(value => value !== 0)) {
            console.log(currentPose.toMove);
            let pose = {
                x: currentPose.x + currentPose.toMove.x,
                y: currentPose.y + currentPose.toMove.y,
                z: currentPose.z + currentPose.toMove.z,
                roll: currentPose.roll + currentPose.toMove.roll,
                pitch: currentPose.pitch + currentPose.toMove.pitch,
                yaw: currentPose.yaw + currentPose.toMove.yaw,
                toolValue: currentPose.toolValue + currentPose.toMove.toolValue,
            };
            dispatch(armPoseActions.updateX(0));
            dispatch(armPoseActions.updateY(0));
            dispatch(armPoseActions.updateZ(0));
            dispatch(armPoseActions.updateRoll(0));
            dispatch(armPoseActions.updatePitch(0));
            dispatch(armPoseActions.updateYaw(0));
            dispatch(armPoseActions.updateToolValue(0));

            await api.post('/move/pose/move/', pose);
        }
    };


    useEffect(() => {
        if (intervalIdRef.current) {
          clearInterval(intervalIdRef.current);
        }
    
        intervalIdRef.current = setInterval(() => {
          moveToPose();
          fetchCurrentPose();
        }, 300);
    
        return () => {
          clearInterval(intervalIdRef.current);
        };
      }, [dispatch, currentPose]);

    // useEffect(() => {
    //     moveToPose();
    //     fetchCurrentPose();
    // }
    // , [currentPose.toMove]);

    return (
        <Provider store={store}>
            <DndProvider backend={HTML5Backend}>
                <div className="box-border flex h-full">
                    <div className="flex h-full w-full flex-col  lg:w-1/12 ">
                        <SideNav></SideNav>
                    </div>
                    <div className="flex h-full w-full flex-col items-center bg-white px-10 lg:w-5/12 ">
                        <div className="m-0 flex h-full w-4/5 p-0">
                            <ActionContainer></ActionContainer>
                        </div>
                    </div>
                    <div className="box-border flex h-full w-full flex-col bg-slate-50 lg:w-6/12">
                        <ArmSimulation></ArmSimulation>
                        <ArmStatus></ArmStatus>
                        <AxisControls></AxisControls>
                    </div>
                </div>
            </DndProvider>
        </Provider>
    );
}
