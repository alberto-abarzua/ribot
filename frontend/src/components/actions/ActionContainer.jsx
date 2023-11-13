import { actionListActions } from '@/redux/ActionListSlice';
import { renderAction } from '@/utils/actions';
import byIdContext from '@/utils/byIdContext';
import { ItemTypes } from '@/utils/ItemTypes';
import AddIcon from '@mui/icons-material/Add';
import PropTypes from 'prop-types';
import { useContext, useState } from 'react';
import { useDrop } from 'react-dnd';
import { NativeTypes } from 'react-dnd-html5-backend';
import { useDispatch } from 'react-redux';

const ActionContainer = ({ actionList, action = null }) => {
    const dispatch = useDispatch();
    const byId = useContext(byIdContext);
    const [isOver, setIsOver] = useState(false);
    console.log('IN action container', action);

    actionList = actionList.map(action => byId[action.id]);
    const [, drop] = useDrop({
        accept: [ItemTypes.ACTION, NativeTypes.FILE],
        collect(monitor) {
            setIsOver(monitor.isOver());
            return {
                handlerId: monitor.getHandlerId(),
            };
        },
        drop(item) {
            if (item.files) {
                const file = item.files[0];
                const reader = new FileReader();
                reader.onload = event => {
                    const actionToAdd = JSON.parse(event.target.result);
                    console.log('action container drop', action);
                    dispatch(
                        actionListActions.addFromJson({
                            actionId: action ? action.id : null,
                            actionToAdd: actionToAdd,
                        })
                    );
                };

                reader.readAsText(file);
            } else {
                dispatch(
                    actionListActions.pushActionToValue({
                        actionId: action ? action.id : null,
                        actionToAddId: item.id,
                        type: item.type,
                        value: item.value,
                    })
                );
            }
        },
    });

    const dropAreaStyles = isOver ? 'bg-blue-300 ' : '';

    return (
        <div className="flex h-full w-full flex-col gap-y-4 p-4">
            {actionList && actionList.map(action => renderAction(action))}
            {((action && action.value.length === 0) || action == null) && (
                <div
                    className={`flex h-24 w-full cursor-cell flex-col items-center justify-center rounded-md hover:bg-slate-200 ${dropAreaStyles}`}
                    ref={drop}
                >
                    <AddIcon className="scale-[2.0] transform text-gray-500"></AddIcon>
                    <p className="select-none p-3 italic text-gray-700">
                        Drag Actions or Action File here!
                    </p>
                </div>
            )}
        </div>
    );
};

ActionContainer.propTypes = {
    actionList: PropTypes.arrayOf(PropTypes.object).isRequired,
    action: PropTypes.shape({
        id: PropTypes.number,
        parentId: PropTypes.number,
        running: PropTypes.bool,
        valid: PropTypes.bool,
        type: PropTypes.string,
        value: PropTypes.any,
    }),
};

export default ActionContainer;
