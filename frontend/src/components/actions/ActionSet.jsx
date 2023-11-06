import ActionContainer from '@/components/actions/ActionContainer';
import BaseAction from '@/components/actions/BaseAction';
import { actionListActions } from '@/redux/ActionListSlice';
import { ItemTypes } from '@/utils/ItemTypes';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize';
import PropTypes from 'prop-types';
import { useDrop } from 'react-dnd';
import { useSelector, useDispatch } from 'react-redux';
const ActionSet = ({ ...props }) => {
    const dispatch = useDispatch();

    const action = useSelector(state => state.actionList.byId[props.id]);

    const actionList = action.value;

    const [, drop] = useDrop({
        accept: ItemTypes.ACTION,
        collect(monitor) {
            return {
                handlerId: monitor.getHandlerId(),
            };
        },
        drop(item) {
            if (item.id === props.id) {
                return;
            }
            dispatch(
                actionListActions.pushActionToValue({ actionId: props.id, actionToAddId: item.id })
            );
        },
    });

    const body =
        actionList.length === 0 ? (
            <div ref={drop}>Drag here</div>
        ) : (
            <ActionContainer actionList={actionList}></ActionContainer>
        );

    return (
        <BaseAction
            className={' bg-action-set'}
            icon={<DashboardCustomizeIcon className="text-6xl"></DashboardCustomizeIcon>}
            {...props}
        >
            <div className="flex flex-1 items-center  justify-end">
                <div className="flex items-center justify-end text-black">
                    <div className=" flex items-center justify-center rounded-md bg-action-data p-2  shadow">
                        {body}
                    </div>
                </div>
            </div>
        </BaseAction>
    );
};

ActionSet.propTypes = {
    id: PropTypes.number.isRequired,
};

export default ActionSet;
