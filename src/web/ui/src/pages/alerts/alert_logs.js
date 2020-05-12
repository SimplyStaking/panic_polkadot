import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Table from 'react-bootstrap/Table';
import Tooltip from 'react-bootstrap/Tooltip';
import Spinner from 'react-bootstrap/Spinner';
import '../../style/style.css';
import moment from 'moment';
import '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronLeft } from '@fortawesome/free-solid-svg-icons/faChevronLeft';
import { faChevronRight } from
  '@fortawesome/free-solid-svg-icons/faChevronRight';
import {
  ToastsContainer,
  ToastsContainerPosition,
  ToastsStore,
} from 'react-toasts';
import Alert from '../../components/alert';
import { getAlerts } from '../../utils/data';

function createCircle(color, radius) {
  return (
    <svg height={21} width={21}>
      <circle cx={10} cy={10} r={radius} fill={color} />
    </svg>
  );
}

function severityColorRepresentation(severity) {
  if (severity === 'CRITICAL') {
    return '#EA4335';
  } if (severity === 'WARNING') {
    return '#FBBC05';
  } if (severity === 'ERROR') {
    return '#b9abc6';
  }
  return '#34A853';
}

function AlertsTableContent({ alerts }) {
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
    const severityColor = severityColorRepresentation(alerts[i].severity);

    content.push(
      <tr key={i}>
        <td className="time-style">{createCircle(severityColor, 10)}</td>
        <OverlayTrigger
          placement="top"
          overlay={(
            <Tooltip id="tooltip-top">
              {moment.unix(alerts[i].timestamp).format('DD-MM-YYYY')}
            </Tooltip>
          )}
        >
          <td className="time-style">
            {moment.unix(alerts[i].timestamp).format('HH:mm:ss')}
          </td>
        </OverlayTrigger>
        <td>{alerts[i].message}</td>
      </tr>,
    );
  }

  return content;
}

function AlertsTable({ alerts }) {
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
        <AlertsTableContent alerts={alerts} />
      </tbody>
    </Table>
  );
}

function NextPageButton({ onClick }) {
  return (
    <Button className="rounded-circle ml-auto button-style" onClick={onClick}>
      <FontAwesomeIcon icon={faChevronRight} color="white" />
    </Button>
  );
}

function PreviousPageButton({ onClick }) {
  return (
    <Button className="rounded-circle mr-auto button-style" onClick={onClick}>
      <FontAwesomeIcon icon={faChevronLeft} color="white" />
    </Button>
  );
}

function AlertsInfo({
  alerts, activePage, onClickPreviousPage, onClickNextPage, totalPages,
}) {
  const navButtons = [];

  // Do not display previous page button if on the first page
  if (activePage !== 1) {
    navButtons.push(
      <PreviousPageButton onClick={onClickPreviousPage} key={1} />,
    );
  }

  // Do not display next page button if we are on the last page or there are no
  // alerts.
  if (activePage !== totalPages && totalPages > 0) {
    navButtons.push(
      <NextPageButton onClick={onClickNextPage} key={2} />,
    );
  }

  return (
    <Container>
      <h1 className="heading-style-1">Live Alerts</h1>
      <AlertsTable alerts={alerts} />
      <Container className="buttons-placement-style">{navButtons}</Container>
    </Container>
  );
}

class AlertLogs extends Component {
  constructor(props) {
    super(props);
    this.noOfAlerts = 50;
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
    // alerts, fetch data of the previous page if it exists. If the number of
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
      response = await getAlerts(this.noOfAlerts, state.activePage);
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (e.response.data.error === 'Mongo not set up') {
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
              <AlertsInfo
                alerts={state.alerts}
                onClickNextPage={() => this.handleNextPage()}
                onClickPreviousPage={() => this.handlePreviousPage()}
                totalPages={state.totalPages}
                activePage={state.activePage}
              />
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

const alertType = PropTypes.shape({
  severity_: PropTypes.string,
  message_: PropTypes.string,
  timestamp_: PropTypes.number,
});

AlertsTable.propTypes = forbidExtraProps({
  alerts: PropTypes.arrayOf(alertType).isRequired,
});

NextPageButton.propTypes = forbidExtraProps({
  onClick: PropTypes.func.isRequired,
});

PreviousPageButton.propTypes = forbidExtraProps({
  onClick: PropTypes.func.isRequired,
});

AlertsInfo.propTypes = forbidExtraProps({
  alerts: PropTypes.arrayOf(alertType).isRequired,
  activePage: PropTypes.number.isRequired,
  onClickPreviousPage: PropTypes.func.isRequired,
  onClickNextPage: PropTypes.func.isRequired,
  totalPages: PropTypes.number.isRequired,
});

export default AlertLogs;
