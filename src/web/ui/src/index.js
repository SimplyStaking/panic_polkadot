import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import AppLauncher from './app';

ReactDOM.render(
  <Router>
    <AppLauncher />
  </Router>,
  document.getElementById('root'),
);
