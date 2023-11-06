import ActionContainer from '@/components/actions/ActionContainer';
import BaseAction from '@/components/actions/BaseAction';
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from '@/components/ui/accordion';
import { actionListActions } from '@/redux/ActionListSlice';
import { ItemTypes } from '@/utils/ItemTypes';
import AddIcon from '@mui/icons-material/Add';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize';
import PropTypes from 'prop-types';
import { useState } from 'react';
import { useDrop } from 'react-dnd';
import { useDispatch } from 'react-redux';

const ActionSet = ({ action, ...props }) => {
    const dispatch = useDispatch();

    const id = action.id;
    const [isOver, setIsOver] = useState(false);

    const actionList = action.value;

    const [, drop] = useDrop({
        accept: ItemTypes.ACTION,
        collect(monitor) {
            setIsOver(monitor.isOver());
            return {
                handlerId: monitor.getHandlerId(),
            };
        },
        drop(item) {
            if (item.id === id) {
                return;
            }
            dispatch(actionListActions.pushActionToValue({ actionId: id, actionToAddId: item.id }));
        },
    });

    const dropAreaStyles = isOver ? 'bg-blue-300 ' : '';

    const body =
        actionList.length === 0 ? (
            <div
                className={`flex h-24 w-full items-center justify-center rounded-md ${dropAreaStyles}`}
                ref={drop}
            >
                <AddIcon className="scale-[2.0] transform text-gray-500"></AddIcon>
            </div>
        ) : (
            <div className="w-full px-2">
                <Accordion type="single" collapsible>
                    <AccordionItem value="item-1">
                        <AccordionTrigger>Sub Actions</AccordionTrigger>
                        <AccordionContent>
                            <ActionContainer actionList={actionList}></ActionContainer>
                        </AccordionContent>
                    </AccordionItem>
                </Accordion>
            </div>
        );
    return (
        <BaseAction
            className={' bg-action-set'}
            icon={<DashboardCustomizeIcon className="text-6xl"></DashboardCustomizeIcon>}
            action={action}
            {...props}
        >
            <div className=" flex flex-1 items-center  justify-end">
                <div className="flex w-full items-center justify-end text-black">
                    <div className="my-3 flex w-full flex-1 items-center justify-center rounded-md bg-action-data  shadow">
                        {body}
                    </div>
                </div>
            </div>
        </BaseAction>
    );
};

ActionSet.propTypes = {
    action: PropTypes.shape({
        type: PropTypes.string.isRequired,
        id: PropTypes.number.isRequired,
        value: PropTypes.arrayOf(PropTypes.any).isRequired,
    }).isRequired,
};

export default ActionSet;
