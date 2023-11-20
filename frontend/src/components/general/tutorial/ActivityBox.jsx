import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { currentStepSelector } from '@/redux/ActivitySlice';
import { activityActions } from '@/redux/ActivitySlice';
import QuizIcon from '@mui/icons-material/Quiz';
import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

const ActivityBox = () => {
    const [isVisible, setIsVisible] = useState(false);
    const dispatch = useDispatch();
    const steps = useSelector(state => state.activity.steps);
    const currentStep = useSelector(currentStepSelector);

    const numSteps = steps.length;
    let num_done = 0;
    for (let step of steps) {
        if (step.completion.done) {
            num_done++;
        } else {
            break;
        }
    }
    const completion = Math.round((num_done / numSteps) * 100);
    console.log(steps);

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsVisible(true);
        }, 4000);

        return () => clearTimeout(timer);
    }, []);

    const clearActivity = () => {
        dispatch(activityActions.clearActivity());
    };

    return (
        <div
            className={`absolute left-1/2 top-2 z-20 flex w-1/4 transform flex-col justify-center  rounded-md border border-gray-700 bg-purple-700 bg-opacity-90  p-4 text-white transition-all  duration-500 ${
                isVisible ? 'translate-y-0 opacity-100' : '-translate-y-full opacity-0'
            }`}
        >
            <div className="mb-2 flex items-center gap-x-2">
                <QuizIcon className="animate-bounce" />
                <p className="whitespace-nowrap text-lg">Arm Activity!</p>
                <Progress value={completion} />
                <div role="button" onClick={clearActivity}>
                    &#10005;
                </div>
            </div>
            {currentStep ? (
                <div className="flex flex-col gap-x-2">
                    <p className="text-lg">Your current step is:</p>

                    <div className="rounded bg-slate-50 px-3 py-1 text-gray-800 shadow-sm shadow-white">
                        <p className="text-xl">{currentStep.name}</p>
                        <p className="text-sm text-gray-600">{currentStep.description}</p>
                    </div>
                </div>
            ) : (
                <div>Activity Completed!</div>
            )}
        </div>
    );
};

export default ActivityBox;
