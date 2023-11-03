import { renderAction } from '@/utils/actions';
import PropTypes from 'prop-types';

const ActionContainer = ({ actionList }) => {
    return (
        <div className="flex h-full w-full flex-col">
            {actionList.map(action => renderAction(action))}
        </div>
    );
};

ActionContainer.propTypes = {
    actionList: PropTypes.arrayOf(PropTypes.object).isRequired,
};

export default ActionContainer;
