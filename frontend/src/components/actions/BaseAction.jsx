import { actionListActions } from '@/redux/ActionListSlice';
import { ItemTypes } from '@/utils/ItemTypes';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';

import PropTypes from 'prop-types';
import { useRef } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { useDispatch } from 'react-redux';

const BaseAction = ({ icon, children, className, id, index, ...props }) => {
    const dispatch = useDispatch();

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
                className={`group flex items-center justify-center space-x-4 rounded-md px-6 py-3 text-white shadow ${className}`}
                {...props}
                ref={ref}
                style={{ opacity: isDragging ? 0 : 1 }}
                data-handler-id={handlerId}
            >
                <div className="flex flex-1 items-center justify-start">{icon}</div>
                {children}
                <div className="flex cursor-grab items-center justify-start ">
                    <DragIndicatorIcon className="text-4xl transition-all duration-300 group-hover:text-gray-600" />
                </div>
            </div>
        );
    } else {
        return (
            <div
                className=" h-24 w-full rounded-md border border-dashed bg-slate-100 shadow"
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
