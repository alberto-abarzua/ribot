import { renderAction } from '@/utils/actions';
import PropTypes from 'prop-types';

const ActionContainer = ({ actionList }) => {
    return (
        <div className="flex h-full w-full flex-col gap-y-4 p-4">
            {actionList && actionList.map(action => renderAction(action))}
        </div>
    );
};

ActionContainer.propTypes = {
    actionList: PropTypes.arrayOf(PropTypes.object).isRequired,
};

export default ActionContainer;
