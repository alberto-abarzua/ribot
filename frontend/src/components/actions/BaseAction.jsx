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
import { useDispatch } from 'react-redux';

const BaseAction = ({ icon, children, className, action, ...props }) => {
    const id = action.id;
    const dispatch = useDispatch();

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

            if (
                id == item.id ||
                item.id == action.parentId ||
                dragPos === PositionTypes.OUT ||
                dragPos === PositionTypes.MIDDLE
            )
                return;

            dispatch(
                actionListActions.moveAction({
                    refActionId: item.id,
                    targetActionId: id,
                    before: dragPos === PositionTypes.TOP,
                    type: item.type,
                    value: item.value,
                })
            );
        },
    });

    const [{ isDragging }, drag, dragPreview] = useDrag({
        type: ItemTypes.ACTION,
        item: { id },
        collect: monitor => ({
            isDragging: monitor.isDragging(),
        }),
        isDragging: monitor => id === monitor.getItem().id,
    });

    dragPreview(drop(ref));

    const onDelete = () => {
        dispatch(actionListActions.deleteAction({ actionId: id }));
    };

    const onDuplicate = () => {
        dispatch(actionListActions.duplicateAction({ actionId: id }));
    };

    let indicator = valid ? (
        running ? (
            <AutorenewIcon className="animate-spin text-4xl transition-all duration-300 group-hover:text-gray-600" />
        ) : (
            <div onMouseDown={e => e.stopPropagation()} ref={drag}>
                <DragIndicatorIcon className="text-4xl transition-all duration-300 group-hover:text-slate-300" />
            </div>
        )
    ) : (
        <ErrorIcon className="text-5xl text-orange-500 transition-all duration-300 group-hover:text-gray-600" />
    );

    if (!isDragging) {
        return (
            <div
                className={`transform transition-all duration-100 ${className} group relative flex w-full shrink-0 items-center justify-center space-x-4 overflow-hidden rounded-md px-6 py-3 text-white shadow`}
                {...props}
                ref={ref}
                data-handler-id={handlerId}
            >
                <div className="flex flex-shrink-0 items-center justify-start">{icon}</div>
                {children}
                <div className="flex cursor-grab items-center justify-start ">{indicator}</div>
                <div
                    className="absolute right-0 top-0 flex cursor-pointer items-center justify-center rounded-bl-md p-1 text-gray-300 transition-all duration-300 hover:bg-gray-100 hover:text-gray-500"
                    onClick={onDelete}
                >
                    <CloseIcon className="text-xl" />
                </div>
                <div
                    className="absolute bottom-0 right-0 flex cursor-pointer items-center justify-center rounded-tl-md p-1 text-gray-300 transition-all duration-300 hover:bg-gray-100 hover:text-gray-500"
                    onClick={onDuplicate}
                >
                    <ContentCopyIcon className="text-xl" />
                </div>
            </div>
        );
    } else {
        return (
            <div
                className="h-10 w-full rounded-md border border-dashed bg-blue-500 opacity-40 shadow"
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
    action: PropTypes.shape({
        id: PropTypes.number.isRequired,
        parentId: PropTypes.number,
        running: PropTypes.bool.isRequired,
        valid: PropTypes.bool.isRequired,
    }).isRequired,
};

export default BaseAction;
