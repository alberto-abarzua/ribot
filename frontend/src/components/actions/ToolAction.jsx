import BaseAction from '@/components/actions/BaseAction';
import TextVariable from '@/components/general/text/TextVariable';
import { actionListActions } from '@/redux/ActionListSlice';
import BuildIcon from '@mui/icons-material/Build';
import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';

const ToolAction = ({ action, ...props }) => {
    const id = action.id;

    const dispatch = useDispatch();

    const [toolValue, setToolValue] = useState(action.value);

    useEffect(() => {
        let valid = toolValue.toolValue >= -100 && toolValue.toolValue <= 100;
        dispatch(actionListActions.setValidStatus({ actionId: id, valid: valid }));

        dispatch(actionListActions.setActionValue({ actionId: id, value: toolValue }));
    }, [toolValue, dispatch, id]);

    return (
        <BaseAction
            className={' bg-action-tool'}
            icon={<BuildIcon className="text-6xl"></BuildIcon>}
            action={action}
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
    action: PropTypes.shape({
        type: PropTypes.string.isRequired,
        id: PropTypes.number.isRequired,
        value: PropTypes.shape({
            toolValue: PropTypes.number.isRequired,
        }).isRequired,
    }).isRequired,
};

export default ToolAction;
