import { actionListActions } from '@/redux/ActionListSlice';
import { renderAction } from '@/utils/actions';
import byIdContext from '@/utils/byIdContext';
import { ItemTypes } from '@/utils/ItemTypes';
import AddIcon from '@mui/icons-material/Add';
import PropTypes from 'prop-types';
import { useContext, useState } from 'react';
import { useDrop } from 'react-dnd';
import { useDispatch } from 'react-redux';

const ActionContainer = ({ actionList }) => {
    const dispatch = useDispatch();
    const byId = useContext(byIdContext);
    const [isOver, setIsOver] = useState(false);

    actionList = actionList.map(action => byId[action.id]);
    const [, drop] = useDrop({
        accept: ItemTypes.ACTION,
        collect(monitor) {
            setIsOver(monitor.isOver());
            return {
                handlerId: monitor.getHandlerId(),
            };
        },
        drop(item) {
            dispatch(
                actionListActions.pushActionToValue({
                    actionId: null,
                    actionToAddId: item.id,
                    type: item.type,
                    value: item.value,
                })
            );
        },
    });

    const dropAreaStyles = isOver ? 'bg-blue-300 ' : '';

    if (actionList.length > 0) {
        return (
            <div className="flex h-full w-full flex-col gap-y-4 p-4">
                {actionList && actionList.map(action => renderAction(action))}
            </div>
        );
    } else {
        return (
            <div
                className={`flex h-24 w-full items-center justify-center rounded-md ${dropAreaStyles}`}
                ref={drop}
            >
                <AddIcon className="scale-[2.0] transform text-gray-500"></AddIcon>
            </div>
        );
    }
};

ActionContainer.propTypes = {
    actionList: PropTypes.arrayOf(PropTypes.object).isRequired,
};

export default ActionContainer;
