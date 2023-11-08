import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { actionListActions } from '@/redux/ActionListSlice';
import { ItemTypes } from '@/utils/ItemTypes';
import PropTypes from 'prop-types';
import { useDrag } from 'react-dnd';
import { useDispatch } from 'react-redux';

const ToolBarElement = ({ element }) => {
    const dispatch = useDispatch();

    const [, dragRef] = useDrag({
        type: ItemTypes.ACTION,
        item: () => {
            return { id: Date.now(), type: element.type, value: element.value };
        },
        collect: monitor => ({
            isDragging: monitor.isDragging(),
        }),
    });

    const addToActionList = () => {
        dispatch(
            actionListActions.addAction({
                type: element.type,
                value: element.value,
                parentId: null,
            })
        );
    };

    return (
        <div>
            <TooltipProvider>
                <Tooltip delayDuration={300}>
                    <TooltipTrigger>
                        <div
                            className={`flex h-14 w-20 shrink grow basis-0 items-center justify-center gap-2.5 ${element.bgColor} ${element.hovercolor}`}
                            ref={dragRef}
                            onClick={addToActionList}
                        >
                            <div className="relative flex h-10 w-10 items-center justify-center text-3xl text-white">
                                <element.icon className="text-3xl"></element.icon>
                            </div>
                        </div>
                    </TooltipTrigger>

                    <TooltipContent>
                        <p>{element.helpText} </p>
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        </div>
    );
};

ToolBarElement.propTypes = {
    element: PropTypes.shape({
        name: PropTypes.string.isRequired,
        type: PropTypes.string.isRequired,
        icon: PropTypes.object.isRequired,
        bgColor: PropTypes.string.isRequired,
        value: PropTypes.any.isRequired,
        hovercolor: PropTypes.string.isRequired,
        helpText: PropTypes.string.isRequired,
    }).isRequired,
};
export default ToolBarElement;
