import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import Container from 'react-bootstrap/Container';
import Table from 'react-bootstrap/Table';
import moment from 'moment';
import '@fortawesome/fontawesome-svg-core';
import { ToastsStore } from 'react-toasts';
import Alert from '../../components/alert';
import { getAlerts } from '../../utils/data';
import { MONGO_NOT_SET_UP } from '../../utils/error';
import Page from '../../components/page';
import {
  ALERT_TYPE,
  SEVERITY_COLOUR_REPRESENTATION,
} from '../../utils/constants';
import { ChevronButton } from '../../components/buttons';
import TooltipOverlay from '../../components/overlays';
import '../../style/style.css';

function SeverityCircle({
  svgHeight, svgWidth, circleCentreX, circleCentreY, color, radius,
}) {
  return (
    <svg height={svgHeight} width={svgWidth}>
      <circle cx={circleCentreX} cy={circleCentreY} r={radius} fill={color} />
    </svg>
  );
}

function LiveAlertsTableContent({ alerts }) {
  const content = [];
  let currentDate = null;

  if (alerts.length === 0) {
    content.push(
      <tr key="no-content-key">
        <td colSpan="3" className="date-style">
          No alerts yet! Make sure that PANIC and MongoDB are set-up and
          running.
        </td>
      </tr>,
    );
    return content;
  }
  for (let i = 0; i < alerts.length; i += 1) {
    // Works only if alerts are ordered by date in recent-first way.
    if (currentDate
            !== (moment.unix(alerts[i].timestamp).format('Do MMMM YYYY'))
    ) {
      currentDate = (moment.unix(alerts[i].timestamp)).format('Do MMMM YYYY');
      content.push(
        <tr key={`date${i}`}>
          <td colSpan="3" className="date-style">{currentDate}</td>
        </tr>,
      );
    }

    const severityColor = SEVERITY_COLOUR_REPRESENTATION[alerts[i].severity];
    content.push(
      <tr key={i}>
        <td className="time-style">
          <SeverityCircle
            svgHeight={21}
            svgWidth={21}
            circleCentreX={10}
            circleCentreY={10}
            color={severityColor}
            radius={10}
          />
        </td>
        <TooltipOverlay
          identifier="tooltip-top"
          placement="top"
          tooltipText={moment.unix(alerts[i].timestamp).format('DD-MM-YYYY')}
          component={(
            <td className="time-style">
              {moment.unix(alerts[i].timestamp).format('HH:mm:ss')}
            </td>
          )}
        />
        <td>{alerts[i].message}</td>
      </tr>,
    );
  }

  return content;
}

function LiveAlertsTable({ alerts }) {
  return (
    <Table responsive size="sm" className="tables-style">
      <thead>
        <tr>
          <th className="column-style">{}</th>
          <th className="column-style">Time</th>
          <th>Message</th>
        </tr>
      </thead>
      <tbody>
        <LiveAlertsTableContent alerts={alerts} />
      </tbody>
    </Table>
  );
}

function LiveAlerts({
  alerts, activePage, onClickPreviousPage, onClickNextPage, totalPages,
}) {
  const navButtons = [];
  // Do not display previous page button if on the first page
  if (activePage !== 1) {
    navButtons.push(
      <ChevronButton
        className="rounded-circle mr-auto button-style"
        onClick={onClickPreviousPage}
        chevronColour="white"
        direction="left"
        key={1}
      />,
    );
  }
  // Do not display the next page button if we are on the last page or there not
  // enough pages.
  if (activePage !== totalPages && totalPages > 0) {
    navButtons.push(
      <ChevronButton
        className="rounded-circle ml-auto button-style"
        onClick={onClickNextPage}
        chevronColour="white"
        direction="right"
        key={2}
      />,
    );
  }
  return (
    <Container>
      <h1 className="heading-style-1">Live Alerts</h1>
      <LiveAlertsTable alerts={alerts} />
      <Container className="buttons-placement-style">{navButtons}</Container>
    </Container>
  );
}

class AlertLogs extends Component {
  constructor(props) {
    super(props);
    this.alertsPerPage = 50;
    this.dataTimer = null;
    this.state = {
      alerts: [],
      totalPages: 1,
      // By default the active page is the first
      activePage: 1,
      // So that the spinner is displayed when the component is mounted
      isFetchingData: true,
    };
  }

  componentDidMount() {
    this.fetchAlerts();
    this.dataTimer = setInterval(this.fetchAlerts.bind(this), 5000);
  }

  componentDidUpdate(_prevProps, _prevState, _snapshot) {
    // If the user deletes elements from the database and a page no longer has
    // alerts, fetch data of the last page that exists. If the number of
    // alerts went to zero, do nothing.
    const { state } = this;
    if (state.activePage > state.totalPages && state.totalPages > 0) {
      this.handleTotalPagesDecrease(state.totalPages);
    }
  }

  componentWillUnmount() {
    clearInterval(this.dataTimer);
    this.dataTimer = null;
  }

  handleTotalPagesDecrease(totalPages) {
    this.setState({ activePage: totalPages, isFetchingData: true },
      () => this.fetchAlerts());
  }

  async fetchAlerts() {
    // isFetchingData was not set to true here to avoid displaying the spinner
    // when the data is already present.
    const { state } = this;
    const alerts = [];
    let response;
    try {
      response = await getAlerts(this.alertsPerPage, state.activePage);
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (e.response.data.error === MONGO_NOT_SET_UP.message) {
          // If MongoDB not set up reset everything to default.
          this.setState({ alerts, totalPages: 1, isFetchingData: false });
        }
        ToastsStore.error(`Error: ${e.response.data.error}`, 5000);
      } else {
        // Something happened in setting up the request that triggered an Error
        ToastsStore.error(`Error: ${e.message}`, 5000);
      }
      return;
    }
    const alertsJson = response.data.result.alerts;
    // To prevent having page zero
    const totalPages = response.data.result.total_pages === 0
      ? 1 : response.data.result.total_pages;
    alertsJson.forEach((alertJson) => {
      // Expect timestamp from Mongo in UTC.
      alerts.push(new Alert(alertJson.severity, alertJson.message,
        parseFloat(alertJson.timestamp)));
    });

    this.setState({ alerts, totalPages, isFetchingData: false });
  }

  handleNextPage() {
    this.setState((prevState) => {
      const nextPage = prevState.activePage + 1;
      return {
        activePage: nextPage,
        isFetchingData: true,
      };
    }, async () => { await this.fetchAlerts(); });
  }

  handlePreviousPage() {
    this.setState((prevState) => {
      const nextPage = prevState.activePage - 1;
      return {
        activePage: nextPage,
        isFetchingData: true,
      };
    }, async () => { await this.fetchAlerts(); });
  }

  render() {
    const { state } = this;
    return (
      <Page
        spinnerCondition={state.isFetchingData}
        component={(
          <LiveAlerts
            alerts={state.alerts}
            onClickNextPage={() => this.handleNextPage()}
            onClickPreviousPage={() => this.handlePreviousPage()}
            totalPages={state.totalPages}
            activePage={state.activePage}
          />
        )}
      />
    );
  }
}

SeverityCircle.propTypes = forbidExtraProps({
  svgHeight: PropTypes.number.isRequired,
  svgWidth: PropTypes.number.isRequired,
  circleCentreX: PropTypes.number.isRequired,
  circleCentreY: PropTypes.number.isRequired,
  color: PropTypes.string.isRequired,
  radius: PropTypes.number.isRequired,
});

LiveAlertsTable.propTypes = forbidExtraProps({
  alerts: PropTypes.arrayOf(ALERT_TYPE).isRequired,
});

LiveAlerts.propTypes = forbidExtraProps({
  alerts: PropTypes.arrayOf(ALERT_TYPE).isRequired,
  activePage: PropTypes.number.isRequired,
  onClickPreviousPage: PropTypes.func.isRequired,
  onClickNextPage: PropTypes.func.isRequired,
  totalPages: PropTypes.number.isRequired,
});

export default AlertLogs;
