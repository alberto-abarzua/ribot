import MoveAxis from '@/assets/move_axis.gif';
import MoveJoints from '@/assets/move_joints.gif';
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
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
                    <div className="relative h-full w-1/3  px-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Free Move</CardTitle>
                                <CardDescription>You can move the arm freely</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <p className="text-lg font-bold">
                                    Using Axis (X,Y,Z,Roll,Pitch and Yaw)
                                </p>
                                <img src={MoveAxis} alt="Move Axis" />

                                <p className="mt-5 text-lg font-bold">Moving individual joints</p>
                                <img src={MoveJoints} alt="Move Joints" />
                            </CardContent>
                        </Card>
                    </div>
                    <div className="relative h-full w-1/3  px-4">
                        <Card>
                            <CardHeader>
                                <CardTitle>Add and move Actions</CardTitle>
                                <CardDescription>
                                    Drag and drop actions from the list or toolbar, each new action
                                    gets the current state of the arm.
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <p className="text-lg font-bold">
                                    Using Axis (X,Y,Z,Roll,Pitch and Yaw)
                                </p>
                                <img src={MoveAxis} alt="Move Axis" />

                                <p className="mt-5 text-lg font-bold">Moving individual joints</p>
                                <img src={MoveJoints} alt="Move Joints" />
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
