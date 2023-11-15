import Actions from '@/assets/actions.gif';
import Controls from '@/assets/controls.png';
import HomeStop from '@/assets/home_stop.png';
import MoveAxis from '@/assets/move_axis.gif';
import MoveJoints from '@/assets/move_joints.gif';
import RunActions from '@/assets/run_actions.gif';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import PropTypes from 'prop-types';
import React, { useEffect } from 'react';

const Tutorial = ({ toggleShow }) => {
    const handleBackdropClick = event => {
        if (event.currentTarget === event.target) {
            toggleShow(false);
        }
    };

    useEffect(() => {
        const handleEscape = event => {
            if (event.key === 'Escape') {
                toggleShow(false);
            }
        };

        window.addEventListener('keydown', handleEscape);

        return () => {
            window.removeEventListener('keydown', handleEscape);
        };
    }, [toggleShow]);

    return (
        <div
            className="fixed inset-0 z-40 flex items-center justify-center bg-black bg-opacity-50"
            onClick={handleBackdropClick}
        >
            <div className="relative z-50 h-5/6 w-4/5 overflow-auto rounded-md  bg-slate-100 p-5 shadow-lg">
                <button
                    onClick={() => toggleShow(false)}
                    className="absolute right-0 top-0 m-3 text-lg hover:text-gray-500"
                >
                    &#10005; {/* Unicode X symbol */}
                </button>

                <div className="flex h-full items-center">
                    <div className="relative h-full w-1/3  px-2">
                        <Card className="h-full">
                            <CardHeader>
                                <CardTitle>Getting Started</CardTitle>
                                <CardDescription>The first steps</CardDescription>
                            </CardHeader>
                            <CardContent className=" flex h-full flex-col gap-y-2">
                                <p className="text-lg font-bold">Home the arm to get started.</p>
                                <p className="text-md text-gray-600">
                                    Press the home button to home the arm to start.
                                </p>
                                <img
                                    src={HomeStop}
                                    alt="Home the arm"
                                    className="h-10 overflow-hidden rounded-md object-contain"
                                />

                                <p className="mt-5 text-lg font-bold">
                                    Move around using the controls!
                                </p>

                                <p className="text-md text-gray-600">
                                    Press the home button to home the arm to start.
                                </p>

                                <img
                                    src={Controls}
                                    alt="Home the arm"
                                    className=" overflow-hidden rounded-md object-contain"
                                />

                                <p className="text-md text-gray-600"></p>
                            </CardContent>
                        </Card>
                    </div>
                    <div className="relative h-full w-1/3  px-2">
                        <Card className="h-full">
                            <CardHeader>
                                <CardTitle>Free Move</CardTitle>
                                <CardDescription>You can move the arm freely</CardDescription>
                            </CardHeader>
                            <CardContent className=" flex h-full flex-col gap-y-2">
                                <p className="text-lg font-bold">
                                    Using Axis (X,Y,Z,Roll,Pitch and Yaw)
                                </p>
                                <p className="text-md text-gray-600">
                                    You can move the arm using coordinate and orientation angles
                                </p>
                                <img src={MoveAxis} alt="Move Axis" />

                                <p className="mt-5 text-lg font-bold">Moving individual joints</p>

                                <p className="text-md text-gray-600">
                                    Each joint can be moved individually.
                                </p>
                                <img src={MoveJoints} alt="Move Joints" />
                            </CardContent>
                        </Card>
                    </div>
                    <div className="relative h-full w-1/3  px-2">
                        <Card className="h-full">
                            <CardHeader>
                                <CardTitle>Add and move Actions</CardTitle>
                            </CardHeader>
                            <CardContent className=" flex h-full flex-col gap-y-2">
                                <p className="text-lg font-bold">Grab an action from the toolbar</p>

                                <p className="text-md text-gray-600">
                                    You can drag and drop actions from the toolbar to the list, move
                                    them around to change the order, download them as a JSON file or
                                    delete them.
                                </p>
                                <img src={Actions} alt="Grab and drop Actions" />

                                <p className=" text-lg font-bold">Run your actions!</p>
                                <p className="text-md text-gray-600">
                                    Run individual actions by right clicking on them, or run all of
                                    them at once by clicking the play button.
                                </p>
                                <img src={RunActions} alt="Run Actions" />
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
};

Tutorial.propTypes = {
    toggleShow: PropTypes.func.isRequired,
};

export default Tutorial;
