import React, { Component } from 'react';
import { Form } from 'react-bootstrap';
import Table from 'react-bootstrap/Table';
import Container from 'react-bootstrap/Container';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { toast } from 'react-toastify';
import { capitalizeSentence, toBool } from '../../utils/string';
import { getConfig } from '../../utils/data';
import {
  ALERTS_CONFIG_ALERT_NAMES,
  ALERTS_CONFIG_SECTION_NAMES,
} from '../../utils/constants';
import ErrorPage from '../error';
import { INTERNAL_ALERTS_CONFIG_NOT_FOUND } from '../../utils/error';
import Page from '../../components/page';
import { SaveConfigButton } from '../../components/buttons';
import {
  CollapsibleForm, Trigger,
} from '../../components/forms/collapsible_form';
import '../../style/style.css';

function sectionNameDisplay(str) {
  // If the section is expected, set it to the enum value. Otherwise, remove the
  // underscores, replace them with spaces and capitalize each word.
  if (str in ALERTS_CONFIG_SECTION_NAMES) {
    return ALERTS_CONFIG_SECTION_NAMES[str];
  }
  return str.split('_').map(capitalizeSentence).join(' ');
}

function alertNameDisplay(str) {
  // If the alert is expected, set it to the enum value. Otherwise, remove the
  // underscores and replace them with spaces.
  if (str in ALERTS_CONFIG_ALERT_NAMES) {
    return ALERTS_CONFIG_ALERT_NAMES[str];
  }
  return capitalizeSentence(str.split('_').join(' '));
}

function allAlertsEnabled(alertsEnabled) {
  // Checks if every alert in the section is enabled.
  const result = Object.entries(alertsEnabled).map(
    ([_, enabled]) => toBool(enabled),
  );
  return result.every(alertEnabled => alertEnabled === true);
}

function SectionTableContent({ alertsEnabled, enableDisableAlert, section }) {
  const content = [];
  Object.entries(alertsEnabled).forEach(([alert, enabled]) => {
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
              onChange={() => enableDisableAlert(section, alert)}
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
        <div className="div-style" key={section}>
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
            open
          />
        </div>,
      );
    },
  );

  return <div className="div-style">{forms}</div>;
}

function AlertsConfig({
  alertsConfigJson, enableDisableAlert,
}) {
  return (
    <Container>
      <h1 className="heading-style-1">Alerts Configuration</h1>
      <AlertsConfigContent
        alertsConfigJson={alertsConfigJson}
        enableDisableAlert={enableDisableAlert}
      />
      <SaveConfigButton
        configName="internal_config_alerts.ini"
        config={alertsConfigJson}
      />
    </Container>
  );
}

class Preferences extends Component {
  constructor(props) {
    super(props);
    // We need to set a timer that tries to get data from the alerts config
    // periodically until it is fetched. This must be done since data from the
    // config must be fetched once.
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

  componentWillUnmount() {
    clearInterval(this.dataTimer);
    this.dataTimer = null;
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
        toast.error(
          `Error: ${e.response.data.error}`, { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that
        // triggered an Error
        toast.error(`Error: ${e.message}`, { autoClose: 5000 });
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
      <Page
        spinnerCondition={state.isFetchingData}
        component={(
          <div>
            { Object.keys(state.alertsConfigJson).length > 0
              ? (
                <AlertsConfig
                  alertsConfigJson={state.alertsConfigJson}
                  enableDisableAlert={
                    (section, alert) => this.enableDisableAlert(section, alert)
                  }
                />
              )
              : <ErrorPage err={INTERNAL_ALERTS_CONFIG_NOT_FOUND} />
            }
          </div>
        )}
      />
    );
  }
}

AlertsConfig.propTypes = forbidExtraProps({
  enableDisableAlert: PropTypes.func.isRequired,
  alertsConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
});

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
