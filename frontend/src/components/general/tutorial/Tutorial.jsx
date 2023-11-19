import Actions from '@/assets/actions.gif';
import Coordinates from '@/assets/coordinates.gif';
import Euler from '@/assets/euler.gif';
import HomeStop from '@/assets/home_stop.png';
import MoveAxis from '@/assets/move_axis.gif';
import MoveJoints from '@/assets/move_joints.gif';
import RunActions from '@/assets/run_actions.gif';
import TutorialCard from '@/components/general/tutorial/TutorialCard';
import PropTypes from 'prop-types';
import { useEffect } from 'react';

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
            className="fixed inset-0 z-40 flex flex-wrap items-center justify-center bg-black bg-opacity-50"
            onClick={handleBackdropClick}
        >
            <div className="bg-opacity-85 relative z-50 flex h-[95%] w-11/12 flex-wrap items-start justify-center gap-4 overflow-auto rounded-md bg-slate-100 p-9 shadow-lg">
                <button
                    onClick={() => toggleShow(false)}
                    className="absolute right-0 top-0 m-3 text-lg hover:text-gray-500"
                >
                    &#10005;
                </button>
                <TutorialCard title="Getting Started" description="The first steps">
                    <p className="text-lg font-bold">Home the Arm to Get Started</p>
                    <p className="text-md text-gray-600">
                        {"Press the home button to initialize the arm's starting position."}
                    </p>
                    <img
                        src={HomeStop}
                        alt="Home the arm"
                        className="h-10 overflow-hidden rounded-md object-contain"
                    />

                    <p className="mt-5 text-xl font-bold">{`Understanding the Robot's Position`}</p>
                    <p className="text-md text-gray-600">
                        {`
                        The robot's position is defined by the location of its end effector (the
                        claw at the end of the arm) and its angle of approach.
                    `}
                    </p>

                    <p className="mt-5 text-lg font-bold">Angle of Approach</p>
                    <div className="flex items-center justify-center gap-x-2">
                        <p className="text-md text-gray-600">
                            {`
                            The angle of approach refers to the orientation of the end effector
                            relative to the target object. It's crucial for ensuring accurate and
                            efficient manipulation.
                        `}
                        </p>

                        <img
                            src={Euler}
                            alt="Angle of Approach"
                            className="w-52 flex-shrink-0 overflow-hidden rounded-md object-contain"
                        />
                    </div>

                    <p className="mt-5 text-lg font-bold">Coordinates</p>
                    <div className="flex items-center justify-center gap-x-2">
                        <p className="text-md text-gray-600">
                            The robot operates in a three-dimensional space, defined by X, Y, and Z
                            coordinates. These coordinates are essential for precise positioning and
                            movement.
                        </p>

                        <img
                            src={Coordinates}
                            alt="Robot Coordinates"
                            className="w-52 flex-shrink-0 overflow-hidden rounded-md object-contain"
                        />
                    </div>
                </TutorialCard>

                <TutorialCard title="Free Move" description="You can move the arm freely">
                    <p className="text-lg font-bold">Using Axes (X, Y, Z, Roll, Pitch, and Yaw)</p>
                    <p className="text-md text-gray-600">
                        Manipulate the arm using coordinate and orientation angles for precise
                        control in 3D space.
                    </p>

                    <img
                        src={MoveAxis}
                        alt="Move using axes"
                        className="h-80 overflow-hidden rounded-md object-contain"
                    />
                    <p className="mt-5 text-lg font-bold">Moving Individual Joints</p>
                    <p className="text-md text-gray-600">
                        Each joint of the robot arm can be controlled individually, allowing for
                        complex and precise movements.
                    </p>
                    <img
                        src={MoveJoints}
                        alt="Move individual joints"
                        className="h-80 overflow-hidden rounded-md object-contain"
                    />
                </TutorialCard>

                <TutorialCard
                    title="Add and Move Actions"
                    description="Customize your action sequence"
                >
                    <p className="text-lg font-bold">Grab an Action from the Toolbar</p>
                    <p className="text-md text-gray-600">
                        Drag and drop actions from the toolbar to the list, rearrange them to modify
                        the sequence, download them as a JSON file, or delete them as needed.
                    </p>
                    <img
                        src={Actions}
                        alt="Drag and drop actions"
                        className="h-80 overflow-hidden rounded-md object-contain"
                    />

                    <p className=" text-lg font-bold">Run Your Actions!</p>
                    <p className="text-md text-gray-600">
                        Execute individual actions by right-clicking on them, or run the entire
                        sequence at once by clicking the play button.
                    </p>
                    <img
                        src={RunActions}
                        alt="Run your actions"
                        className="h-80 overflow-hidden rounded-md object-contain"
                    />
                </TutorialCard>
            </div>
        </div>
    );
};

Tutorial.propTypes = {
    toggleShow: PropTypes.func.isRequired,
};

export default Tutorial;
