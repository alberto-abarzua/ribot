import BaseAction from './BaseAction';
import TextVariable from '../general/text/TextVariable';
import { actionListActions } from '@/redux/ActionListSlice';
import BuildIcon from '@mui/icons-material/Build';
import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';

const ToolAction = ({ ...props }) => {
    const dispatch = useDispatch();

    const action = useSelector(state => state.actionList.byId[props.id]);
    const [toolValue, setToolValue] = useState(action.value);

    useEffect(() => {
        dispatch(actionListActions.setActionValue({ actionId: props.id, value: toolValue }));
    }, [toolValue, dispatch, props.id]);

    return (
        <BaseAction
            className={'h-20 bg-action-tool'}
            icon={<BuildIcon className="text-6xl"></BuildIcon>}
            {...props}
        >
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-action-data p-2  shadow">
                        <TextVariable
                            label="Tool Value"
                            value={toolValue.toolValue}
                            setValue={value =>
                                setToolValue(prev => ({ ...prev, toolValue: value }))
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
    id: PropTypes.number.isRequired,
};

export default ToolAction;
