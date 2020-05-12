import React from 'react';
import { Route, Switch } from 'react-router-dom';
import Dashboard from '../pages/dashboard';
import AlertLogs from '../pages/alerts/alert_logs';
import { MainUserConfig } from '../pages/configs/main_user_config';
import Preferences from '../pages/alerts/preferences';
import { NodesConfig } from '../pages/configs/nodes_config';
import ReposConfig from '../pages/configs/repos_config';
import ErrorPage from '../pages/error';
import { RESOURCE_NOT_FOUND } from '../utils/error';

function Routes() {
  return (
    <Switch>
      <Route path="/" exact render={() => (<Dashboard />)} />
      <Route path="/alerts/logs" exact render={() => (<AlertLogs />)} />
      <Route path="/settings/main" exact render={() => (<MainUserConfig />)} />
      <Route path="/settings/nodes" exact render={() => (<NodesConfig />)} />
      <Route
        path="/settings/repositories"
        exact
        render={() => (<ReposConfig />)}
      />
      <Route
        path="/alerts/preferences"
        exact
        render={() => (<Preferences />)}
      />
      <Route path="*" render={() => (<ErrorPage err={RESOURCE_NOT_FOUND} />)} />
    </Switch>
  );
}

export default Routes;
