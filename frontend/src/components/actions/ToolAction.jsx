import { actionListActions } from '@/redux/ActionListSlice';
import BuildIcon from '@mui/icons-material/Build';

import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import TextVariable from '../general/text/TextVariable';
import BaseAction from './BaseAction';

const ToolAction = ({ ...props }) => {
    const dispatch = useDispatch();

    const action = useSelector(state => state.actionList.actions[props.index]);
    const [toolValue, setToolValue] = useState(action.value);

    useEffect(() => {
        dispatch(
            actionListActions.updateValueByIndex({
                index: props.index,
                value: toolValue,
            })
        );
    }, [toolValue, dispatch, props.index]);

    return (
        <BaseAction
            className={'bg-yellow-200'}
            icon={<BuildIcon className="text-6xl"></BuildIcon>}
            {...props}
        >
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-slate-200 p-2  shadow">
                        <TextVariable
                            label="Tool Value"
                            value={toolValue.tool_value}
                            setValue={value =>
                                setToolValue(prev => ({ ...prev, tool_value: value }))
                            }
                            disabled={false}
                        />
                    </div>
                </div>
            </div>
        </BaseAction>
    );
};

ToolAction.propTypes = {
    index: PropTypes.number.isRequired,
};

export default ToolAction;
