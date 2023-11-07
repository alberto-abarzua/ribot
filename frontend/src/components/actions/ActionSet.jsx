import ActionContainer from '@/components/actions/ActionContainer';
import BaseAction from '@/components/actions/BaseAction';
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from '@/components/ui/accordion';
import { Label } from '@/components/ui/label';
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
                <Accordion type="single" collapsible defaultValue="item-1" className="w-full">
                    <AccordionItem value="item-1">
                        <AccordionTrigger>
                            <input
                                type="search"
                                autoComplete="off"
                                className="focus:border-blue-3 w-2/3 rounded-md border-none bg-slate-300 px-2 py-1 text-lg italic text-gray-900 hover:border-blue-300 "
                                placeholder="Change Action Set Name"
                                value={action.name}
                                name="actionsetlabel"
                                onChange={e =>
                                    dispatch(
                                        actionListActions.setActionName({
                                            actionId: action.id,
                                            name: e.target.value,
                                        })
                                    )
                                }
                            />
                        </AccordionTrigger>
                        <AccordionContent>
                            <ActionContainer actionList={actionList}></ActionContainer>
                        </AccordionContent>
                    </AccordionItem>
                </Accordion>
            </div>
        );
    return (
        <BaseAction
            className={' bg-action-set opacity-90'}
            icon={<DashboardCustomizeIcon className="text-6xl"></DashboardCustomizeIcon>}
            action={action}
            {...props}
        >
            <div className=" flex flex-1 items-center  justify-end">
                <div className="flex w-full flex-col items-start justify-center text-black">
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
        name: PropTypes.string,
    }).isRequired,
};

export default ActionSet;
