import BaseAction from './BaseAction';
import TextVariable from '../general/text/TextVariable';
import { actionListActions } from '@/redux/ActionListSlice';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

const SleepAction = ({ ...props }) => {
    const dispatch = useDispatch();
    const action = useSelector(state => state.actionList.byId[props.id]);
    const [sleepValue, setsleepValue] = useState(action.value);

    useEffect(() => {
        dispatch(actionListActions.setActionValue({ actionId: props.id, value: sleepValue }));
    }, [sleepValue, dispatch, props.id]);

    return (
        <BaseAction
            className={'h-20 bg-action-sleep'}
            icon={<BedtimeIcon className="text-6xl"></BedtimeIcon>}
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
    id: PropTypes.number.isRequired,
};
export default SleepAction;
