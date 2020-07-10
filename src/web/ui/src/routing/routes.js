import React from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import Dashboard from '../pages/dashboard';
import AlertLogs from '../pages/alerts/logs';
import MainSettingsPage from '../pages/settings/main';
import Preferences from '../pages/alerts/preferences';
import NodesSettingsPage from '../pages/settings/nodes';
import ReposSettingsPage from '../pages/settings/repos';
import ErrorPage from '../pages/error';
import AuthenticationPage from '../pages/authentication';
import { RESOURCE_NOT_FOUND } from '../utils/error';

function PrivateRoute({ component: Component, isAuthenticated, ...rest }) {
  return (
    <Route
      {...rest}
      render={props => (isAuthenticated === true
        ? <Component {...props} />
        : (
          <Redirect to={{
            pathname: '/login', state: { from: props.location },
          }}
          />
        ))}
    />
  );
}

function LoginRoute({
  component: Component, isAuthenticated, setAuthentication, ...rest
}) {
  return (
    <Route
      {...rest}
      render={props => (isAuthenticated === true
        ? (
          <Redirect to={{
            pathname: '/', state: { from: props.location },
          }}
          />
        )
        : <Component setAuthentication={setAuthentication} />
      )}
    />
  );
}

function Routes({ isAuthenticated, setAuthentication }) {
  return (
    <Switch>
      <LoginRoute
        path="/login"
        exact
        component={AuthenticationPage}
        isAuthenticated={isAuthenticated}
        setAuthentication={setAuthentication}
      />
      <PrivateRoute
        path="/"
        exact
        component={Dashboard}
        isAuthenticated={isAuthenticated}
      />
      <PrivateRoute
        path="/alerts/logs"
        exact
        component={AlertLogs}
        isAuthenticated={isAuthenticated}
      />
      <PrivateRoute
        path="/alerts/preferences"
        exact
        component={Preferences}
        isAuthenticated={isAuthenticated}
      />
      <PrivateRoute
        path="/settings/main"
        exact
        component={MainSettingsPage}
        isAuthenticated={isAuthenticated}
      />
      <PrivateRoute
        path="/settings/nodes"
        exact
        component={NodesSettingsPage}
        isAuthenticated={isAuthenticated}
      />
      <PrivateRoute
        path="/settings/repositories"
        exact
        component={ReposSettingsPage}
        isAuthenticated={isAuthenticated}
      />
      <Route path="*" render={() => (<ErrorPage err={RESOURCE_NOT_FOUND} />)} />
    </Switch>
  );
}

PrivateRoute.propTypes = ({
  component: PropTypes.oneOfType([
    PropTypes.element, PropTypes.func,
  ]).isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  location: PropTypes.oneOfType([
    PropTypes.string, PropTypes.object,
  ]),
});

PrivateRoute.defaultProps = {
  location: undefined,
};

LoginRoute.propTypes = ({
  component: PropTypes.oneOfType([
    PropTypes.element, PropTypes.func,
  ]).isRequired,
  isAuthenticated: PropTypes.bool.isRequired,
  location: PropTypes.oneOfType([
    PropTypes.string, PropTypes.object,
  ]),
  setAuthentication: PropTypes.func.isRequired,
});

LoginRoute.defaultProps = {
  location: undefined,
};

Routes.propTypes = forbidExtraProps({
  isAuthenticated: PropTypes.bool.isRequired,
  setAuthentication: PropTypes.func.isRequired,
});

export default Routes;
