import React, { useLayoutEffect } from 'react';
import { configureStore } from '@reduxjs/toolkit';
import { combineReducers } from 'redux';
import { Provider } from 'react-redux';
import { usePath, useRoutes } from 'hookrouter';

import Dashboard from '../dashboard/Dashboard/Dashboard';
import dashboardSlice from '../../slices/dashboardSlice/dashboardSlice';
import { setPageTracking } from '../../util/util';
import HourlyUtilization from '../HourlyDemo/HourlyUtilization';

export const routes = {
  '/': () => <Dashboard />,
  '/hourly': () => <HourlyUtilization />
};

// Using combineReducers as prep for adding more stores
const store = configureStore({ reducer: combineReducers({ dashboardSlice })});

const App = () => {
  const routeResult = useRoutes(routes);
  useLayoutEffect(() => {
    window.scrollTo(0, 0);
  });

  const path = usePath();
  setPageTracking(path);

  if (routeResult) {
    // Provider = redux provider
    return (
      <Provider store={store}>
        {routeResult}
      </Provider>
    );
  } else {
    return '404 Page not found';
  }
}

export default App;
