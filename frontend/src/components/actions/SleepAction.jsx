import BaseAction from './BaseAction';
import TextVariable from '../general/text/TextVariable';
import { actionListActions } from '@/redux/ActionListSlice';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';

const SleepAction = ({ action, ...props }) => {
    const id = action.id;
    const dispatch = useDispatch();
    const [sleepValue, setsleepValue] = useState(action.value);

    useEffect(() => {
        dispatch(actionListActions.setActionValue({ actionId: id, value: sleepValue }));
    }, [sleepValue, dispatch, id]);

    return (
        <BaseAction
            className={'bg-action-sleep'}
            icon={<BedtimeIcon className="text-6xl"></BedtimeIcon>}
            action={action}
            {...props}
        >
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-action-data p-2  shadow">
                        <TextVariable
                            label="Timeout (s)"
                            setValue={value =>
                                setsleepValue(prev => ({ ...prev, duration: value }))
                            }
                            value={sleepValue.duration}
                            disabled={false}
                        />
                    </div>
                </div>
            </div>
        </BaseAction>
    );
};

SleepAction.propTypes = {
    action: PropTypes.shape({
        type: PropTypes.string.isRequired,
        id: PropTypes.number.isRequired,
        value: PropTypes.shape({
            duration: PropTypes.number.isRequired,
        }).isRequired,
    }).isRequired,
};
export default SleepAction;
