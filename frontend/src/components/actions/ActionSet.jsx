import BaseAction from './BaseAction';
// import { actionListActions } from '@/redux/ActionListSlice';
import { BaseActionObj } from '@/utils/actions';
import BuildIcon from '@mui/icons-material/Build';
import PropTypes from 'prop-types';
import { useSelector } from 'react-redux';

const ActionSet = ({ ...props }) => {
    // const dispatch = useDispatch();

    const action = useSelector(state => state.actionList.actions[props.index]);
    const actionObj = BaseActionObj.fromSerializable(action);

    return (
        <BaseAction
            className={'h-20 bg-action-set'}
            icon={<BuildIcon className="text-6xl"></BuildIcon>}
            {...props}
        >
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-action-data p-2  shadow">
                        {actionObj.value.map(action => action.render())}
                    </div>
                </div>
            </div>
        </BaseAction>
    );
};

ActionSet.propTypes = {
    index: PropTypes.number.isRequired,
};

export default ActionSet;
