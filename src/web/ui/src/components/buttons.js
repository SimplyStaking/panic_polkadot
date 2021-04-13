import React from 'react';
import Button from 'react-bootstrap/Button';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronRight } from
  '@fortawesome/free-solid-svg-icons/faChevronRight';
import { faChevronLeft } from '@fortawesome/free-solid-svg-icons/faChevronLeft';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { toast } from 'react-toastify';
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
  const onClick = async () => {
    try {
      toast.info('Saving config', { autoClose: 5000 });
      await sendConfig(configName, config);
      toast.success('Config saved', { autoClose: 5000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(
          `Saving failed. Error: ${e.response.data.error}`, { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(`Saving failed. Error: ${e.message}`, { autoClose: 5000 });
      }
    }
  };
  return (
    <div className="div-content-centre-style-margin-top">
      <Button className="button-style2" onClick={onClick}>Save Config</Button>
    </div>
  );
}

function PingNodeButton({ disabled, wsUrl }) {
  const onClick = async () => {
    try {
      toast.info(`Pinging node ${wsUrl}`, { autoClose: 5000 });
      await pingNode(wsUrl);
      toast.success('Ping successful', { autoClose: 5000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(
          `Ping request failed. Error: ${e.response.data.error}`,
          { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(`Ping request failed. Error: ${e.message}`,
          { autoClose: 5000 });
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
      Test via API
    </Button>
  );
}

function PingRepoButton({ disabled, repo }) {
  const onClick = async () => {
    try {
      toast.info(`Connecting with repo ${repo}`, { autoClose: 5000 });
      // Remove last '/' to connect with https://api.github.com/repos/repoPage`.
      await pingRepo(
        `https://api.github.com/repos/${repo.substring(0, repo.length - 1)}`,
      );
      toast.success('Successfully connected', { autoClose: 5000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(
          `Could not connect with repo ${repo}. Error: ${
            e.response.data.message}`, { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(
          `Could not connect with repo ${repo}. Error: ${e.message}`,
          { autoClose: 5000 },
        );
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
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
      <FontAwesomeIcon icon={faTimesCircle} color="red" className="fa-remove" />
    </button>
  );
}

function ConnectWithBotButton({ disabled, botToken }) {
  const onClick = async () => {
    try {
      toast.info(`Connecting with bot ${botToken}`, { autoClose: 5000 });
      await fetchData(`https://api.telegram.org/bot${botToken}/getME`);
      toast.success('Connection successful', { autoClose: 5000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        toast.error(
          `Connection failed. Error: ${e.response.data.description}`,
          { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(`Connection failed. Error: ${e.message}`,
          { autoClose: 5000 });
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
      Connect With Bot
    </Button>
  );
}

function SendTestAlertButton({ disabled, botChatID, botToken }) {
  const onClick = async () => {
    try {
      toast.info(
        'Sending test alert. Make sure to check the chat corresponding '
        + `with chat id ${botChatID}`, { autoClose: 5000 },
      );
      await fetchData(`https://api.telegram.org/bot${botToken}`
        + '/sendMessage', {
        chat_id: botChatID,
        text: '*Test Alert*',
        parse_mode: 'Markdown',
      });
      toast.success('Test alert sent successfully', { autoClose: 5000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(
          `Could not send test alert. Error: ${e.response.data.description}`,
          { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(
          `Could not send test alert. Error: ${e.message}`, { autoClose: 5000 },
        );
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
      Send test alert
    </Button>
  );
}

function PingBotButton({ disabled, botToken, botChatID }) {
  const onClick = async () => {
    try {
      toast.info(`Pinging bot ${botToken}.`, { autoClose: 5000 });
      await fetchData(`https://api.telegram.org/bot${botToken}`
        + '/sendMessage', {
        chat_id: botChatID,
        text: 'PONG!',
        parse_mode: 'Markdown',
      });
      toast.success('Ping request sent. Make sure to check the chat '
        + `corresponding with chat id ${botChatID} for a PONG!`,
      { autoClose: 7000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(`Ping request failed. Error: ${
          e.response.data.description}`, { autoClose: 5000 });
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(`Ping request failed. Error: ${e.message}`,
          { autoClose: 5000 });
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
      Ping bot
    </Button>
  );
}

function SendTestEmailButton({
  disabled, to, smtp, from, user, pass,
}) {
  const onClick = async () => {
    try {
      toast.info(`Sending test e-mail to address ${to}`, { autoClose: 5000 });
      await sendTestEmail(smtp, from, to, user, pass);
      toast.success('Test e-mail sent successfully, check inbox',
        { autoClose: 5000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(`Could not send test e-mail. Error: ${
          e.response.data.error}`, { autoClose: 5000 });
      } else {
        // Something happened in setting up the request that triggered an error
        toast.error(`Could not send test e-mail. Error: ${e.message}`,
          { autoClose: 5000 });
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
      Send test e-mail
    </Button>
  );
}

function TestCallButton({
  disabled, phoneNoToDial, accountSid, authToken, twilioPhoneNo,
}) {
  const onClick = async () => {
    try {
      toast.info(`Calling number ${phoneNoToDial}`, { autoClose: 5000 });
      await testCall(accountSid, authToken, twilioPhoneNo, phoneNoToDial);
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(`Error in calling ${phoneNoToDial}. Error: ${
          e.response.data.error}`, { autoClose: 5000 });
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(
          `Error in calling ${phoneNoToDial}. Error: ${e.message}`,
          { autoClose: 5000 },
        );
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
      Test call
    </Button>
  );
}

function ConnectWithMongoButton({
  disabled, host, port, user, pass,
}) {
  const onClick = async () => {
    try {
      toast.info('Connecting with MongoDB.', { autoClose: 5000 });
      await pingMongoDB(host, port, user, pass);
      toast.success('Connection successful', { autoClose: 5000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(
          `Connection failed. Error: ${e.response.data.error}`,
          { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(`Connection failed. Error: ${e.message}`,
          { autoClose: 5000 });
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
      Connect with MongoDB
    </Button>
  );
}

function ConnectWithRedisButton({
  disabled, host, port, password,
}) {
  const onClick = async () => {
    try {
      toast.info('Connecting with Redis.', { autoClose: 5000 });
      await pingRedis(host, port, password);
      toast.success('Connection successful', { autoClose: 5000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(
          `Connection failed. Error: ${e.response.data.error}`,
          { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an error
        toast.error(`Connection failed. Error: ${e.message}`,
          { autoClose: 5000 });
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
      Connect with Redis
    </Button>
  );
}

function PingApiButton({ disabled, endpoint }) {
  const onClick = async () => {
    try {
      toast.info(`Connecting with API at endpoint ${endpoint}.`,
        { autoClose: 5000 });
      await pingAPIServer(endpoint);
      toast.success('Connection successful', { autoClose: 5000 });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(
          `Connection failed. Error: ${e.response.data.error}`,
          { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(`Connection failed. Error: ${e.message}`,
          { autoClose: 5000 });
      }
    }
  };
  return (
    <Button className="button-style2" disabled={disabled} onClick={onClick}>
      Ping API
    </Button>
  );
}

function LoginButton({
  credentials, setAuthentication, handleSetCredentialsValid, handleSetValidated,
}) {
  const onClick = async () => {
    try {
      toast.info('Authenticating...', { autoClose: 2000 });
      await authenticate(credentials.username, credentials.password);
      handleSetCredentialsValid(true);
      await sleep(2000);
      toast.success('Authentication successful', { autoClose: 2000 });
      setAuthentication(true);
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(
          `Authentication failed. Error: ${e.response.data.error}`,
          { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(`Authentication failed. Error: ${e.message}`,
          { autoClose: 5000 });
      }
      handleSetCredentialsValid(false);
    }
    handleSetValidated(true);
  };
  return (
    <Button className="button-style2" onClick={onClick}>Login</Button>
  );
}

function LogoutButton({ setAuthentication }) {
  const onClick = async () => {
    try {
      toast.info('Logging out ...', { autoClose: 2000 });
      await terminateSession();
      await sleep(2000);
      toast.success('Logged out', { autoClose: 2000 });
      setAuthentication(false);
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        toast.error(
          `Could not log out. Error: ${e.response.data.error}`,
          { autoClose: 5000 },
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        toast.error(`Could not log out. Error: ${e.message}`,
          { autoClose: 5000 });
      }
    }
  };
  return (
    <button className="logout-button-style" onClick={onClick} type="button">
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
