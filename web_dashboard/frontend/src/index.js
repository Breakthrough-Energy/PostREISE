import 'react-app-polyfill/ie11';
import 'react-app-polyfill/stable';
// These lines MUST be first in src/index.js.
// Details: https://github.com/facebook/create-react-app/tree/master/packages/react-app-polyfill

import React from 'react';
import ReactDOM from 'react-dom';
import ReactGA from 'react-ga';
import * as serviceWorker from './serviceWorker';
import App from './components/App/App';

import './index.css';
import 'normalize.css';

// Initialize google analytics tracking. This id is public
const trackingId = "UA-191995016-3";
ReactGA.initialize(trackingId);

ReactDOM.render(<App />, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
