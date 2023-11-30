import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from '@/components/ui/accordion';
import { Progress } from '@/components/ui/progress';
import { currentStepSelector } from '@/redux/ActivitySlice';
import { activityActions } from '@/redux/ActivitySlice';
import { prefillGoogleForm } from '@/utils/activity';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import QuizIcon from '@mui/icons-material/Quiz';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

const ActivityBox = () => {
    const [isVisible, setIsVisible] = useState(false);
    const [formUrl, setFormUrl] = useState(null);
    const dispatch = useDispatch();
    const steps = useSelector(state => state.activity.steps);
    const currentStep = useSelector(currentStepSelector);
    const actionList = useSelector(state => state.actionList);

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

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsVisible(true);
        }, 4000);

        // 30 min
        const exitTimeout = 30 * 60 * 1000;

        const exitTimer = setTimeout(() => {
            window.close();
        }, exitTimeout);

        return () => {
            clearTimeout(timer);
            clearTimeout(exitTimer);
        };
    }, []);

    const clearActivity = () => {
        dispatch(activityActions.clearActivity());
    };

    useEffect(() => {
        if (!currentStep) {
            const results = {
                steps: steps,
            };
            const url = prefillGoogleForm(results);
            console.log(url);
            setFormUrl(url);
        }
    }, [currentStep, steps, actionList]);

    return (
        <div
            className={`absolute left-[50%] top-1 z-20 flex w-[28%] scale-[0.9] transform flex-col justify-center  rounded-md border border-gray-700 bg-purple-700 bg-opacity-90  p-2 text-white transition-all  duration-500 ${
                isVisible ? 'translate-y-0 opacity-100' : '-translate-y-full opacity-0'
            }`}
        >
            <Accordion type="single" collapsible>
                <AccordionItem value="item-1">
                    <AccordionTrigger>
                        <p className="whitespace-nowrap text-lg">Arm Activity!</p>
                    </AccordionTrigger>

                    <AccordionContent>
                        <div className="my-2 flex items-center gap-x-2">
                            <QuizIcon className="animate-bounce" />
                            <Progress value={completion} />
                            <div role="button" onClick={clearActivity}>
                                <RestartAltIcon></RestartAltIcon>
                            </div>
                        </div>
                        {currentStep ? (
                            <div className="flex flex-col gap-x-2">
                                <p className="text-lg">Your current step is:</p>

                                <div className="rounded bg-slate-50 px-3 py-1 text-gray-800 shadow-sm shadow-white">
                                    <p className="text-xl">{currentStep.name}</p>
                                    <p className="text-sm text-gray-600">
                                        {currentStep.description}
                                    </p>
                                    {currentStep.extra && (
                                        <p className="text-sm font-bold text-gray-600">
                                            {currentStep.extra}
                                        </p>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <>
                                <p className="text-lg">Activity Completed!</p>
                                <div className="flex items-center justify-center gap-x-2 py-4">
                                    <InsertDriveFileIcon className="text-blue-500"></InsertDriveFileIcon>
                                    <a
                                        href={formUrl}
                                        className="text-xl font-bold text-blue-400 underline"
                                    >
                                        Please fill out this form!
                                    </a>
                                </div>
                            </>
                        )}
                    </AccordionContent>
                </AccordionItem>
            </Accordion>
        </div>
    );
};

export default ActivityBox;
