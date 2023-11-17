import store from '@/redux/store';
import PropTypes from 'prop-types';
import { HTML5toTouch } from 'rdndmb-html5-to-touch';
import { DndProvider } from 'react-dnd-multi-backend';
import { Provider } from 'react-redux';

const Providers = ({ children }) => {
    return (
        <Provider store={store}>
            <DndProvider options={HTML5toTouch}>{children}</DndProvider>
        </Provider>
    );
};

Providers.propTypes = {
    children: PropTypes.node.isRequired,
};

export default Providers;
