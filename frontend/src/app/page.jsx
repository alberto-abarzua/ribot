'use client';
import ActionContainer from '@/components/actions/ActionContainer';
import ArmSimulation from '@/components/ArmSimulation/ArmSimulation';
import ArmStatus from '@/components/controls/ArmStatus';
import AxisControls from '@/components/controls/AxisControls';
import SideNav from '@/components/general/layout/SideNav';
import { armPoseActions } from '@/redux/ArmPoseSlice';
import store from '@/redux/store';
import api from '@/utils/api';

import { useEffect, useRef } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Provider } from 'react-redux';
import { useSelector, useDispatch } from 'react-redux';

export default function Home() {
    const dispatch = useDispatch();
    const currentPose = useSelector(state => state.armPose);
    const currentPoseRef = useRef(currentPose);
    const intervalIdRef = useRef();

    useEffect(() => {
        currentPoseRef.current = currentPose;
    }, [currentPose]);

    useEffect(() => {
        if (intervalIdRef.current) {
            clearInterval(intervalIdRef.current);
        }

        const fetchCurrentPose = async () => {
            const response = await api.get('/move/status/');
            dispatch(armPoseActions.updateCurrent(response.data));
        };

        const moveToPose = async () => {
            if (Object.values(currentPoseRef.current.toMove).some(value => value !== 0)) {
                let pose = {
                    x: currentPoseRef.current.x + currentPoseRef.current.toMove.x,
                    y: currentPoseRef.current.y + currentPoseRef.current.toMove.y,
                    z: currentPoseRef.current.z + currentPoseRef.current.toMove.z,
                    roll: currentPoseRef.current.roll + currentPoseRef.current.toMove.roll,
                    pitch: currentPoseRef.current.pitch + currentPoseRef.current.toMove.pitch,
                    yaw: currentPoseRef.current.yaw + currentPoseRef.current.toMove.yaw,
                };

                let tool = {
                    toolValue:
                        currentPoseRef.current.toolValue + currentPoseRef.current.toMove.toolValue,
                };

                dispatch(
                    armPoseActions.update({
                        x: 0,
                        y: 0,
                        z: 0,
                        roll: 0,
                        pitch: 0,
                        yaw: 0,
                        toolValue: 0,
                    })
                );
                // console.log(currentPoseRef.current)
                try {
                    console.log('moving');
                    let response = await api.post('/move/pose/move/', pose);
                    if (response.status === 400) {
                        alert(response.data.message);
                    }
                } catch (error) {
                    if (error.response && error.response.status === 400) {
                        alert(error.response.data.message); //TODO: make this a toast
                    } else {
                        console.error('An unexpected error occurred:', error);
                        alert('An unexpected error occurred');
                    }
                }

                if (currentPoseRef.current.toMove.toolValue !== 0) {
                    console.log('seding tool');
                    try {
                        let response = await api.post('/move/tool/move/', tool);
                        if (response.status === 400) {
                            alert(response.data.message);
                        }
                    } catch (error) {
                        if (error.response && error.response.status === 400) {
                            alert(error.response.data.message); //TODO: make this a toast
                        } else {
                            console.error('An unexpected error occurred:', error);
                            alert('An unexpected error occurred');
                        }
                    }
                }
            }
        };

        intervalIdRef.current = setInterval(() => {
            moveToPose();
            fetchCurrentPose();
        }, 100);

        return () => {
            clearInterval(intervalIdRef.current);
        };
    }, [dispatch]);
    return (
        <Provider store={store}>
            <DndProvider backend={HTML5Backend}>
                <div className="box-border flex h-full">
                    <div className="flex h-full w-full flex-col  lg:w-1/12 ">
                        <SideNav></SideNav>
                    </div>
                    <div className="flex h-full w-full flex-col items-center bg-white lg:w-5/12 ">
                        <ActionContainer></ActionContainer>
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
