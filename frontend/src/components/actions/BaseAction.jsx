import { actionListActions } from '@/redux/ActionListSlice';
import { PositionTypes, dragLocation } from '@/utils/dragndrop';
import { ItemTypes } from '@/utils/ItemTypes';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import CloseIcon from '@mui/icons-material/Close';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import ErrorIcon from '@mui/icons-material/Error';
import PropTypes from 'prop-types';
import { useRef } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { useDispatch, useSelector } from 'react-redux';

const BaseAction = ({ icon, children, className, id, ...props }) => {
    const dispatch = useDispatch();
    const action = useSelector(state => state.actionList.byId[id]);

    const running = action.running;
    const valid = action.valid;

    const ref = useRef(null);

    const [{ handlerId }, drop] = useDrop({
        accept: ItemTypes.ACTION,
        collect(monitor) {
            return {
                handlerId: monitor.getHandlerId(),
            };
        },
        hover(item, monitor) {
            const dragPos = dragLocation(ref, monitor);

            if (id === item.id) {
                return;
            }

            if (item.id == action.parentId) {
                return;
            }

            if (dragPos === PositionTypes.OUT) {
                return;
            }

            const before = dragPos === PositionTypes.TOP;
            console.log('hovering on action', id % 1000, dragPos);
            dispatch(
                actionListActions.moveAction({
                    refActionId: item.id, // action to be moved
                    targetActionId: id, // neighbor action to place before or after
                    before: before,
                })
            );
        },
    });

    const [{ isDragging }, drag] = useDrag({
        type: ItemTypes.ACTION,
        item: { id },
        collect: monitor => ({
            isDragging: monitor.isDragging(),
        }),
    });
    if (isDragging) {
        console.log('dragging', id % 1000);
    }

    const onDelete = () => {
        dispatch(actionListActions.deleteAction({ actionId: id }));
    };

    const onDuplicate = () => {
        dispatch(actionListActions.duplicateAction({ actionId: id }));
    };

    drag(drop(ref));

    let indicator = null;

    if (valid) {
        if (running) {
            indicator = (
                <AutorenewIcon className="animate-spin text-4xl transition-all duration-300 group-hover:text-gray-600" />
            );
        } else {
            indicator = (
                <DragIndicatorIcon className="text-4xl transition-all duration-300 group-hover:text-gray-600" />
            );
        }
    } else {
        indicator = (
            <ErrorIcon className="text-5xl text-orange-500 transition-all duration-300 group-hover:text-gray-600" />
        );
    }

    if (!isDragging) {
        return (
            <div
                className={`transform transition-all duration-100  ${className} group relative flex w-full shrink-0 items-center justify-center space-x-4 overflow-hidden rounded-md px-6 py-3 text-white shadow   `}
                {...props}
                ref={ref}
                style={{ opacity: isDragging ? 0 : 1 }}
                data-handler-id={handlerId}
            >
                <div className="flex flex-shrink-0 items-center justify-start">{icon}</div>
                {children}
                <div className="flex cursor-grab items-center justify-start ">{indicator}</div>
                <div
                    className="absolute right-0 top-0 flex cursor-pointer items-center justify-center rounded-bl-md p-1 text-gray-300  transition-all duration-300 hover:bg-gray-100 hover:text-gray-500"
                    onClick={onDelete}
                >
                    <CloseIcon className="text-xl"></CloseIcon>
                </div>
                <div
                    className="absolute bottom-0 right-0 flex cursor-pointer items-center justify-center rounded-tl-md p-1 text-gray-300  transition-all duration-300 hover:bg-gray-100 hover:text-gray-500"
                    onClick={onDuplicate}
                >
                    <ContentCopyIcon className="text-xl"></ContentCopyIcon>
                </div>
                <p>{id % 1000}</p>
            </div>
        );
    } else {
        return (
            <div
                className="h-20 w-full rounded-md border border-dashed bg-slate-100 shadow"
                {...props}
                ref={ref}
                data-handler-id={handlerId}
            ></div>
        );
    }
};

BaseAction.propTypes = {
    icon: PropTypes.element.isRequired,
    children: PropTypes.element.isRequired,
    className: PropTypes.string,
    id: PropTypes.number.isRequired,
};

export default BaseAction;
