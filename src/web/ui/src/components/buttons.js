import React from 'react';
import Button from 'react-bootstrap/Button';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronRight } from
  '@fortawesome/free-solid-svg-icons/faChevronRight';
import { faChevronLeft } from '@fortawesome/free-solid-svg-icons/faChevronLeft';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { ToastsStore } from 'react-toasts';
import { faTimesCircle } from '@fortawesome/free-solid-svg-icons/faTimesCircle';
import {
  authenticate, fetchData, pingAPIServer, pingMongoDB, pingNode, pingRedis,
  pingRepo, sendConfig, sendTestEmail, terminateSession, testCall,
} from '../utils/data';
import sleep from '../utils/time';
import '../style/style.css';

function ChevronButton({
  className, onClick, chevronColour, direction,
}) {
  return (
    <Button className={className} onClick={onClick}>
      <FontAwesomeIcon
        icon={direction === 'left' ? faChevronLeft : faChevronRight}
        color={chevronColour}
      />
    </Button>
  );
}

function SaveConfigButton({ configName, config }) {
  return (
    <div className="div-content-centre-style-margin-top">
      <Button
        className="button-style2"
        onClick={async () => {
          try {
            ToastsStore.info('Saving config', 5000);
            await sendConfig(configName, config);
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
  );
}

function PingNodeButton({ disabled, wsUrl }) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info(`Pinging node ${wsUrl}`, 5000);
          await pingNode(wsUrl);
          ToastsStore.success('Ping successful', 5000);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded
            // with a status code that falls out of the
            // range of 2xx
            ToastsStore.error(
              `Ping request failed. Error: ${e.response.data.error}`,
              5000,
            );
          } else {
            // Something happened in setting up the request
            // that triggered an Error
            ToastsStore.error(`Ping request failed. Error: ${e.message}`, 5000);
          }
        }
      }
      }
    >
      Test via API
    </Button>
  );
}

function PingRepoButton({ disabled, repo }) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info(`Connecting with repo ${repo}`, 5000);
          // Remove last '/' to connect with
          // https://api.github.com/repos/repoPage`.
          await pingRepo(
            `https://api.github.com/repos/${
              repo.substring(0, repo.length - 1)
            }`,
          );
          ToastsStore.success('Successfully connected', 5000);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Could not connect with repo ${repo}. Error: ${
                e.response.data.message}`, 5000,
            );
          } else {
            // Something happened in setting up the request
            // that triggered an Error
            ToastsStore.error(
              `Could not connect with repo ${repo}. Error: ${e.message}`, 5000,
            );
          }
        }
      }
      }
    >
      Connect with repo
    </Button>
  );
}

function RemoveButton({ handleRemove, itemKey }) {
  return (
    <button
      className="delete-button-style"
      onClick={() => handleRemove(itemKey)}
      type="button"
    >
      <FontAwesomeIcon
        icon={faTimesCircle}
        color="red"
        className="fa-remove"
      />
    </button>
  );
}

function ConnectWithBotButton({ disabled, botToken }) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info(`Connecting with bot ${botToken}`, 5000);
          await fetchData(`https://api.telegram.org/bot${botToken}/getME`);
          ToastsStore.success('Connection successful', 5000);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Connection failed. Error: ${e.response.data.description}`, 5000,
            );
          } else {
            // Something happened in setting up the request that triggered an
            // Error
            ToastsStore.error(`Connection failed. Error: ${e.message}`, 5000);
          }
        }
      }
      }
    >
      Connect With Bot
    </Button>
  );
}

function SendTestAlertButton({ disabled, botChatID, botToken }) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info(
            'Sending test alert. Make sure to check the chat corresponding '
            + `with chat id ${botChatID}`, 5000,
          );
          await fetchData(
            `https://api.telegram.org/bot${botToken}`
            + '/sendMessage', {
              chat_id: botChatID,
              text: '*Test Alert*',
              parse_mode: 'Markdown',
            },
          );
          ToastsStore.success('Test alert sent successfully', 5000);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded
            // with a status code that falls out of the
            // range of 2xx
            ToastsStore.error(
              `Could not send test alert. 
               Error: ${e.response.data.description}`, 5000,
            );
          } else {
            // Something happened in setting up the request
            // that triggered an Error
            ToastsStore.error(
              `Could not send test alert. Error: ${e.message}`, 5000,
            );
          }
        }
      }
      }
    >
      Send test alert
    </Button>
  );
}

function PingBotButton({ disabled, botToken, botChatID }) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info(`Pinging bot ${botToken}.`, 5000);
          await fetchData(
            `https://api.telegram.org/bot${botToken}`
            + '/sendMessage', {
              chat_id: botChatID,
              text: 'PONG!',
              parse_mode: 'Markdown',
            },
          );
          ToastsStore.success(
            'Ping request sent. Make sure to check the chat '
            + `corresponding with chat id ${botChatID} for a PONG!`, 7000,
          );
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Ping request failed. Error: ${e.response.data.description}`,
              5000,
            );
          } else {
            // Something happened in setting up the request
            // that triggered an Error
            ToastsStore.error(`Ping request failed. Error: ${e.message}`, 5000);
          }
        }
      }
      }
    >
      Ping bot
    </Button>
  );
}

function SendTestEmailButton({
  disabled, to, smtp, from, user, pass,
}) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info(`Sending test e-mail to address ${to}`, 5000);
          await sendTestEmail(smtp, from, to, user, pass);
          ToastsStore.success(
            'Test e-mail sent successfully, check inbox', 5000,
          );
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Could not send test e-mail. Error: ${e.response.data.error}`,
              5000,
            );
          } else {
            // Something happened in setting up the request that triggered an
            // error
            ToastsStore.error(
              `Could not send test e-mail. Error: ${e.message}`, 5000,
            );
          }
        }
      }
      }
    >
      Send test e-mail
    </Button>
  );
}

function TestCallButton({
  disabled, phoneNoToDial, accountSid, authToken, twilioPhoneNo,
}) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info(`Calling number ${phoneNoToDial}`, 5000);
          await testCall(accountSid, authToken, twilioPhoneNo, phoneNoToDial);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Error in calling ${phoneNoToDial}. Error: ${
                e.response.data.error
              }`, 5000,
            );
          } else {
            // Something happened in setting up the request that triggered an
            // Error
            ToastsStore.error(
              `Error in calling ${phoneNoToDial}. Error: ${e.message}`, 5000,
            );
          }
        }
      }
      }
    >
      Test call
    </Button>
  );
}

function ConnectWithMongoButton({
  disabled, host, port, user, pass,
}) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info('Connecting with MongoDB.', 5000);
          await pingMongoDB(host, port, user, pass);
          ToastsStore.success('Connection successful', 5000);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Connection failed. Error: ${e.response.data.error}`,
              5000,
            );
          } else {
            // Something happened in setting up the request that triggered an
            // Error
            ToastsStore.error(`Connection failed. Error: ${e.message}`, 5000);
          }
        }
      }
      }
    >
      Connect with MongoDB
    </Button>
  );
}

function ConnectWithRedisButton({
  disabled, host, port, password,
}) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info('Connecting with Redis.', 5000);
          await pingRedis(host, port, password);
          ToastsStore.success('Connection successful', 5000);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Connection failed. Error: ${e.response.data.error}`, 5000,
            );
          } else {
            // Something happened in setting up the request that triggered an
            // error
            ToastsStore.error(
              `Connection failed. Error: ${e.message}`, 5000,
            );
          }
        }
      }
      }
    >
      Connect with Redis
    </Button>
  );
}

function PingApiButton({ disabled, endpoint }) {
  return (
    <Button
      className="button-style2"
      disabled={disabled}
      onClick={async () => {
        try {
          ToastsStore.info(`Connecting with API at endpoint ${
            endpoint}.`, 5000);
          await pingAPIServer(endpoint);
          ToastsStore.success('Connection successful', 5000);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Connection failed. Error: ${e.response.data.error}`, 5000,
            );
          } else {
            // Something happened in setting up the request that triggered an
            // Error
            ToastsStore.error(`Connection failed. Error: ${e.message}`, 5000);
          }
        }
      }
      }
    >
      Ping API
    </Button>
  );
}

function LoginButton({
  credentials, setAuthentication, handleSetCredentialsValid, handleSetValidated,
}) {
  return (
    <Button
      className="button-style2"
      onClick={async () => {
        try {
          ToastsStore.info('Authenticating...', 2000);
          await authenticate(credentials.username, credentials.password);
          handleSetCredentialsValid(true);
          await sleep(2000);
          ToastsStore.success('Authentication successful', 2000);
          setAuthentication(true);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Authentication failed. Error: ${e.response.data.error}`, 5000,
            );
          } else {
            // Something happened in setting up the request that triggered an
            // Error
            ToastsStore.error(`Authentication failed. Error: ${
              e.message}`, 5000);
          }
          handleSetCredentialsValid(false);
        }
        handleSetValidated(true);
      }
      }
    >
      Login
    </Button>
  );
}

function LogoutButton({ setAuthentication }) {
  return (
    <button
      className="logout-button-style"
      onClick={async () => {
        try {
          ToastsStore.info('Logging out ...', 2000);
          await terminateSession();
          await sleep(2000);
          ToastsStore.success('Logged out', 2000);
          setAuthentication(false);
        } catch (e) {
          if (e.response) {
            // The request was made and the server responded with a status code
            // that falls out of the range of 2xx
            ToastsStore.error(
              `Could not log out. Error: ${e.response.data.error}`, 5000,
            );
          } else {
            // Something happened in setting up the request that triggered an
            // Error
            ToastsStore.error(`Could not log out. Error: ${
              e.message}`, 5000);
          }
        }
      }
      }
      type="button"
    >
      Logout
    </button>
  );
}

ChevronButton.propTypes = forbidExtraProps({
  className: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  chevronColour: PropTypes.string.isRequired,
  direction: PropTypes.string.isRequired,
});

SaveConfigButton.propTypes = forbidExtraProps({
  configName: PropTypes.string.isRequired,
  config: PropTypes.objectOf(PropTypes.object).isRequired,
});

PingNodeButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  wsUrl: PropTypes.string.isRequired,
});

PingRepoButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  repo: PropTypes.string.isRequired,
});

ConnectWithBotButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  botToken: PropTypes.string.isRequired,
});

SendTestAlertButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  botToken: PropTypes.string.isRequired,
  botChatID: PropTypes.string.isRequired,
});

SendTestEmailButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  to: PropTypes.string.isRequired,
  smtp: PropTypes.string.isRequired,
  from: PropTypes.string.isRequired,
  user: PropTypes.string.isRequired,
  pass: PropTypes.string.isRequired,
});

TestCallButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  phoneNoToDial: PropTypes.string.isRequired,
  accountSid: PropTypes.string.isRequired,
  authToken: PropTypes.string.isRequired,
  twilioPhoneNo: PropTypes.string.isRequired,
});

PingBotButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  botToken: PropTypes.string.isRequired,
  botChatID: PropTypes.string.isRequired,
});

ConnectWithMongoButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  host: PropTypes.string.isRequired,
  port: PropTypes.string.isRequired,
  user: PropTypes.string.isRequired,
  pass: PropTypes.string.isRequired,
});

ConnectWithRedisButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  host: PropTypes.string.isRequired,
  port: PropTypes.string.isRequired,
  password: PropTypes.string.isRequired,
});

PingApiButton.propTypes = forbidExtraProps({
  disabled: PropTypes.bool.isRequired,
  endpoint: PropTypes.string.isRequired,
});

RemoveButton.propTypes = forbidExtraProps({
  handleRemove: PropTypes.func.isRequired,
  itemKey: PropTypes.number.isRequired,
});

LoginButton.propTypes = forbidExtraProps({
  credentials: PropTypes.shape({
    username: PropTypes.string,
    password: PropTypes.string,
  }).isRequired,
  setAuthentication: PropTypes.func.isRequired,
  handleSetCredentialsValid: PropTypes.func.isRequired,
  handleSetValidated: PropTypes.func.isRequired,
});

LogoutButton.propTypes = forbidExtraProps({
  setAuthentication: PropTypes.func.isRequired,
});

export {
  ChevronButton, SaveConfigButton, PingNodeButton, RemoveButton, PingRepoButton,
  ConnectWithBotButton, SendTestAlertButton, PingBotButton, SendTestEmailButton,
  TestCallButton, ConnectWithMongoButton, PingApiButton, ConnectWithRedisButton,
  LoginButton, LogoutButton,
};
