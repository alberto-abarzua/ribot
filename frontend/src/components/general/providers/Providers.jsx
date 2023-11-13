import store from '@/redux/store';
import PropTypes from 'prop-types';
import React from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Provider } from 'react-redux';

const Providers = ({ children }) => {
    return (
        <Provider store={store}>
            <DndProvider backend={HTML5Backend}>{children}</DndProvider>
        </Provider>
    );
};

Providers.propTypes = {
    children: PropTypes.node.isRequired,
};

export default Providers;
