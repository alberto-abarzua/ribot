import { actionListActions } from '@/redux/ActionListSlice';
import { ItemTypes } from '@/utils/ItemTypes';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import CloseIcon from '@mui/icons-material/Close';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';

import PropTypes from 'prop-types';
import { useRef } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { useDispatch, useSelector } from 'react-redux';
const BaseAction = ({ icon, children, className, id, index, ...props }) => {
    const dispatch = useDispatch();
    const running = useSelector(state => state.actionList.actions[index].running);
    console.log('running ss', running);
    const ref = useRef(null);
    const [{ handlerId }, drop] = useDrop({
        accept: ItemTypes.ACTION,
        collect(monitor) {
            return {
                handlerId: monitor.getHandlerId(),
            };
        },
        hover(item, monitor) {
            if (!ref.current) {
                return;
            }
            const dragIndex = item.index;
            const hoverIndex = index;
            if (dragIndex === hoverIndex) {
                return;
            }
            const hoverBoundingRect = ref.current.getBoundingClientRect();
            const hoverMiddleY = (hoverBoundingRect.bottom - hoverBoundingRect.top) / 2;
            const clientOffset = monitor.getClientOffset();
            const hoverClientY = clientOffset.y - hoverBoundingRect.top;
            if (
                (dragIndex < hoverIndex && hoverClientY < hoverMiddleY) ||
                (dragIndex > hoverIndex && hoverClientY > hoverMiddleY)
            ) {
                return;
            }
            dispatch(
                actionListActions.moveInList({
                    dragIndex,
                    hoverIndex,
                })
            );

            item.index = hoverIndex;
        },
    });
    const [{ isDragging }, drag] = useDrag({
        type: ItemTypes.ACTION,
        item: { id, index },
        collect: monitor => ({
            isDragging: monitor.isDragging(),
        }),
    });
    drag(drop(ref));
    if (!isDragging) {
        return (
            <div
                className={`transform transition-all duration-100  ${className} group relative flex w-full max-w-lg shrink-0 items-center justify-center space-x-4 overflow-hidden rounded-md px-6 py-3 text-white shadow   `}
                {...props}
                ref={ref}
                style={{ opacity: isDragging ? 0 : 1 }}
                data-handler-id={handlerId}
            >
                <div className="flex flex-1 items-center justify-start">{icon}</div>
                {children}
                <div className="flex cursor-grab items-center justify-start ">
                    {!running && (
                        <DragIndicatorIcon className="text-4xl transition-all duration-300 group-hover:text-gray-600" />
                    )}
                    {running && (
                        <AutorenewIcon className="animate-spin text-4xl transition-all duration-300 group-hover:text-gray-600" />
                    )}
                </div>
                <div
                    className="absolute right-0 top-0 flex cursor-pointer items-center justify-center rounded-bl-md p-1 text-gray-300  transition-all duration-300 hover:bg-gray-100 hover:text-gray-500"
                    onClick={() => dispatch(actionListActions.deleteAction(index))}
                >
                    <CloseIcon className="text-xl"></CloseIcon>
                </div>
            </div>
        );
    } else {
        return (
            <div
                className=" h-24 w-full max-w-lg rounded-md border border-dashed bg-slate-100 shadow"
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
    index: PropTypes.number.isRequired,
};

export default BaseAction;
