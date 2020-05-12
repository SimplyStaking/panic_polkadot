import React, { Component } from 'react';
import { Container, Form } from 'react-bootstrap';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import Spinner from 'react-bootstrap/Spinner';
import {
  ToastsContainer,
  ToastsStore,
  ToastsContainerPosition,
} from 'react-toasts';
import { CollapsibleForm, Trigger } from '../configs/main_user_config';
import { capitalizeSentence, toBool } from '../../utils/string';
import { getConfig, sendConfig } from '../../utils/data';
import {
  ALERTS_CONFIG_ALERT_NAMES,
  ALERTS_CONFIG_SECTION_NAMES,
} from '../../utils/constants';
import '../../style/style.css';
import ErrorPage from '../error';
import { INTERNAL_ALERTS_CONFIG_NOT_FOUND } from '../../utils/error';

function sectionNameDisplay(str) {
  if (str in ALERTS_CONFIG_SECTION_NAMES) {
    return ALERTS_CONFIG_SECTION_NAMES[str];
  }
  return str.split('_').map(capitalizeSentence).join(' ');
}

function allAlertsEnabled(alertsEnabled) {
  // Checks if every alert is enabled. If yes return true, otherwise return
  // false.
  const result = Object.entries(alertsEnabled).map(
    ([_, enabled]) => toBool(enabled),
  );
  return result.every(alertEnabled => alertEnabled === true);
}

function alertNameDisplay(str) {
  if (str in ALERTS_CONFIG_ALERT_NAMES) {
    return ALERTS_CONFIG_ALERT_NAMES[str];
  }
  return capitalizeSentence(str.split('_').join(' '));
}

function SectionTableContent(props) {
  const content = [];
  Object.entries(props.alertsEnabled).forEach(([alert, enabled]) => {
    content.push(
      <tr key={alert}>
        <td>{alertNameDisplay(alert)}</td>
        <td className="column-style">
          <Form>
            <Form.Check
              className="switch-style"
              type="switch"
              id={`section-${alert}-config-switch`}
              label=""
              defaultChecked={toBool(enabled)}
              onChange={() => props.enableDisableAlert(props.section, alert)}
            />
          </Form>
        </td>
      </tr>,
    );
  });

  return content;
}

function SectionTable({ alertsEnabled, enableDisableAlert, section }) {
  return (
    <Table responsive borderless className="tables-style-2">
      <tbody>
        <SectionTableContent
          alertsEnabled={alertsEnabled}
          enableDisableAlert={enableDisableAlert}
          section={section}
        />
      </tbody>
    </Table>
  );
}

function AlertsConfigContent({ alertsConfigJson, enableDisableAlert }) {
  const forms = [];

  Object.entries(alertsConfigJson).forEach(
    ([section, sectionAlertsEnabled]) => {
      forms.push(
        <CollapsibleForm
          trigger={(
            <Trigger
              name={sectionNameDisplay(section)}
              checkEnabled={allAlertsEnabled(sectionAlertsEnabled)}
            />
          )}
          triggerClassName="collapsible-style"
          triggerOpenedClassName="collapsible-style"
          content={(
            <SectionTable
              alertsEnabled={sectionAlertsEnabled}
              enableDisableAlert={enableDisableAlert}
              section={section}
            />
        )}
          key={section}
          open
        />,
      );
    },
  );

  return <div className="div-style">{forms}</div>;
}

class AlertsConfig extends Component {
  constructor(props) {
    super(props);
    // We need to set a timer that tries to get the nodes currently in config
    // periodically until the data is fetched. This must be done since data from
    // the config must be fetched once.
    this.dataTimer = null;
    this.state = {
      alertsConfigJson: {},
      isFetchingData: true,
    };
  }

  componentDidMount() {
    this.fetchAlertsConfig();
    this.dataTimer = setInterval(this.fetchAlertsConfig.bind(this), 5000);
  }

  async fetchAlertsConfig() {
    let response;
    try {
      response = await getConfig('internal_config_alerts.ini');
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded
        // with a status code that falls out of the range of
        // 2xx
        ToastsStore.error(
          `Error: ${e.response.data.error}`, 5000,
        );
      } else {
        // Something happened in setting up the request that
        // triggered an Error
        ToastsStore.error(`Error: ${e.message}`, 5000);
      }
      return;
    }
    if (response.data.result !== undefined
      && Object.keys(response.data.result).length !== 0) {
      clearInterval(this.dataTimer);
      this.dataTimer = null;
      this.setState({
        alertsConfigJson: response.data.result, isFetchingData: false,
      });
    } else {
      this.setState({ isFetchingData: false });
    }
  }

  enableDisableAlert(section, alert) {
    this.setState((prevState) => {
      const newAlertsConfig = prevState.alertsConfigJson;
      newAlertsConfig[section][alert] = (!toBool(
        newAlertsConfig[section][alert],
      )).toString();
      return { alertsConfigJson: newAlertsConfig };
    });
  }

  render() {
    const { state } = this;
    return (
      <div>
        {
          state.isFetchingData
            ? (
              <div className="div-spinner-style">
                <Spinner
                  animation="border"
                  role="status"
                  className="spinner-style"
                />
              </div>
            )
            : (
              <div>
                { Object.keys(state.alertsConfigJson).length > 0
                  ? (
                    <div>
                      <h1 className="heading-style-1">Alerts Configuration</h1>
                      <AlertsConfigContent
                        alertsConfigJson={state.alertsConfigJson}
                        enableDisableAlert={
                          (section, alert) => this.enableDisableAlert(
                            section, alert,
                          )
                        }
                      />
                      <div className="div-content-centre-style-margin-top">
                        <Button
                          className="button-style2"
                          onClick={async () => {
                            try {
                              ToastsStore.info('Saving config', 5000);
                              await sendConfig(
                                'internal_config_alerts.ini',
                                state.alertsConfigJson,
                              );
                              ToastsStore.success('Config saved', 5000);
                            } catch (e) {
                              if (e.response) {
                                // The request was made and the server responded
                                // with a status code that falls out of the
                                // range of 2xx
                                ToastsStore.error(
                                  `Saving failed. Error: ${
                                    e.response.data.error
                                  }`, 5000,
                                );
                              } else {
                                // Something happened in setting up the request
                                // that triggered an Error
                                ToastsStore.error(
                                  `Saving failed. Error: ${e.message}`, 5000,
                                );
                              }
                            }
                          }
                          }
                        >
                          Save Config
                        </Button>
                      </div>
                    </div>
                  )
                  : <ErrorPage err={INTERNAL_ALERTS_CONFIG_NOT_FOUND} />
                }
              </div>
            )
        }
        <ToastsContainer
          store={ToastsStore}
          position={ToastsContainerPosition.TOP_CENTER}
          lightBackground
        />
      </div>
    );
  }
}

function Preferences() {
  return (
    <Container>
      <AlertsConfig />
    </Container>
  );
}

SectionTable.propTypes = forbidExtraProps({
  alertsEnabled: PropTypes.objectOf(PropTypes.string).isRequired,
  enableDisableAlert: PropTypes.func.isRequired,
  section: PropTypes.string.isRequired,
});

AlertsConfigContent.propTypes = forbidExtraProps({
  alertsConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  enableDisableAlert: PropTypes.func.isRequired,
});

export default Preferences;
