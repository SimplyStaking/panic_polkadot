import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import { ToastsStore } from 'react-toasts';
import Page from '../../components/page';
import { getConfig, sendConfig } from '../../utils/data';
import {
  checkConfigAndFix, fieldEmpty, fixUserConfigMain,
} from '../../utils/configs';
import { seperatorValuesNonEmpty, toBool } from '../../utils/string';
import { mainUserConfig } from '../../utils/templates';
import GeneralForm from '../../components/forms/general_forms';
import { TelegramCommandsForm, TelegramAlertsForm } from
  '../../components/forms/telegram_forms';
import EmailAlertsForm from '../../components/forms/email_forms';
import TwilioAlertsForm from '../../components/forms/twilio_forms';
import MongoForm from '../../components/forms/mongo_forms';
import PARForm from '../../components/forms/par_forms';
import APIServerForm from '../../components/forms/api_server_forms';
import RedisForm from '../../components/forms/redis_forms';
import '../../style/style.css';

function MainUserConfig({
  mainUserConfigJson, validated, alerterIdentifierValid,
  telegramAlertsBotTokenValid, telegramAlertsChatIdValid,
  SMTPServerAddressValid, fromAddressValid, toAddressesValid,
  emailAlertsFormValid, accountSIDValid, accountAuthTokenValid,
  twilioPhoneNumberValid, twilioPhoneNumbersToDialValid, twilioAlertsFormValid,
  mongoHostValid, mongoPortValid, mongoDBNameValid, PARIntervalSecValid,
  telegramCommandsBotTokenValid, telegramCommandsChatIdValid, redisHostValid,
  redisPortValid, redisFormValid, polkadotAPIEndpointValid, APIFormValid,
  mongoFormValid, handleChangeInNonBooleanField, handleChangeInBooleanField,
}) {
  return (
    <div>
      <h1 className="heading-style-1">Main User Configuration</h1>
      <GeneralForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
        alerterIdentifierValid={alerterIdentifierValid}
      />
      <TelegramAlertsForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        telegramAlertsBotTokenValid={telegramAlertsBotTokenValid}
        telegramAlertsChatIdValid={telegramAlertsChatIdValid}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
        handleChangeInBooleanField={handleChangeInBooleanField}
      />
      <EmailAlertsForm
        validated={validated}
        mainUserConfigJson={mainUserConfigJson}
        SMTPServerAddressValid={SMTPServerAddressValid}
        fromAddressValid={fromAddressValid}
        toAddressesValid={toAddressesValid}
        emailAlertsFormValid={emailAlertsFormValid}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
        handleChangeInBooleanField={handleChangeInBooleanField}
      />
      <TwilioAlertsForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        accountSIDValid={accountSIDValid}
        accountAuthTokenValid={accountAuthTokenValid}
        twilioPhoneNumberValid={twilioPhoneNumberValid}
        twilioPhoneNumbersToDialValid={twilioPhoneNumbersToDialValid}
        twilioAlertsFormValid={twilioAlertsFormValid}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
        handleChangeInBooleanField={handleChangeInBooleanField}
      />
      <MongoForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        mongoHostValid={mongoHostValid}
        mongoPortValid={mongoPortValid}
        mongoDBNameValid={mongoDBNameValid}
        mongoFormValid={mongoFormValid}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
        handleChangeInBooleanField={handleChangeInBooleanField}
      />
      <PARForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        PARIntervalSecValid={PARIntervalSecValid}
        handleChangeInBooleanField={handleChangeInBooleanField}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
      />
      <TelegramCommandsForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        telegramCommandsBotTokenValid={telegramCommandsBotTokenValid}
        telegramCommandsChatIdValid={telegramCommandsChatIdValid}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
        handleChangeInBooleanField={handleChangeInBooleanField}
      />
      <RedisForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        redisHostValid={redisHostValid}
        redisPortValid={redisPortValid}
        redisFormValid={redisFormValid}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
        handleChangeInBooleanField={handleChangeInBooleanField}
      />
      <APIServerForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        polkadotAPIEndpointValid={polkadotAPIEndpointValid}
        APIFormValid={APIFormValid}
        handleChangeInNonBooleanField={handleChangeInNonBooleanField}
      />
    </div>
  );
}

class MainSettingsPage extends Component {
  constructor(props) {
    super(props);
    // We need to set a timer that tries to get the data periodically until the
    // data is fetched. This must be done since data from the config must be
    // fetched once.
    this.dataTimer = null;
    this.state = {
      mainUserConfigJson: Object.create(mainUserConfig,
        Object.getOwnPropertyDescriptors(mainUserConfig)),
      isFetchingData: true,
      validated: false,
    };
  }

  componentDidMount() {
    this.fetchMainUserConfig();
    this.dataTimer = setInterval(this.fetchMainUserConfig.bind(this), 5000);
  }

  componentWillUnmount() {
    clearInterval(this.dataTimer);
    this.dataTimer = null;
  }

  async fetchMainUserConfig() {
    let response;
    try {
      response = await getConfig('user_config_main.ini');
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
    clearInterval(this.dataTimer);
    this.dataTimer = null;
    if (response.data.result !== undefined
      && Object.keys(response.data.result).length !== 0) {
      const checkedConfig = checkConfigAndFix(
        response.data.result, mainUserConfig,
      );
      this.setState({
        mainUserConfigJson: checkedConfig, isFetchingData: false,
      });
    } else {
      this.setState({ isFetchingData: false });
    }
  }

  alerterIdentifierValid() {
    const { state } = this;
    return !fieldEmpty(
      state.mainUserConfigJson.general.unique_alerter_identifier,
    );
  }

  generalFormValid() {
    return this.alerterIdentifierValid();
  }

  telegramAlertsBotTokenValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.telegram_alerts.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.telegram_alerts.bot_token);
  }

  telegramAlertsChatIdValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.telegram_alerts.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.telegram_alerts.bot_chat_id);
  }

  telegramAlertsFormValid() {
    return this.telegramAlertsBotTokenValid()
      && this.telegramAlertsChatIdValid();
  }

  SMTPServerAddressValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.email_alerts.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.email_alerts.smtp);
  }

  fromAddressValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.email_alerts.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.email_alerts.from);
  }

  // The addresses are valid if the field is not empty, seperated by ';' and
  // each address is non-empty (for multiple addresses only).
  toAddressesValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.email_alerts.enabled)) {
      return true;
    }
    return !fieldEmpty(
      state.mainUserConfigJson.email_alerts.to,
    ) && new RegExp('^[^\\s]+([;][^\\s]+)*$').test(
      state.mainUserConfigJson.email_alerts.to,
    ) && seperatorValuesNonEmpty(state.mainUserConfigJson.email_alerts.to, ';');
  }

  emailAlertsFormValid() {
    return this.SMTPServerAddressValid() && this.fromAddressValid()
      && this.toAddressesValid();
  }

  accountSIDValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.twilio_alerts.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.twilio_alerts.account_sid);
  }

  accountAuthTokenValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.twilio_alerts.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.twilio_alerts.auth_token);
  }

  twilioPhoneNumberValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.twilio_alerts.enabled)) {
      return true;
    }
    return !fieldEmpty(
      state.mainUserConfigJson.twilio_alerts.twilio_phone_number,
    ) && new RegExp('^[+][0-9]+$')
      .test(state.mainUserConfigJson.twilio_alerts.twilio_phone_number);
  }

  // Twilio phone numbers are valid if they start with +, and for multiple
  // inputs they are separated with ;.
  twilioPhoneNumbersToDialValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.twilio_alerts.enabled)) {
      return true;
    }
    return !fieldEmpty(
      state.mainUserConfigJson.twilio_alerts.phone_numbers_to_dial,
    ) && new RegExp('^[+][0-9]+([;][+][0-9]+)*$').test(
      state.mainUserConfigJson.twilio_alerts.phone_numbers_to_dial,
    );
  }

  twilioAlertsFormValid() {
    return this.accountSIDValid() && this.accountAuthTokenValid()
      && this.twilioPhoneNumberValid() && this.twilioPhoneNumbersToDialValid();
  }

  mongoHostValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.mongo.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.mongo.host);
  }

  // A port is valid only if it is a number
  mongoPortValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.mongo.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.mongo.port)
      && new RegExp('^([0-9]+)*$').test(state.mainUserConfigJson.mongo.port);
  }

  // The database name is valid only if it does not contain spaces
  mongoDBNameValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.mongo.enabled)) {
      return true;
    }
    return new RegExp('^[^ ]+$').test(state.mainUserConfigJson.mongo.db_name);
  }

  mongoFormValid() {
    return this.mongoHostValid() && this.mongoPortValid()
      && this.mongoDBNameValid();
  }

  // The interval seconds are valid only if they are numbers
  PARIntervalSecValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.periodic_alive_reminder.enabled)) {
      return true;
    }
    return !fieldEmpty(
      state.mainUserConfigJson.periodic_alive_reminder.interval_seconds,
    ) && new RegExp('^([0-9]+)*$').test(
      state.mainUserConfigJson.periodic_alive_reminder.interval_seconds,
    );
  }

  PARFormValid() {
    return this.PARIntervalSecValid();
  }

  telegramCommandsBotTokenValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.telegram_commands.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.telegram_commands.bot_token);
  }

  telegramCommandsChatIdValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.telegram_commands.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.telegram_commands.bot_chat_id);
  }

  telegramCommandsFormValid() {
    return this.telegramCommandsBotTokenValid()
      && this.telegramCommandsChatIdValid();
  }

  redisHostValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.redis.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.redis.host);
  }

  // A port is valid only if it is a number
  redisPortValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.redis.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.redis.port)
      && new RegExp('^([0-9]+)*$').test(state.mainUserConfigJson.redis.port);
  }

  redisFormValid() {
    return this.redisHostValid() && this.redisPortValid();
  }

  polkadotAPIEndpointValid() {
    const { state } = this;
    return !fieldEmpty(state.mainUserConfigJson.api.polkadot_api_endpoint);
  }

  APIFormValid() {
    return this.polkadotAPIEndpointValid();
  }

  mainUserConfigValid() {
    return this.generalFormValid() && this.telegramAlertsFormValid()
      && this.emailAlertsFormValid() && this.twilioAlertsFormValid()
      && this.mongoFormValid() && this.PARFormValid()
      && this.telegramCommandsFormValid() && this.redisFormValid()
      && this.APIFormValid();
  }

  handleChangeInNonBooleanField(event, form, field) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.mainUserConfigJson;
      newConfig[form][field] = event.target.value;
      return { mainUserConfigJson: newConfig };
    });
  }

  handleChangeInBooleanField(event, form, field) {
    this.setState((prevState) => {
      const newConfig = prevState.mainUserConfigJson;
      newConfig[form][field] = (!toBool(
        prevState.mainUserConfigJson[form][field],
      )).toString();
      return { mainUserConfigJson: newConfig };
    });
  }

  render() {
    const { state } = this;
    return (
      <Page
        spinnerCondition={state.isFetchingData}
        component={(
          <Container>
            <MainUserConfig
              mainUserConfigJson={state.mainUserConfigJson}
              validated={state.validated}
              alerterIdentifierValid={() => this.alerterIdentifierValid()}
              SMTPServerAddressValid={() => this.SMTPServerAddressValid()}
              telegramAlertsBotTokenValid={
                () => this.telegramAlertsBotTokenValid()
              }
              telegramAlertsChatIdValid={
                () => this.telegramAlertsChatIdValid()
              }
              fromAddressValid={() => this.fromAddressValid()}
              toAddressesValid={() => this.toAddressesValid()}
              emailAlertsFormValid={() => this.emailAlertsFormValid()}
              twilioAlertsFormValid={() => this.twilioAlertsFormValid()}
              accountAuthTokenValid={() => this.accountAuthTokenValid()}
              twilioPhoneNumberValid={() => this.twilioPhoneNumberValid()}
              twilioPhoneNumbersToDialValid={
                () => this.twilioPhoneNumbersToDialValid()
              }
              mongoHostValid={() => this.mongoHostValid()}
              mongoPortValid={() => this.mongoPortValid()}
              mongoDBNameValid={() => this.mongoDBNameValid()}
              PARIntervalSecValid={() => this.PARIntervalSecValid()}
              telegramCommandsChatIdValid={
                () => this.telegramCommandsChatIdValid()
              }
              redisHostValid={() => this.redisHostValid()}
              redisPortValid={() => this.redisPortValid()}
              redisFormValid={() => this.redisFormValid()}
              polkadotAPIEndpointValid={
                () => this.polkadotAPIEndpointValid()
              }
              APIFormValid={() => this.APIFormValid()}
              mongoFormValid={() => this.mongoFormValid()}
              accountSIDValid={() => this.accountSIDValid()}
              telegramCommandsBotTokenValid={
                () => this.telegramCommandsBotTokenValid()
              }
              handleChangeInNonBooleanField={
                (event, form, field) => {
                  this.handleChangeInNonBooleanField(event, form, field);
                }
              }
              handleChangeInBooleanField={
                (event, form, field) => {
                  this.handleChangeInBooleanField(event, form, field);
                }
              }
            />
            <div className="div-content-centre-style-margin-top">
              <Button
                className="button-style2"
                onClick={(event) => {
                  event.preventDefault();
                  if (!this.mainUserConfigValid()) {
                    this.setState({ validated: true });
                    event.stopPropagation();
                    return;
                  }
                  ToastsStore.info('Saving config', 5000);
                  const newMainConfig = fixUserConfigMain(
                    state.mainUserConfigJson,
                  );
                  this.setState({
                    mainUserConfigJson: newMainConfig,
                  },
                  async () => {
                    try {
                      await sendConfig(
                        'user_config_main.ini', state.mainUserConfigJson,
                      );
                      this.setState({ validated: false });
                      ToastsStore.success('Config saved', 5000);
                    } catch (e) {
                      if (e.response) {
                        // The request was made and the server responded
                        // with a status code that falls out of the
                        // range of 2xx
                        ToastsStore.error(
                          `Saving failed. Error: ${e.response.data.error}`,
                          5000,
                        );
                      } else {
                        // Something happened in setting up the request
                        // that triggered an Error
                        ToastsStore.error(
                          `Saving failed. Error: ${e.message}`, 5000,
                        );
                      }
                    }
                  });
                }
                }
              >
                Save Config
              </Button>
            </div>
          </Container>
        )}
      />
    );
  }
}

MainUserConfig.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  alerterIdentifierValid: PropTypes.func.isRequired,
  telegramAlertsBotTokenValid: PropTypes.func.isRequired,
  telegramAlertsChatIdValid: PropTypes.func.isRequired,
  SMTPServerAddressValid: PropTypes.func.isRequired,
  fromAddressValid: PropTypes.func.isRequired,
  toAddressesValid: PropTypes.func.isRequired,
  emailAlertsFormValid: PropTypes.func.isRequired,
  accountSIDValid: PropTypes.func.isRequired,
  accountAuthTokenValid: PropTypes.func.isRequired,
  twilioPhoneNumberValid: PropTypes.func.isRequired,
  twilioPhoneNumbersToDialValid: PropTypes.func.isRequired,
  twilioAlertsFormValid: PropTypes.func.isRequired,
  mongoHostValid: PropTypes.func.isRequired,
  mongoPortValid: PropTypes.func.isRequired,
  mongoDBNameValid: PropTypes.func.isRequired,
  PARIntervalSecValid: PropTypes.func.isRequired,
  telegramCommandsBotTokenValid: PropTypes.func.isRequired,
  telegramCommandsChatIdValid: PropTypes.func.isRequired,
  redisHostValid: PropTypes.func.isRequired,
  redisPortValid: PropTypes.func.isRequired,
  redisFormValid: PropTypes.func.isRequired,
  polkadotAPIEndpointValid: PropTypes.func.isRequired,
  APIFormValid: PropTypes.func.isRequired,
  mongoFormValid: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
});

export default MainSettingsPage;
