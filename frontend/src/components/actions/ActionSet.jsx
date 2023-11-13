import ActionContainer from '@/components/actions/ActionContainer';
import BaseAction from '@/components/actions/BaseAction';
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from '@/components/ui/accordion';
import { actionListActions } from '@/redux/ActionListSlice';
import DashboardCustomizeIcon from '@mui/icons-material/DashboardCustomize';
import PropTypes from 'prop-types';
import { useDispatch } from 'react-redux';

const ActionSet = ({ action, ...props }) => {
    const dispatch = useDispatch();

    const name = action.name ? action.name : '';

    const actionList = action.value;

    const body = (
        <div className="w-full px-2">
            <Accordion type="single" collapsible defaultValue="item-1" className="w-full">
                <AccordionItem value="item-1">
                    <AccordionTrigger>
                        <input
                            type="search"
                            autoComplete="off"
                            className="focus:border-blue-3 w-2/3 rounded-md border-none bg-slate-300 px-2 py-1 text-lg italic text-gray-900 hover:border-blue-300 "
                            placeholder="Name This Action Set"
                            value={name}
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
                        <ActionContainer actionList={actionList} action={action}></ActionContainer>
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
