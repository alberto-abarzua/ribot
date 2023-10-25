'use client';

import store from '@/redux/store';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Provider } from 'react-redux';

// eslint-disable-next-line react/prop-types
const Providers = ({ children }) => {
    return (
        <Provider store={store}>
            <DndProvider backend={HTML5Backend}>{children}</DndProvider>
        </Provider>
    );
};

export default Providers;
