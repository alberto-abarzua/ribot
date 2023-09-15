import { actionListActions } from '@/redux/ActionListSlice';
import BedtimeIcon from '@mui/icons-material/Bedtime';

import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import TextVariable from '../general/text/TextVariable';
import BaseAction from './BaseAction';

const SleepAction = ({ ...props }) => {
    const dispatch = useDispatch();
    const action = useSelector(state => state.actionList.actions[props.index]);
    const [sleepValue, setsleepValue] = useState(action.value);
    useEffect(() => {
        dispatch(
            actionListActions.updateValueByIndex({
                index: props.index,
                value: sleepValue,
            })
        );
    }, [sleepValue, dispatch, props.index]);

    return (
        <BaseAction
            className={'bg-rose-400'}
            icon={<BedtimeIcon className="text-6xl"></BedtimeIcon>}
            {...props}
        >
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-slate-200 p-2  shadow">
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
    index: PropTypes.number.isRequired,
};
export default SleepAction;
