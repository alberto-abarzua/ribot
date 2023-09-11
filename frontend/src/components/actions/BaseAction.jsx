import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import { useRef } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import { ItemTypes } from '@/utils/ItemTypes';
import PropTypes from 'prop-types';

const BaseAction = ({ icon, children, className, id, index, moveInListAction, ...props }) => {
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
            console.log(item);
            const dragIndex = item.index;
            console.log('dragIndex', dragIndex);
            console.log('index', index);
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
                console.log('herer');
                return;
            }
            moveInListAction(dragIndex, hoverIndex);
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
                className={`flex items-center justify-center space-x-4 rounded-md px-6 py-3 text-white shadow ${className}`}
                {...props}
                ref={ref}
                style={{ opacity: isDragging ? 0 : 1 }}
                data-handler-id={handlerId}
            >
                <div className="flex flex-1 items-center justify-start">{icon}</div>
                {children}
                <div className="flex cursor-grab items-center justify-start ">
                    <DragIndicatorIcon className="text-4xl" />
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
    id: PropTypes.string.isRequired,
    index: PropTypes.number.isRequired,
    moveInListAction: PropTypes.func.isRequired,
};

export default BaseAction;
