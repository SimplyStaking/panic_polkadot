import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
import Collapsible from 'react-collapsible';
import Spinner from 'react-bootstrap/Spinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck } from '@fortawesome/free-solid-svg-icons/faCheck';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import {
  ToastsContainer,
  ToastsContainerPosition,
  ToastsStore,
} from 'react-toasts';
import '../../style/style.css';
import {
  fetchData,
  pingMongoDB,
  pingRedis,
  pingAPIServer,
  sendTestEmail,
  testCall,
  getConfig,
  sendConfig,
} from '../../utils/data';
import {
  checkConfigAndFix,
  clearSectionData,
  fieldEmpty,
} from '../../utils/configs';
import { seperatorValuesNonEmpty, toBool } from '../../utils/string';
import { mainUserConfig } from '../../utils/templates';

// sm represents the total number of columns to take
function createFormLabel(column, sm, label) {
  return <Form.Label column={column} sm={sm}>{label}</Form.Label>;
}

function createColumnWithContent(sm, content, key) {
  return <Col sm={sm} key={key}>{content}</Col>;
}

function createColumnForm(labels, columns) {
  const form = [];

  for (let i = 0; i < labels.length; i += 1) {
    form.push(
      <Form.Group as={Row} key={i}>
        {labels[i]}
        {columns[i]}
      </Form.Group>,
    );
  }
  return <Form onSubmit={(e) => { e.preventDefault(); }}>{form}</Form>;
}

function CollapsibleForm({
  trigger, triggerClassName, triggerOpenedClassName, triggerDisabled, open,
  content,
}) {
  return (
    <div className="div-style">
      <Collapsible
        trigger={trigger}
        triggerClassName={triggerClassName}
        triggerOpenedClassName={triggerOpenedClassName}
        triggerDisabled={triggerDisabled}
        open={open}
      >
        {content}
      </Collapsible>
    </div>
  );
}

function GeneralForm({
  mainUserConfigJson, validated, handleChangeInAlerterIdentifier,
  alerterIdentifierValid,
}) {
  const labels = [createFormLabel(true, '3', 'Alerter identifier')];
  const columns = [
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            onChange={event => handleChangeInAlerterIdentifier(event)}
            placeholder="PANIC Alerter"
            value={mainUserConfigJson.general.unique_alerter_identifier}
            isInvalid={validated && !alerterIdentifierValid()}
            isValid={validated && alerterIdentifierValid()}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Alerter identifier cannot be empty!
          </Form.Control.Feedback>
          <Form.Text className="text-muted">
            Must be unique if you are running multiple instances of PANIC.
          </Form.Text>
        </div>,
        1,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="stash-overlay"
            placement="right"
            overlay={(
              <Tooltip id="stash-tooltip">
                Please make sure that uniqueness is observed since this setup
                cannot detect other PANIC configurations.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        2,
      ),
    ],
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={<Trigger name="General" />}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        content={createColumnForm(labels, columns)}
        open
      />
    </div>
  );
}

function Trigger({
  name, checkEnabled,
}) {
  return (
    <div className="ml-auto">
      <div className="trigger-div-style">
        {name}
        {checkEnabled && (
          <FontAwesomeIcon
            icon={faCheck}
            color="green"
            className="fa-xs enabled-style"
          />
        )}
      </div>
    </div>
  );
}

function TelegramAlertsForm({
  mainUserConfigJson, validated, handleEnableTelegramAlerts,
  handleChangeInAlertsBotToken, telegramAlertsBotTokenValid,
  telegramAlertsChatIdValid, handleChangeInAlertsChatId,
}) {
  const labels = [
    createFormLabel(true, '3', 'Enabled'),
    createFormLabel(true, '3', 'Bot token'),
    createFormLabel(true, '3', 'Bot chat ID'),
  ];
  const columns = [
    createColumnWithContent(
      '1',
      <div>
        <Form.Check
          type="checkbox"
          id="telegram-alerts-enabled-check-box"
          aria-label="checkbox"
          className="checkbox-style"
          onChange={() => handleEnableTelegramAlerts()}
          checked={toBool(mainUserConfigJson.telegram_alerts.enabled)}
        />
      </div>,
      1,
    ),
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="123456789:ABCDEF-1234abcd5678efgh12345_abc123"
            disabled={!toBool(mainUserConfigJson.telegram_alerts.enabled)}
            onChange={event => handleChangeInAlertsBotToken(event)}
            value={mainUserConfigJson.telegram_alerts.bot_token}
            isInvalid={validated && !telegramAlertsBotTokenValid()
            && toBool(mainUserConfigJson.telegram_alerts.enabled)}
            isValid={validated && telegramAlertsBotTokenValid()
             && toBool(mainUserConfigJson.telegram_alerts.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Bot token cannot be empty!
          </Form.Control.Feedback>
        </div>,
        2,
      ),
      createColumnWithContent(
        '4',
        <div>
          <Button
            className="button-style2"
            disabled={!toBool(mainUserConfigJson.telegram_alerts.enabled)
            || !telegramAlertsBotTokenValid()}
            onClick={async () => {
              try {
                ToastsStore.info(
                  `Connecting with bot ${
                    mainUserConfigJson.telegram_alerts.bot_token
                  }`, 5000,
                );
                await fetchData(
                  `https://api.telegram.org/bot${
                    mainUserConfigJson.telegram_alerts.bot_token
                  }/getME`,
                );
                ToastsStore.success('Connection successful', 5000);
              } catch (e) {
                if (e.response) {
                  // The request was made and the server responded
                  // with a status code that falls out of the
                  // range of 2xx
                  ToastsStore.error(
                    `Connection failed. Error: ${e.response.data.description}`,
                    5000,
                  );
                } else {
                  // Something happened in setting up the request
                  // that triggered an Error
                  ToastsStore.error(
                    `Connection failed. Error: ${e.message}`, 5000,
                  );
                }
              }
            }
            }
          >
            Connect With Bot
          </Button>
        </div>,
        3,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="123456789"
            disabled={!toBool(mainUserConfigJson.telegram_alerts.enabled)}
            onChange={event => handleChangeInAlertsChatId(event)}
            value={mainUserConfigJson.telegram_alerts.bot_chat_id}
            isInvalid={validated && !telegramAlertsChatIdValid()
            && toBool(mainUserConfigJson.telegram_alerts.enabled)}
            isValid={validated && telegramAlertsChatIdValid()
            && toBool(mainUserConfigJson.telegram_alerts.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Bot chat ID cannot be empty!
          </Form.Control.Feedback>
        </div>,
        4,
      ),
      createColumnWithContent(
        '4',
        <div>
          <Button
            className="button-style2"
            disabled={!toBool(mainUserConfigJson.telegram_alerts.enabled)
            || !telegramAlertsChatIdValid()}
            onClick={async () => {
              try {
                ToastsStore.info(
                  `Sending test alert. Make sure to check the chat corresponding
                  with chat id ${
                    mainUserConfigJson.telegram_alerts.bot_chat_id
                  }`, 5000,
                );
                await fetchData(
                  `https://api.telegram.org/bot${
                    mainUserConfigJson.telegram_alerts.bot_token
                  }`
                  + '/sendMessage', {
                    chat_id: mainUserConfigJson.telegram_alerts.bot_chat_id,
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
        </div>,
        5,
      ),
    ],
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(
          <Trigger
            name="Telegram Alerts"
            checkEnabled={toBool(mainUserConfigJson.telegram_alerts.enabled)}
          />
        )}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              Alerts sent via Telegram are a fast and reliable means of alerting
              that we highly recommend enabling. This requires you to have a
              Telegram bot set up, which is a free and quick procedure.
            </Form.Text>
            {createColumnForm(labels, columns)}
          </div>
        )}
        open
      />
    </div>
  );
}

function EmailAlertsForm({
  handleEnableEmailAlerts, mainUserConfigJson, SMTPServerAddressValid,
  handleChangeInSMTPServerAddress, validated, handleChangeInFromAddress,
  fromAddressValid, handleChangeInToAddresses, toAddressesValid,
  handleUsernameChange, handleEmailAlertsPasswordChange, emailAlertsFormValid,
}) {
  const labels = [
    createFormLabel(true, '3', 'Enabled'),
    createFormLabel(true, '3', 'SMTP server address'),
    createFormLabel(true, '3', 'From'),
    createFormLabel(true, '3', 'To'),
    createFormLabel(true, '3', 'Username'),
    createFormLabel(true, '3', 'Password'),
  ];
  const columns = [
    createColumnWithContent(
      '1',
      <div>
        <Form.Check
          type="checkbox"
          id="email-alerts-enabled-check-box"
          aria-label="checkbox"
          className="checkbox-style"
          onChange={() => handleEnableEmailAlerts()}
          checked={toBool(mainUserConfigJson.email_alerts.enabled)}
        />
      </div>,
      1,
    ),
    createColumnWithContent(
      '5',
      <div>
        <Form.Control
          type="text"
          placeholder="my.smtp.com"
          disabled={!toBool(mainUserConfigJson.email_alerts.enabled)}
          onChange={event => handleChangeInSMTPServerAddress(event)}
          value={mainUserConfigJson.email_alerts.smtp}
          isInvalid={validated && !SMTPServerAddressValid()
          && toBool(mainUserConfigJson.email_alerts.enabled)}
          isValid={validated && SMTPServerAddressValid()
          && toBool(mainUserConfigJson.email_alerts.enabled)}
        />
        <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
        <Form.Control.Feedback type="invalid">
          SMTP server address cannot be empty!
        </Form.Control.Feedback>
      </div>,
      2,
    ),
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="alerter@email.com"
            disabled={!toBool(mainUserConfigJson.email_alerts.enabled)}
            onChange={event => handleChangeInFromAddress(event)}
            value={mainUserConfigJson.email_alerts.from}
            isInvalid={validated && !fromAddressValid()
            && toBool(mainUserConfigJson.email_alerts.enabled)}
            isValid={validated && fromAddressValid()
            && toBool(mainUserConfigJson.email_alerts.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            From address cannot be empty!
          </Form.Control.Feedback>
        </div>,
        3,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="email-alerts-sender-overlay"
            placement="right"
            overlay={(
              <Tooltip id="email-alerts-sender-tooltip">
                Specify the details of the sender
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        4,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="user@email.com"
            disabled={!toBool(mainUserConfigJson.email_alerts.enabled)}
            onChange={event => handleChangeInToAddresses(event)}
            value={mainUserConfigJson.email_alerts.to}
            isInvalid={validated && !toAddressesValid()
            && toBool(mainUserConfigJson.email_alerts.enabled)}
            isValid={validated && toAddressesValid()
            && toBool(mainUserConfigJson.email_alerts.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(mainUserConfigJson.email_alerts.to)
            ? (
              <Form.Control.Feedback type="invalid">
                To e-mail addresses cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                To e-mail addresses are not in the required format.
              </Form.Control.Feedback>
            )}
          <Form.Text className="text-muted">
            Separate addresses with semi-colons and no spaces if you wish to
            enter multiple addresses.
          </Form.Text>
        </div>,
        5,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="email-alerts-to-overlay"
            placement="right"
            overlay={(
              <Tooltip id="email-alerts-to-tooltip">
                Specify the e-mail addresses where you want to receive alerts.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        6,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="my_username"
            disabled={!toBool(mainUserConfigJson.email_alerts.enabled)}
            onChange={event => handleUsernameChange(event)}
            value={mainUserConfigJson.email_alerts.user}
            isValid={validated
            && toBool(mainUserConfigJson.email_alerts.enabled)
            }
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
        </div>,
        7,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="email-alerts-username-overlay"
            placement="right"
            overlay={(
              <Tooltip id="email-alerts-username-tooltip">
                Username for SMTP authentication. Leave blank for no
                authentication.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        8,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="password"
            placeholder="HMASDNoiSADnuiasdgnAIO876hg967bv99vb8buyT8BVuyT76VBT"
            disabled={(!toBool(mainUserConfigJson.email_alerts.enabled))
            || (fieldEmpty(mainUserConfigJson.email_alerts.user))}
            onChange={event => handleEmailAlertsPasswordChange(event)}
            value={mainUserConfigJson.email_alerts.pass}
            isValid={validated
            && toBool(mainUserConfigJson.email_alerts.enabled)
            && !(fieldEmpty(mainUserConfigJson.email_alerts.user))}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
        </div>,
        9,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="email-alerts-password-overlay"
            placement="right"
            overlay={(
              <Tooltip id="email-alerts-password-tooltip">
                Password for SMTP authentication.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        10,
      ),
    ],
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(
          <Trigger
            name="Email Alerts"
            checkEnabled={toBool(mainUserConfigJson.email_alerts.enabled)}
          />
        )}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              Email alerts are more useful as a backup alerting channel rather
              than the main one, given that one is much more likely to notice a
              message on Telegram or a phone call. Email alerts also require an
              SMTP server to be set up for the alerter to be able to send.
            </Form.Text>
            {createColumnForm(labels, columns)}
            <div className="div-content-centre-style">
              <Button
                className="button-style2"
                disabled={!toBool(mainUserConfigJson.email_alerts.enabled)
                || !emailAlertsFormValid()}
                onClick={async () => {
                  try {
                    ToastsStore.info(
                      `Sending test e-mail to address ${
                        mainUserConfigJson.email_alerts.to.split(';')[0]
                      }`, 5000,
                    );
                    await sendTestEmail(
                      mainUserConfigJson.email_alerts.smtp,
                      mainUserConfigJson.email_alerts.from,
                      mainUserConfigJson.email_alerts.to.split(';')[0],
                      mainUserConfigJson.email_alerts.user,
                      mainUserConfigJson.email_alerts.pass,
                    );
                    ToastsStore.success(
                      'Test e-mail sent successfully, check inbox', 5000,
                    );
                  } catch (e) {
                    if (e.response) {
                      // The request was made and the server responded
                      // with a status code that falls out of the
                      // range of 2xx
                      ToastsStore.error(
                        `Could not send test e-mail. Error: ${
                          e.response.data.error
                        }`, 5000,
                      );
                    } else {
                      // Something happened in setting up the request
                      // that triggered an Error
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
            </div>
          </div>
        )}
      />
    </div>
  );
}

function TwilioAlertsForm({
  mainUserConfigJson, validated, handleEnableTwilioAlerts, accountSIDValid,
  handleChangeInTwilioAccountSID, handleChangeInTwilioAccountAuthToken,
  accountAuthTokenValid, twilioPhoneNumberValid,
  handleChangeInTwilioPhoneNumber, twilioPhoneNumbersToDialValid,
  handleChangeInTwilioPhoneNumbersToDial, twilioAlertsFormValid,
}) {
  const labels = [
    createFormLabel(true, '3', 'Enabled'),
    createFormLabel(true, '3', 'Account SID'),
    createFormLabel(true, '3', 'Account AuthToken'),
    createFormLabel(true, '3', 'Twilio phone number'),
    createFormLabel(true, '3', 'Phone numbers to dial'),
  ];
  const columns = [
    createColumnWithContent(
      '1',
      <div>
        <Form.Check
          type="checkbox"
          id="twilio-alerts-enabled-check-box"
          aria-label="checkbox"
          className="checkbox-style"
          onChange={() => handleEnableTwilioAlerts()}
          checked={toBool(mainUserConfigJson.twilio_alerts.enabled)}
        />
      </div>,
      1,
    ),
    createColumnWithContent(
      '5',
      <div>
        <Form.Control
          type="text"
          placeholder="abcd1234efgh5678ABCD1234EFGH567890"
          disabled={!toBool(mainUserConfigJson.twilio_alerts.enabled)}
          onChange={event => handleChangeInTwilioAccountSID(event)}
          value={mainUserConfigJson.twilio_alerts.account_sid}
          isInvalid={validated && !accountSIDValid()
          && toBool(mainUserConfigJson.twilio_alerts.enabled)}
          isValid={validated && accountSIDValid()
          && toBool(mainUserConfigJson.twilio_alerts.enabled)}
        />
        <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
        <Form.Control.Feedback type="invalid">
          Account SID cannot be empty!
        </Form.Control.Feedback>
      </div>,
      2,
    ),
    createColumnWithContent(
      '5',
      <div>
        <Form.Control
          type="text"
          placeholder="1234abcd5678efgh1234abcd5678efgh"
          disabled={!toBool(mainUserConfigJson.twilio_alerts.enabled)}
          onChange={event => handleChangeInTwilioAccountAuthToken(event)}
          value={mainUserConfigJson.twilio_alerts.auth_token}
          isInvalid={validated && !accountAuthTokenValid()
          && toBool(mainUserConfigJson.twilio_alerts.enabled)}
          isValid={validated && accountAuthTokenValid()
          && toBool(mainUserConfigJson.twilio_alerts.enabled)}
        />
        <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
        <Form.Control.Feedback type="invalid">
          Account AuthToken cannot be empty!
        </Form.Control.Feedback>
      </div>,
      3,
    ),
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="+12025551234"
            disabled={!toBool(mainUserConfigJson.twilio_alerts.enabled)}
            onChange={event => handleChangeInTwilioPhoneNumber(event)}
            value={mainUserConfigJson.twilio_alerts.twilio_phone_number}
            isInvalid={validated && !twilioPhoneNumberValid()
            && toBool(mainUserConfigJson.twilio_alerts.enabled)}
            isValid={validated && twilioPhoneNumberValid()
            && toBool(mainUserConfigJson.twilio_alerts.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(mainUserConfigJson.twilio_alerts.twilio_phone_number)
            ? (
              <Form.Control.Feedback type="invalid">
                Twilio phone number cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                Twilio phone number is not in the required format.
              </Form.Control.Feedback>
            )}
          <Form.Text className="text-muted">Format: +12025551234</Form.Text>
        </div>,
        4,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="twilio-alerts-phone-no-overlay"
            placement="right"
            overlay={(
              <Tooltip id="twilio-alerts-phone-no-tooltip">
                Your registered Twilio phone number
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        5,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="+12025551235,+12025551236,+12025551237"
            disabled={!toBool(mainUserConfigJson.twilio_alerts.enabled)}
            onChange={event => handleChangeInTwilioPhoneNumbersToDial(event)}
            value={mainUserConfigJson.twilio_alerts.phone_numbers_to_dial}
            isInvalid={validated && !twilioPhoneNumbersToDialValid()
            && toBool(mainUserConfigJson.twilio_alerts.enabled)}
            isValid={validated && twilioPhoneNumbersToDialValid()
            && toBool(mainUserConfigJson.twilio_alerts.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(mainUserConfigJson.twilio_alerts.phone_numbers_to_dial)
            ? (
              <Form.Control.Feedback type="invalid">
                Phone numbers to dial cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                Phone numbers to dial are not in the required format.
              </Form.Control.Feedback>
            )}
          <Form.Text className="text-muted">
            Format: +12025551234. Separate phone numbers with semi-colons and no
            spaces if you wish to enter multiple numbers.
          </Form.Text>
        </div>,
        6,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="twilio-alerts-to-dial-no-overlay"
            placement="right"
            overlay={(
              <Tooltip id="twilio-alerts-to-dial-no-tooltip">
                Phone numbers to receive alerts
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        7,
      ),
    ],
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(
          <Trigger
            name="Twilio Alerts"
            checkEnabled={toBool(mainUserConfigJson.twilio_alerts.enabled)}
          />
        )}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              Twilio phone-call alerts are the most important alerts since they
              are the best at grabbing your attention, especially when
              you&apos;re asleep! To set these up, you have to have a Twilio
              account set up, with a registered Twilio phone number and a
              verified phone number. The timed trial version of Twilio is free.
            </Form.Text>
            {createColumnForm(labels, columns)}
            <div className="div-content-centre-style">
              <Button
                className="button-style2"
                disabled={!toBool(mainUserConfigJson.twilio_alerts.enabled)
                || !twilioAlertsFormValid()}
                onClick={async () => {
                  try {
                    ToastsStore.info(
                      `Calling number ${
                        mainUserConfigJson.twilio_alerts.phone_numbers_to_dial
                          .split(';')[0]}`, 5000,
                    );
                    await testCall(
                      mainUserConfigJson.twilio_alerts.account_sid,
                      mainUserConfigJson.twilio_alerts.auth_token,
                      mainUserConfigJson.twilio_alerts.twilio_phone_number,
                      mainUserConfigJson.twilio_alerts.phone_numbers_to_dial
                        .split(';')[0],
                    );
                  } catch (e) {
                    if (e.response) {
                      // The request was made and the server responded
                      // with a status code that falls out of the
                      // range of 2xx
                      ToastsStore.error(
                        `Error in calling ${
                          mainUserConfigJson.twilio_alerts.phone_numbers_to_dial
                            .split(';')[0]}. Error: ${
                          e.response.data.error
                        }`, 5000,
                      );
                    } else {
                      // Something happened in setting up the request
                      // that triggered an Error
                      ToastsStore.error(
                        `Error in calling ${
                          mainUserConfigJson.twilio_alerts.phone_numbers_to_dial
                            .split(';')[0]}. Error: ${e.message}`, 5000,
                      );
                    }
                  }
                }
                }
              >
                Test call
              </Button>
            </div>
          </div>
        )}
      />
    </div>
  );
}

function MongoForm({
  mainUserConfigJson, validated, handleEnableMongoAlerts, mongoHostValid,
  handleChangeInMongoHost, handleChangeInMongoPort, mongoPortValid,
  handleChangeInMongoDBName, mongoDBNameValid, handleChangeInMongoUser,
  handleMongoPassChange, mongoFormValid,
}) {
  const labels = [
    createFormLabel(true, '3', 'Enabled'),
    createFormLabel(true, '3', 'Host IP'),
    createFormLabel(true, '3', 'Host port'),
    createFormLabel(true, '3', 'Database name'),
    createFormLabel(true, '3', 'Username'),
    createFormLabel(true, '3', 'Password'),
  ];
  const columns = [
    createColumnWithContent(
      '1',
      <div>
        <Form.Check
          type="checkbox"
          id="mongo-enabled-check-box"
          aria-label="checkbox"
          className="checkbox-style"
          onChange={() => handleEnableMongoAlerts()}
          checked={toBool(mainUserConfigJson.mongo.enabled)}
        />
      </div>,
      1,
    ),
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="localhost"
            disabled={!toBool(mainUserConfigJson.mongo.enabled)}
            onChange={event => handleChangeInMongoHost(event)}
            value={mainUserConfigJson.mongo.host}
            isInvalid={validated && !mongoHostValid()
            && toBool(mainUserConfigJson.mongo.enabled)}
            isValid={validated && mongoHostValid()
            && toBool(mainUserConfigJson.mongo.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Host IP cannot be empty!
          </Form.Control.Feedback>
        </div>,
        2,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="mongo-host-ip-overlay"
            placement="right"
            overlay={(
              <Tooltip id="mongo-host-ip-tooltip">
                The IP of the Mongo server. If you will be running PANIC using
                Docker, do not use localhost, instead use the full IP address
                (local or external) of the machine that the Mongo container will
                be running on.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        3,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="27017"
            disabled={!toBool(mainUserConfigJson.mongo.enabled)}
            onChange={event => handleChangeInMongoPort(event)}
            value={mainUserConfigJson.mongo.port}
            isInvalid={validated && !mongoPortValid()
            && toBool(mainUserConfigJson.mongo.enabled)}
            isValid={validated && mongoPortValid()
            && toBool(mainUserConfigJson.mongo.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(mainUserConfigJson.mongo.port)
            ? (
              <Form.Control.Feedback type="invalid">
                Port field cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                Port is not a number.
              </Form.Control.Feedback>
            )}
        </div>,
        4,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="mongo-host-port-overlay"
            placement="right"
            overlay={(
              <Tooltip id="mongo-host-port-tooltip">
                The port of the Mongo server. If you will be running PANIC
                using Docker, you should leave the port as 27017. If you wish to
                run the Mongo container on another port, please input this port
                number here and change the &apos;MONGO_HOST_PORT&apos; value
                inside the &apos;panic_polkadot/.env&apos; file
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        5,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="panic"
            disabled={!toBool(mainUserConfigJson.mongo.enabled)}
            onChange={event => handleChangeInMongoDBName(event)}
            value={mainUserConfigJson.mongo.db_name}
            isInvalid={validated && !mongoDBNameValid()
            && toBool(mainUserConfigJson.mongo.enabled)}
            isValid={validated && mongoDBNameValid()
            && toBool(mainUserConfigJson.mongo.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(mainUserConfigJson.mongo.db_name)
            ? (
              <Form.Control.Feedback type="invalid">
                Database name field cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                Database name cannot contain spaces.
              </Form.Control.Feedback>
            )}
          <Form.Text className="text-muted">
            Database name cannot contain spaces.
          </Form.Text>
        </div>,
        6,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="mongo-database-name-overlay"
            placement="right"
            overlay={(
              <Tooltip id="mongo-database-name-tooltip">
                The database you wish to use to store the alerts. This will be
                auto-created if it does not exist. You can re-use the same
                database if another PANIC is installed.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        7,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            palceholder="username"
            disabled={!toBool(mainUserConfigJson.mongo.enabled)}
            onChange={event => handleChangeInMongoUser(event)}
            value={mainUserConfigJson.mongo.user}
            isValid={validated && toBool(mainUserConfigJson.mongo.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
        </div>,
        8,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="mongo-username-overlay"
            placement="right"
            overlay={(
              <Tooltip id="mongo-username-tooltip">
                Username for authentication. Leave blank for no authentication.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        9,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="password"
            placeholder="aKoJ8hHa897gZGiuHiugOIGoiuygOIu
            ugO879gtLnPGkjhgOgiuo76uyi"
            disabled={
              (!toBool(mainUserConfigJson.mongo.enabled))
              || (fieldEmpty(mainUserConfigJson.mongo.user))
            }
            onChange={event => handleMongoPassChange(event)}
            value={mainUserConfigJson.mongo.pass}
            isValid={validated && toBool(mainUserConfigJson.mongo.enabled)
            && !(fieldEmpty(mainUserConfigJson.mongo.user))}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
        </div>,
        10,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="mongo-password-overlay"
            placement="right"
            overlay={(
              <Tooltip id="mongo-password-tooltip">
                Password for authentication.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        11,
      ),
    ],
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(
          <Trigger
            name="Mongo"
            checkEnabled={toBool(mainUserConfigJson.mongo.enabled)}
          />
        )}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              Mongo can be set up to persist any alert in a MongoDB collection.
            </Form.Text>
            {createColumnForm(labels, columns)}
            <div className="div-content-centre-style">
              <Button
                className="button-style2"
                disabled={!toBool(mainUserConfigJson.mongo.enabled)
                || !mongoFormValid()}
                onClick={async () => {
                  try {
                    ToastsStore.info('Connecting with MongoDB.', 5000);
                    await pingMongoDB(mainUserConfigJson.mongo.host,
                      mainUserConfigJson.mongo.port,
                      mainUserConfigJson.mongo.user,
                      mainUserConfigJson.mongo.pass);
                    ToastsStore.success('Connection successful', 5000);
                  } catch (e) {
                    if (e.response) {
                      // The request was made and the server responded
                      // with a status code that falls out of the
                      // range of 2xx
                      ToastsStore.error(
                        `Connection failed. Error: ${e.response.data.error}`,
                        5000,
                      );
                    } else {
                      // Something happened in setting up the request
                      // that triggered an Error
                      ToastsStore.error(
                        `Connection failed. Error: ${e.message}`, 5000,
                      );
                    }
                  }
                }
                }
              >
                Connect with MongoDB
              </Button>
            </div>
          </div>
        )}
      />
    </div>
  );
}

function PeriodicAliveReminderForm({
  mainUserConfigJson, validated, handleEnablePAR, PARIntervalSecValid,
  handleChangeInPARIntervalSec, handleEnablePAREmailAlerts,
  handleEnablePARTelegramAlerts, handleEnablePARMongoAlerts,
}) {
  const labels = [
    createFormLabel(true, '3', 'Enabled'),
    createFormLabel(true, '3', 'Interval Seconds'),
    createFormLabel(true, '3', 'Email alerts'),
    createFormLabel(true, '3', 'Telegram alerts'),
    createFormLabel(true, '3', 'Mongo alerts'),
  ];
  const columns = [
    createColumnWithContent(
      '1',
      <div>
        <Form.Check
          type="checkbox"
          id="par-enabled-check-box"
          aria-label="checkbox"
          className="checkbox-style"
          onChange={() => handleEnablePAR()}
          checked={toBool(mainUserConfigJson.periodic_alive_reminder.enabled)}
        />
      </div>,
      1,
    ),
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="3600"
            disabled={
              !toBool(mainUserConfigJson.periodic_alive_reminder.enabled)
            }
            onChange={event => handleChangeInPARIntervalSec(event)}
            value={mainUserConfigJson.periodic_alive_reminder.interval_seconds}
            isInvalid={validated && !PARIntervalSecValid()
            && toBool(mainUserConfigJson.periodic_alive_reminder.enabled)}
            isValid={validated && PARIntervalSecValid()
            && toBool(mainUserConfigJson.periodic_alive_reminder.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(
            mainUserConfigJson.periodic_alive_reminder.interval_seconds,
          )
            ? (
              <Form.Control.Feedback type="invalid">
                The interval seconds field cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                Input is not a positive integer.
              </Form.Control.Feedback>
            )}
        </div>,
        2,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="par-interval-overlay"
            placement="right"
            overlay={(
              <Tooltip id="par-interval-tooltip">
                The number of seconds to pass before sending an alive reminder
                alert.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        3,
      ),
    ],
    createColumnWithContent(
      '2',
      <div>
        <div style={{ display: 'inline-block' }}>
          <Form.Check
            type="checkbox"
            id="par-email-enabled-check-box"
            aria-label="checkbox"
            className="checkbox-style"
            onChange={() => handleEnablePAREmailAlerts()}
            checked={
              toBool(mainUserConfigJson.periodic_alive_reminder.email_enabled)
            }
            disabled={
              !toBool(mainUserConfigJson.periodic_alive_reminder.enabled)
            || !toBool(mainUserConfigJson.email_alerts.enabled)
            }
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <OverlayTrigger
            key="par-email-enabled-overlay"
            placement="right"
            overlay={(
              <Tooltip id="par-email-enabled-tooltip">
                Tick box if you wish to receive reminder alerts via e-mail. Only
                applicable if e-mail alerts are enabled.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>
      </div>,
      4,
    ),
    createColumnWithContent(
      '2',
      <div>
        <div style={{ display: 'inline-block' }}>
          <Form.Check
            type="checkbox"
            id="par-telegram-enabled-check-box"
            aria-label="checkbox"
            className="checkbox-style"
            onChange={() => handleEnablePARTelegramAlerts()}
            checked={toBool(
              mainUserConfigJson.periodic_alive_reminder.telegram_enabled,
            )}
            disabled={
              !toBool(mainUserConfigJson.periodic_alive_reminder.enabled)
            || !toBool(mainUserConfigJson.telegram_alerts.enabled)}
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <OverlayTrigger
            key="par-telegram-enabled-overlay"
            placement="right"
            overlay={(
              <Tooltip id="par-telegram-enabled-tooltip">
                Tick box if you wish to receive reminder alerts via Telegram.
                Only applicable if Telegram alerts are enabled.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>
      </div>,
      5,
    ),
    createColumnWithContent(
      '2',
      <div>
        <div style={{ display: 'inline-block' }}>
          <Form.Check
            type="checkbox"
            id="par-mongo-enabled-check-box"
            aria-label="checkbox"
            className="checkbox-style"
            disabled={
              !toBool(mainUserConfigJson.periodic_alive_reminder.enabled)
            || !toBool(mainUserConfigJson.mongo.enabled)}
            onChange={() => handleEnablePARMongoAlerts()}
            checked={
              toBool(mainUserConfigJson.periodic_alive_reminder.mongo_enabled)
            }
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <OverlayTrigger
            key="par-mongo-enabled-overlay"
            placement="right"
            overlay={(
              <Tooltip id="par-mongo-enabled-tooltip">
                Tick box if you wish to save reminder alerts in a Mongo
                database. Only applicable if Mongo was set up.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>
      </div>,
      6,
    ),
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(
          <Trigger
            name="Periodic Alive Reminder"
            checkEnabled={
              toBool(mainUserConfigJson.periodic_alive_reminder.enabled)
            }
          />
        )}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              The periodic alive reminder is a way for the alerter to inform its
              users that it is still running.
            </Form.Text>
            {createColumnForm(labels, columns)}
          </div>
        )}
      />
    </div>
  );
}

function TelegramCommandsForm({
  mainUserConfigJson, validated, handleEnableTelegramCommands,
  handleChangeInCommandsBotToken, telegramCommandsBotTokenValid,
  telegramCommandsChatIdValid, handleChangeInCommandsChatId,
}) {
  const labels = [
    createFormLabel(true, '3', 'Enabled'),
    createFormLabel(true, '3', 'Bot token'),
    createFormLabel(true, '3', 'Bot chat ID'),
  ];
  const columns = [
    createColumnWithContent(
      '1',
      <div>
        <Form.Check
          type="checkbox"
          id="telegram-commands-enabled-check-box"
          aria-label="checkbox"
          className="checkbox-style"
          onChange={() => handleEnableTelegramCommands()}
          checked={toBool(mainUserConfigJson.telegram_commands.enabled)}
        />
      </div>,
      1,
    ),
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="123456789:ABCDEF-1234abcd5678efgh12345_abc123"
            disabled={!toBool(mainUserConfigJson.telegram_commands.enabled)}
            onChange={event => handleChangeInCommandsBotToken(event)}
            value={mainUserConfigJson.telegram_commands.bot_token}
            isInvalid={validated && !telegramCommandsBotTokenValid()
            && toBool(mainUserConfigJson.telegram_commands.enabled)}
            isValid={validated && telegramCommandsBotTokenValid()
            && toBool(mainUserConfigJson.telegram_commands.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Bot token cannot be empty!
          </Form.Control.Feedback>
        </div>,
        2,
      ),
      createColumnWithContent(
        '4',
        <div>
          <Button
            className="button-style2"
            disabled={!toBool(mainUserConfigJson.telegram_commands.enabled)
            || !telegramCommandsBotTokenValid()}
            onClick={async () => {
              try {
                ToastsStore.info(
                  `Connecting with bot ${
                    mainUserConfigJson.telegram_commands.bot_token
                  }`, 5000,
                );
                await fetchData(
                  `https://api.telegram.org/bot${
                    mainUserConfigJson.telegram_commands.bot_token
                  }/getME`,
                );
                ToastsStore.success('Connection successful', 5000);
              } catch (e) {
                if (e.response) {
                  // The request was made and the server responded
                  // with a status code that falls out of the
                  // range of 2xx
                  ToastsStore.error(
                    `Connection failed. Error: ${e.response.data.description}`,
                    5000,
                  );
                } else {
                  // Something happened in setting up the request
                  // that triggered an Error
                  ToastsStore.error(
                    `Connection failed. Error: ${e.message}`, 5000,
                  );
                }
              }
            }
            }
          >
            Connect With Bot
          </Button>
        </div>,
        3,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="123456789"
            disabled={!toBool(mainUserConfigJson.telegram_commands.enabled)}
            onChange={event => handleChangeInCommandsChatId(event)}
            value={mainUserConfigJson.telegram_commands.bot_chat_id}
            isInvalid={validated && !telegramCommandsChatIdValid()
            && toBool(mainUserConfigJson.telegram_commands.enabled)}
            isValid={validated && telegramCommandsChatIdValid()
            && toBool(mainUserConfigJson.telegram_commands.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Bot chat ID cannot be empty!
          </Form.Control.Feedback>
        </div>,
        4,
      ),
      createColumnWithContent(
        '4',
        <div>
          <Button
            className="button-style2"
            disabled={!toBool(mainUserConfigJson.telegram_commands.enabled)
            || !telegramCommandsChatIdValid()}
            onClick={async () => {
              try {
                ToastsStore.info(
                  `Pinging bot ${
                    mainUserConfigJson.telegram_commands.bot_token}.`, 5000,
                );
                await fetchData(
                  `https://api.telegram.org/bot${
                    mainUserConfigJson.telegram_commands.bot_token}`
                  + '/sendMessage', {
                    chat_id: mainUserConfigJson.telegram_commands.bot_chat_id,
                    text: 'PONG!',
                    parse_mode: 'Markdown',
                  },
                );
                ToastsStore.success(
                  'Ping request sent. Make sure to check the chat '
                  + `corresponding with chat id ${
                    mainUserConfigJson.telegram_commands.bot_chat_id}`
                  + ' for a PONG!', 7000,
                );
              } catch (e) {
                if (e.response) {
                  // The request was made and the server responded
                  // with a status code that falls out of the
                  // range of 2xx
                  ToastsStore.error(
                    `Ping request failed. 
                    Error: ${e.response.data.description}`, 5000,
                  );
                } else {
                  // Something happened in setting up the request
                  // that triggered an Error
                  ToastsStore.error(
                    `Ping request failed. Error: ${e.message}`, 5000,
                  );
                }
              }
            }
            }
          >
            Ping bot
          </Button>
        </div>,
        5,
      ),
    ],
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(
          <Trigger
            name="Telegram Commands"
            checkEnabled={toBool(mainUserConfigJson.telegram_commands.enabled)}
          />
        )}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              {
                'Telegram is also used as a two-way interface with the '
                + 'alerter and as an assistant, allowing you to do things '
                + 'such as snooze phone call alerts and to get the '
                + 'alerter\'s current status from Telegram. Once again, this '
                + 'requires you to set up a Telegram bot, which is free and '
                + 'easy. You can reuse the Telegram bot set up for alerts. '
                + 'However, if you are running more than one instance of the '
                + 'PANIC alerter, do not use the same telegram bot as the '
                + 'other instance(s).'
              }
            </Form.Text>
            {createColumnForm(labels, columns)}
          </div>
        )}
      />
    </div>
  );
}

function RedisForm({
  mainUserConfigJson, validated, handleEnableRedis, redisHostValid,
  handleChangeInRedisHost, handleChangeInRedisPort, redisPortValid,
  handleRedisPassChange, redisFormValid,
}) {
  const labels = [
    createFormLabel(true, '3', 'Enabled'),
    createFormLabel(true, '3', 'Host IP'),
    createFormLabel(true, '3', 'Host port'),
    createFormLabel(true, '3', 'Password'),
  ];
  const columns = [
    createColumnWithContent(
      '1',
      <div>
        <Form.Check
          type="checkbox"
          id="redis-enabled-check-box"
          aria-label="checkbox"
          className="checkbox-style"
          onChange={() => handleEnableRedis()}
          checked={toBool(mainUserConfigJson.redis.enabled)}
        />
      </div>,
      1,
    ),
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="localhost"
            disabled={!toBool(mainUserConfigJson.redis.enabled)}
            onChange={event => handleChangeInRedisHost(event)}
            value={mainUserConfigJson.redis.host}
            isInvalid={validated && !redisHostValid()
            && toBool(mainUserConfigJson.redis.enabled)}
            isValid={validated && redisHostValid()
            && toBool(mainUserConfigJson.redis.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Host IP cannot be empty!
          </Form.Control.Feedback>
        </div>,
        2,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="Redis-host-ip-overlay"
            placement="right"
            overlay={(
              <Tooltip id="redis-host-ip-tooltip">
                The IP of the Redis server. If you will be running PANIC using
                Docker, do not use &apos;localhost&apos;, instead use the full
                IP address (local or external) of the machine that the Redis
                container will be running on.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        3,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="6379"
            disabled={!toBool(mainUserConfigJson.redis.enabled)}
            onChange={event => handleChangeInRedisPort(event)}
            value={mainUserConfigJson.redis.port}
            isInvalid={validated && !redisPortValid()
            && toBool(mainUserConfigJson.redis.enabled)}
            isValid={validated && redisPortValid()
            && toBool(mainUserConfigJson.redis.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(mainUserConfigJson.redis.port)
            ? (
              <Form.Control.Feedback type="invalid">
                Port field cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                Port is not a number.
              </Form.Control.Feedback>
            )}
        </div>,
        4,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="Redis-host-port-overlay"
            placement="right"
            overlay={(
              <Tooltip id="redis-host-port-tooltip">
                The port of the Redis server. If you will be running PANIC
                using Docker, you should leave the port as 6379. If you wish to
                run the Redis container on another port, please input this port
                number here and change the &apos;REDIS_HOST_PORT&apos; value
                inside the &apos;panic_polkadot/.env&apos; file.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        5,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="password"
            placeholder="aKoJ8hHa897gZGiuHiugOIGoiuygOIuugO87
            9gtLnPGkjhgOgiuo76uyi"
            disabled={!toBool(mainUserConfigJson.redis.enabled)}
            onChange={event => handleRedisPassChange(event)}
            value={mainUserConfigJson.redis.password}
            isValid={validated && toBool(mainUserConfigJson.redis.enabled)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
        </div>,
        6,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="Redis-password-overlay"
            placement="right"
            overlay={(
              <Tooltip id="redis-password-tooltip">
                Redis authentication password. Leave blank if no authentication
                was set up.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        7,
      ),
    ],
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(
          <Trigger
            name="Redis"
            checkEnabled={toBool(mainUserConfigJson.redis.enabled)}
          />
          )}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              Redis is used by the alerter to persist data every now and then,
              so that PANIC can continue where it left off if it is restarted.
              It is also used to be able to get the status of the alerter and to
              have some control over it, such as to snooze Twilio phone calls.
            </Form.Text>
            {createColumnForm(labels, columns)}
            <div className="div-content-centre-style">
              <Button
                className="button-style2"
                disabled={
                  !toBool(mainUserConfigJson.redis.enabled) || !redisFormValid()
                }
                onClick={async () => {
                  try {
                    ToastsStore.info('Connecting with Redis.', 5000);
                    await pingRedis(
                      mainUserConfigJson.redis.host,
                      mainUserConfigJson.redis.port,
                      mainUserConfigJson.redis.password,
                    );
                    ToastsStore.success('Connection successful', 5000);
                  } catch (e) {
                    if (e.response) {
                      // The request was made and the server responded
                      // with a status code that falls out of the
                      // range of 2xx
                      ToastsStore.error(
                        `Connection failed. Error: ${
                          e.response.data.error
                        }`, 5000,
                      );
                    } else {
                      // Something happened in setting up the request
                      // that triggered an Error
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
            </div>
          </div>
        )}
      />
    </div>
  );
}

function APIForm({
  mainUserConfigJson, validated, polkadotAPIEndpointValid,
  handleChangeInPolkadotAPIEndpoint, APIFormValid,
}) {
  const labels = [createFormLabel(true, '3', 'Polkadot API Server endpoint')];
  const columns = [
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            placeholder="http://localhost:3000"
            onChange={event => handleChangeInPolkadotAPIEndpoint(event)}
            value={mainUserConfigJson.api.polkadot_api_endpoint}
            isInvalid={validated && !polkadotAPIEndpointValid()}
            isValid={validated && polkadotAPIEndpointValid()}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Polkadot API endpoint cannot be empty.
          </Form.Control.Feedback>
        </div>,
        1,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="API-server-endpoint-overlay"
            placement="right"
            overlay={(
              <Tooltip id="API-server-endpoint-tooltip">
                {'The API server\'s address. If you will be running PANIC '
                + 'using Docker, do not use \'localhost\', instead use the '
                + 'full IP address (local or external) of the machine that '
                + 'the API container will be running on. You should also set '
                + 'the port to 3000. Otherwise, you must run the API Docker '
                + 'using -p <port>:3000.'}
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        2,
      ),
    ],
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(<Trigger name="API Server" />)}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              The API Server is used by the alerter to get data from the nodes.
              It is important that before running and setting up the alerter,
              the API Server is set up and running with all nodes you wish to
              monitor.
            </Form.Text>
            {createColumnForm(labels, columns)}
            <div className="div-content-centre-style">
              <Button
                className="button-style2"
                disabled={!APIFormValid()}
                onClick={async () => {
                  try {
                    ToastsStore.info(`Connecting with API at endpoint ${
                      mainUserConfigJson.api.polkadot_api_endpoint}.`, 5000);
                    await pingAPIServer(
                      mainUserConfigJson.api.polkadot_api_endpoint,
                    );
                    ToastsStore.success('Connection successful', 5000);
                  } catch (e) {
                    if (e.response) {
                      // The request was made and the server responded
                      // with a status code that falls out of the
                      // range of 2xx
                      ToastsStore.error(
                        `Connection failed. Error: ${
                          e.response.data.error
                        }`, 5000,
                      );
                    } else {
                      // Something happened in setting up the request
                      // that triggered an Error
                      ToastsStore.error(
                        `Connection failed. Error: ${e.message}`, 5000,
                      );
                    }
                  }
                }
                }
              >
                Ping API
              </Button>
            </div>
          </div>
        )}
      />
    </div>
  );
}


function MainUserConfigForm({
  mainUserConfigJson, validated, handleChangeInAlerterIdentifier,
  alerterIdentifierValid, handleEnableTelegramAlerts,
  handleChangeInAlertsBotToken, telegramAlertsBotTokenValid,
  telegramAlertsChatIdValid, handleChangeInAlertsChatId,
  handleEnableEmailAlerts, SMTPServerAddressValid,
  handleChangeInSMTPServerAddress, handleChangeInFromAddress, fromAddressValid,
  handleChangeInToAddresses, toAddressesValid, handleUsernameChange,
  handleEmailAlertsPasswordChange, emailAlertsFormValid,
  handleEnableTwilioAlerts, accountSIDValid, handleChangeInTwilioAccountSID,
  accountAuthTokenValid, handleChangeInTwilioAccountAuthToken,
  twilioPhoneNumberValid, handleChangeInTwilioPhoneNumber,
  twilioPhoneNumbersToDialValid, handleChangeInTwilioPhoneNumbersToDial,
  twilioAlertsFormValid, handleEnableMongoAlerts, mongoHostValid,
  handleChangeInMongoHost, handleChangeInMongoPort, mongoPortValid,
  handleChangeInMongoDBName, mongoDBNameValid, handleChangeInMongoUser,
  handleMongoPassChange, handleEnablePAR, PARIntervalSecValid,
  handleChangeInPARIntervalSec, handleEnablePAREmailAlerts,
  handleEnablePARTelegramAlerts, handleEnablePARMongoAlerts,
  handleEnableTelegramCommands, handleChangeInCommandsBotToken,
  telegramCommandsBotTokenValid, telegramCommandsChatIdValid,
  handleChangeInCommandsChatId, handleEnableRedis, redisHostValid,
  handleChangeInRedisHost, handleChangeInRedisPort, redisPortValid,
  handleRedisPassChange, redisFormValid, polkadotAPIEndpointValid,
  handleChangeInPolkadotAPIEndpoint, APIFormValid, mongoFormValid,
}) {
  return (
    <div>
      <h1 className="heading-style-1">Main User Configuration</h1>
      <GeneralForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        handleChangeInAlerterIdentifier={handleChangeInAlerterIdentifier}
        alerterIdentifierValid={alerterIdentifierValid}
      />
      <TelegramAlertsForm
        mainUserConfigJson={mainUserConfigJson}
        handleEnableTelegramAlerts={handleEnableTelegramAlerts}
        validated={validated}
        handleChangeInAlertsBotToken={handleChangeInAlertsBotToken}
        telegramAlertsBotTokenValid={telegramAlertsBotTokenValid}
        telegramAlertsChatIdValid={telegramAlertsChatIdValid}
        handleChangeInAlertsChatId={handleChangeInAlertsChatId}
      />
      <EmailAlertsForm
        validated={validated}
        handleEnableEmailAlerts={handleEnableEmailAlerts}
        mainUserConfigJson={mainUserConfigJson}
        SMTPServerAddressValid={SMTPServerAddressValid}
        handleChangeInSMTPServerAddress={handleChangeInSMTPServerAddress}
        handleChangeInFromAddress={handleChangeInFromAddress}
        fromAddressValid={fromAddressValid}
        handleChangeInToAddresses={handleChangeInToAddresses}
        toAddressesValid={toAddressesValid}
        handleUsernameChange={handleUsernameChange}
        handleEmailAlertsPasswordChange={handleEmailAlertsPasswordChange}
        emailAlertsFormValid={emailAlertsFormValid}
      />
      <TwilioAlertsForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        handleEnableTwilioAlerts={handleEnableTwilioAlerts}
        accountSIDValid={accountSIDValid}
        handleChangeInTwilioAccountSID={handleChangeInTwilioAccountSID}
        handleChangeInTwilioAccountAuthToken={
          handleChangeInTwilioAccountAuthToken
        }
        accountAuthTokenValid={accountAuthTokenValid}
        twilioPhoneNumberValid={twilioPhoneNumberValid}
        handleChangeInTwilioPhoneNumber={handleChangeInTwilioPhoneNumber}
        twilioPhoneNumbersToDialValid={twilioPhoneNumbersToDialValid}
        handleChangeInTwilioPhoneNumbersToDial={
          handleChangeInTwilioPhoneNumbersToDial
        }
        twilioAlertsFormValid={twilioAlertsFormValid}
      />
      <MongoForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        handleEnableMongoAlerts={handleEnableMongoAlerts}
        mongoHostValid={mongoHostValid}
        handleChangeInMongoHost={handleChangeInMongoHost}
        mongoPortValid={mongoPortValid}
        handleChangeInMongoPort={handleChangeInMongoPort}
        handleChangeInMongoDBName={handleChangeInMongoDBName}
        mongoDBNameValid={mongoDBNameValid}
        handleChangeInMongoUser={handleChangeInMongoUser}
        handleMongoPassChange={handleMongoPassChange}
        mongoFormValid={mongoFormValid}
      />
      <PeriodicAliveReminderForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        handleEnablePAR={handleEnablePAR}
        PARIntervalSecValid={PARIntervalSecValid}
        handleChangeInPARIntervalSec={handleChangeInPARIntervalSec}
        handleEnablePAREmailAlerts={handleEnablePAREmailAlerts}
        handleEnablePARTelegramAlerts={handleEnablePARTelegramAlerts}
        handleEnablePARMongoAlerts={handleEnablePARMongoAlerts}
      />
      <TelegramCommandsForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        handleEnableTelegramCommands={handleEnableTelegramCommands}
        handleChangeInCommandsBotToken={handleChangeInCommandsBotToken}
        telegramCommandsBotTokenValid={telegramCommandsBotTokenValid}
        telegramCommandsChatIdValid={telegramCommandsChatIdValid}
        handleChangeInCommandsChatId={handleChangeInCommandsChatId}
      />
      <RedisForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        handleEnableRedis={handleEnableRedis}
        redisHostValid={redisHostValid}
        handleChangeInRedisHost={handleChangeInRedisHost}
        handleChangeInRedisPort={handleChangeInRedisPort}
        redisPortValid={redisPortValid}
        handleRedisPassChange={handleRedisPassChange}
        redisFormValid={redisFormValid}
      />
      <APIForm
        mainUserConfigJson={mainUserConfigJson}
        validated={validated}
        polkadotAPIEndpointValid={polkadotAPIEndpointValid}
        handleChangeInPolkadotAPIEndpoint={handleChangeInPolkadotAPIEndpoint}
        APIFormValid={APIFormValid}
      />
    </div>
  );
}

class MainUserConfig extends Component {
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
  // each address is non-empty.
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

  mongoHostValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.mongo.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.mongo.host);
  }

  mongoPortValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.mongo.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.mongo.port)
      && new RegExp('^([0-9]+)*$').test(state.mainUserConfigJson.mongo.port);
  }

  telegramAlertsFormValid() {
    return this.telegramAlertsBotTokenValid()
      && this.telegramAlertsChatIdValid();
  }

  emailAlertsFormValid() {
    return this.SMTPServerAddressValid() && this.fromAddressValid()
      && this.toAddressesValid();
  }

  twilioAlertsFormValid() {
    return this.accountSIDValid() && this.accountAuthTokenValid()
      && this.twilioPhoneNumberValid() && this.twilioPhoneNumbersToDialValid();
  }

  mongoDBNameValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.mongo.enabled)) {
      return true;
    }
    return new RegExp('^[^ ]+$').test(state.mainUserConfigJson.mongo.db_name);
  }

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

  redisHostValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.redis.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.redis.host);
  }

  redisPortValid() {
    const { state } = this;
    if (!toBool(state.mainUserConfigJson.redis.enabled)) {
      return true;
    }
    return !fieldEmpty(state.mainUserConfigJson.redis.port)
      && new RegExp('^([0-9]+)*$').test(state.mainUserConfigJson.redis.port);
  }

  polkadotAPIEndpointValid() {
    const { state } = this;
    return !fieldEmpty(state.mainUserConfigJson.api.polkadot_api_endpoint);
  }

  generalFormValid() {
    return this.alerterIdentifierValid();
  }

  APIFormValid() {
    return this.polkadotAPIEndpointValid();
  }

  mongoFormValid() {
    return this.mongoHostValid() && this.mongoPortValid()
      && this.mongoDBNameValid();
  }

  PARFormValid() {
    return this.PARIntervalSecValid();
  }

  telegramCommandsFormValid() {
    return this.telegramCommandsBotTokenValid()
      && this.telegramCommandsChatIdValid();
  }

  redisFormValid() {
    return this.redisHostValid() && this.redisPortValid();
  }

  mainUserConfigValid() {
    return this.generalFormValid() && this.telegramAlertsFormValid()
      && this.emailAlertsFormValid() && this.twilioAlertsFormValid()
      && this.mongoFormValid() && this.PARFormValid()
      && this.telegramCommandsFormValid() && this.redisFormValid()
      && this.APIFormValid();
  }

  handleChangeInAlerterIdentifier(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.mainUserConfigJson;
      newConfig.general.unique_alerter_identifier = event.target.value;
      return { mainUserConfigJson: newConfig };
    });
  }

  handleChangeInAlertsBotToken(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.mainUserConfigJson;
      newConfig.telegram_alerts.bot_token = event.target.value;
      return { mainUserConfigJson: newConfig };
    });
  }

  handleChangeInAlertsChatId(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.mainUserConfigJson;
      newConfig.telegram_alerts.bot_chat_id = event.target.value;
      return { mainUserConfigJson: newConfig };
    });
  }

  handleChangeInSMTPServerAddress(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.mainUserConfigJson;
      newConfig.email_alerts.smtp = event.target.value;
      return { mainUserConfigJson: newConfig };
    });
  }

  handleEnableTelegramAlerts() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.telegram_alerts.enabled = (!toBool(
        prevState.mainUserConfigJson.telegram_alerts.enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEnableEmailAlerts() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.email_alerts.enabled = (!toBool(
        prevState.mainUserConfigJson.email_alerts.enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEnableMongoAlerts() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.mongo.enabled = (!toBool(
        prevState.mainUserConfigJson.mongo.enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInFromAddress(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.email_alerts.from = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInToAddresses(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.email_alerts.to = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleUsernameChange(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.email_alerts.user = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEmailAlertsPasswordChange(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.email_alerts.pass = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEnableTwilioAlerts() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.twilio_alerts.enabled = (!toBool(
        prevState.mainUserConfigJson.twilio_alerts.enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEnablePAR() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.periodic_alive_reminder.enabled = (!toBool(
        prevState.mainUserConfigJson.periodic_alive_reminder.enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEnablePAREmailAlerts() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.periodic_alive_reminder.email_enabled = (!toBool(
        prevState.mainUserConfigJson.periodic_alive_reminder.email_enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEnablePARTelegramAlerts() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.periodic_alive_reminder.telegram_enabled = (!toBool(
        prevState.mainUserConfigJson.periodic_alive_reminder.telegram_enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEnablePARMongoAlerts() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.periodic_alive_reminder.mongo_enabled = (!toBool(
        prevState.mainUserConfigJson.periodic_alive_reminder.mongo_enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEnableTelegramCommands() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.telegram_commands.enabled = (!toBool(
        prevState.mainUserConfigJson.telegram_commands.enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleEnableRedis() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.redis.enabled = (!toBool(
        prevState.mainUserConfigJson.redis.enabled,
      )).toString();
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInTwilioAccountSID(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.twilio_alerts.account_sid = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInTwilioAccountAuthToken(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.twilio_alerts.auth_token = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInTwilioPhoneNumber(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.twilio_alerts.twilio_phone_number = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInTwilioPhoneNumbersToDial(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.twilio_alerts.phone_numbers_to_dial = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInMongoHost(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.mongo.host = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInMongoPort(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.mongo.port = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInMongoDBName(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.mongo.db_name = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInMongoUser(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.mongo.user = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  // TODO: Re-factor these into a single function which takes the entry to be
  //       modified.

  handleMongoPassChange(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.mongo.pass = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInPARIntervalSec(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.periodic_alive_reminder.interval_seconds = event.target
        .value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInCommandsBotToken(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.telegram_commands.bot_token = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInCommandsChatId(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.telegram_commands.bot_chat_id = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInRedisHost(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.redis.host = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInRedisPort(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.redis.port = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleRedisPassChange(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.redis.password = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  handleChangeInPolkadotAPIEndpoint(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      newMainUserConfig.api.polkadot_api_endpoint = event.target.value;
      return { mainUserConfigJson: newMainUserConfig };
    });
  }

  // This function is used to fix data fields which are dependent on each other.
  // For example there is no need to store the mongo password if authentication
  // is disabled. This must be done before saving the config to prevent having
  // un-meaningful data in the config.
  fixUserConfigMain() {
    this.setState((prevState) => {
      const newMainUserConfig = prevState.mainUserConfigJson;
      // if username is blank, then authentication is disabled, therefore
      // password should be cleared
      if (fieldEmpty(newMainUserConfig.email_alerts.user)) {
        newMainUserConfig.email_alerts.pass = '';
      }
      if (fieldEmpty(newMainUserConfig.mongo.user)) {
        newMainUserConfig.mongo.pass = '';
      }

      // if a channel is disabled, there is no point in leaving it enabled for
      // the PAR
      if (!toBool(newMainUserConfig.email_alerts.enabled)) {
        newMainUserConfig.periodic_alive_reminder.email_enabled = 'false';
      }
      if (!toBool(newMainUserConfig.telegram_alerts.enabled)) {
        newMainUserConfig.periodic_alive_reminder.telegram_enabled = 'false';
      }
      if (!toBool(newMainUserConfig.mongo.enabled)) {
        newMainUserConfig.periodic_alive_reminder.mongo_enabled = 'false';
      }

      // Clear data of non-enabled sections
      Object.entries(newMainUserConfig).forEach(([section, data]) => {
        if (section !== 'general' && section !== 'api') {
          if (toBool(newMainUserConfig[section].enabled) === false) {
            newMainUserConfig[section] = clearSectionData(data);
          }
        }
      });
      return { mainUserConfigJson: newMainUserConfig };
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
                <Container>
                  <MainUserConfigForm
                    mainUserConfigJson={state.mainUserConfigJson}
                    handleEnableTelegramAlerts={
                      () => this.handleEnableTelegramAlerts()
                    }
                    handleEnableEmailAlerts={
                      () => this.handleEnableEmailAlerts()
                    }
                    handleEnableTwilioAlerts={
                      () => this.handleEnableTwilioAlerts()
                    }
                    handleEnableMongoAlerts={
                      () => this.handleEnableMongoAlerts()
                    }
                    handleEnablePAR={() => this.handleEnablePAR()}
                    handleEnablePAREmailAlerts={
                      () => this.handleEnablePAREmailAlerts()
                    }
                    handleEnablePARTelegramAlerts={
                      () => this.handleEnablePARTelegramAlerts()
                    }
                    handleEnablePARMongoAlerts={
                      () => this.handleEnablePARMongoAlerts()
                    }
                    handleEnableTelegramCommands={
                      () => this.handleEnableTelegramCommands()
                    }
                    handleEnableRedis={() => this.handleEnableRedis()}
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
                    handleChangeInAlerterIdentifier={
                      event => this.handleChangeInAlerterIdentifier(event)
                    }
                    handleChangeInAlertsBotToken={
                      event => this.handleChangeInAlertsBotToken(event)
                    }
                    handleChangeInAlertsChatId={
                      event => this.handleChangeInAlertsChatId(event)
                    }
                    handleChangeInSMTPServerAddress={
                      event => this.handleChangeInSMTPServerAddress(event)
                    }
                    handleChangeInFromAddress={
                      event => this.handleChangeInFromAddress(event)
                    }
                    handleChangeInToAddresses={
                      event => this.handleChangeInToAddresses(event)
                    }
                    handleChangeInMongoHost={
                      event => this.handleChangeInMongoHost(event)
                    }
                    handleUsernameChange={
                      event => this.handleUsernameChange(event)
                    }
                    handleEmailAlertsPasswordChange={
                      event => this.handleEmailAlertsPasswordChange(event)
                    }
                    accountSIDValid={() => this.accountSIDValid()}
                    telegramCommandsBotTokenValid={
                      () => this.telegramCommandsBotTokenValid()
                    }
                    handleChangeInTwilioAccountSID={
                      event => this.handleChangeInTwilioAccountSID(event)
                    }
                    handleChangeInTwilioAccountAuthToken={
                      event => this.handleChangeInTwilioAccountAuthToken(event)
                    }
                    handleChangeInTwilioPhoneNumber={
                      event => this.handleChangeInTwilioPhoneNumber(event)
                    }
                    handleChangeInTwilioPhoneNumbersToDial={
                      event => this.handleChangeInTwilioPhoneNumbersToDial(
                        event,
                      )
                    }
                    handleChangeInMongoPort={
                      event => this.handleChangeInMongoPort(event)
                    }
                    handleChangeInMongoDBName={
                      event => this.handleChangeInMongoDBName(event)
                    }
                    handleChangeInMongoUser={
                      event => this.handleChangeInMongoUser(event)
                    }
                    handleMongoPassChange={
                      event => this.handleMongoPassChange(event)
                    }
                    handleChangeInPARIntervalSec={
                      event => this.handleChangeInPARIntervalSec(event)
                    }
                    handleChangeInCommandsBotToken={
                      event => this.handleChangeInCommandsBotToken(event)
                    }
                    handleChangeInCommandsChatId={
                      event => this.handleChangeInCommandsChatId(event)
                    }
                    handleChangeInRedisHost={
                      event => this.handleChangeInRedisHost(event)
                    }
                    handleChangeInRedisPort={
                      event => this.handleChangeInRedisPort(event)
                    }
                    handleRedisPassChange={
                      event => this.handleRedisPassChange(event)
                    }
                    handleChangeInPolkadotAPIEndpoint={
                      event => this.handleChangeInPolkadotAPIEndpoint(event)
                    }
                  />
                  <div className="div-content-centre-style-margin-top">
                    <Button
                      className="button-style2"
                      onClick={async (event) => {
                        event.preventDefault();
                        if (!this.mainUserConfigValid()) {
                          this.setState({ validated: true });
                          event.stopPropagation();
                          return;
                        }
                        try {
                          ToastsStore.info('Saving config', 5000);
                          this.fixUserConfigMain();
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
                      }
                      }
                    >
                      Save Config
                    </Button>
                  </div>
                </Container>
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

CollapsibleForm.propTypes = forbidExtraProps({
  trigger: PropTypes.oneOfType([PropTypes.element, PropTypes.string])
    .isRequired,
  triggerClassName: PropTypes.string.isRequired,
  triggerOpenedClassName: PropTypes.string.isRequired,
  triggerDisabled: PropTypes.bool,
  open: PropTypes.bool,
  content: PropTypes.oneOfType([PropTypes.element, PropTypes.string])
    .isRequired,
});

CollapsibleForm.defaultProps = {
  triggerDisabled: false,
  open: false,
};

Trigger.propTypes = forbidExtraProps({
  name: PropTypes.string.isRequired,
  checkEnabled: PropTypes.bool,
});

Trigger.defaultProps = {
  checkEnabled: false,
};

GeneralForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  handleChangeInAlerterIdentifier: PropTypes.func.isRequired,
  alerterIdentifierValid: PropTypes.func.isRequired,
});

TelegramAlertsForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  handleEnableTelegramAlerts: PropTypes.func.isRequired,
  handleChangeInAlertsBotToken: PropTypes.func.isRequired,
  telegramAlertsBotTokenValid: PropTypes.func.isRequired,
  telegramAlertsChatIdValid: PropTypes.func.isRequired,
  handleChangeInAlertsChatId: PropTypes.func.isRequired,
});

EmailAlertsForm.propTypes = forbidExtraProps({
  handleEnableEmailAlerts: PropTypes.func.isRequired,
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  SMTPServerAddressValid: PropTypes.func.isRequired,
  handleChangeInSMTPServerAddress: PropTypes.func.isRequired,
  validated: PropTypes.bool.isRequired,
  handleChangeInFromAddress: PropTypes.func.isRequired,
  fromAddressValid: PropTypes.func.isRequired,
  handleChangeInToAddresses: PropTypes.func.isRequired,
  toAddressesValid: PropTypes.func.isRequired,
  handleUsernameChange: PropTypes.func.isRequired,
  handleEmailAlertsPasswordChange: PropTypes.func.isRequired,
  emailAlertsFormValid: PropTypes.func.isRequired,
});

TwilioAlertsForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  handleEnableTwilioAlerts: PropTypes.func.isRequired,
  accountSIDValid: PropTypes.func.isRequired,
  handleChangeInTwilioAccountSID: PropTypes.func.isRequired,
  handleChangeInTwilioAccountAuthToken: PropTypes.func.isRequired,
  accountAuthTokenValid: PropTypes.func.isRequired,
  twilioPhoneNumberValid: PropTypes.func.isRequired,
  handleChangeInTwilioPhoneNumber: PropTypes.func.isRequired,
  twilioPhoneNumbersToDialValid: PropTypes.func.isRequired,
  handleChangeInTwilioPhoneNumbersToDial: PropTypes.func.isRequired,
  twilioAlertsFormValid: PropTypes.func.isRequired,
});

MongoForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  handleEnableMongoAlerts: PropTypes.func.isRequired,
  mongoHostValid: PropTypes.func.isRequired,
  handleChangeInMongoHost: PropTypes.func.isRequired,
  handleChangeInMongoPort: PropTypes.func.isRequired,
  mongoPortValid: PropTypes.func.isRequired,
  handleChangeInMongoDBName: PropTypes.func.isRequired,
  mongoDBNameValid: PropTypes.func.isRequired,
  handleChangeInMongoUser: PropTypes.func.isRequired,
  handleMongoPassChange: PropTypes.func.isRequired,
  mongoFormValid: PropTypes.func.isRequired,
});

PeriodicAliveReminderForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  handleEnablePAR: PropTypes.func.isRequired,
  PARIntervalSecValid: PropTypes.func.isRequired,
  handleChangeInPARIntervalSec: PropTypes.func.isRequired,
  handleEnablePAREmailAlerts: PropTypes.func.isRequired,
  handleEnablePARTelegramAlerts: PropTypes.func.isRequired,
  handleEnablePARMongoAlerts: PropTypes.func.isRequired,
});

TelegramCommandsForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  handleEnableTelegramCommands: PropTypes.func.isRequired,
  handleChangeInCommandsBotToken: PropTypes.func.isRequired,
  telegramCommandsBotTokenValid: PropTypes.func.isRequired,
  telegramCommandsChatIdValid: PropTypes.func.isRequired,
  handleChangeInCommandsChatId: PropTypes.func.isRequired,
});

RedisForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  handleEnableRedis: PropTypes.func.isRequired,
  redisHostValid: PropTypes.func.isRequired,
  handleChangeInRedisHost: PropTypes.func.isRequired,
  handleChangeInRedisPort: PropTypes.func.isRequired,
  redisPortValid: PropTypes.func.isRequired,
  handleRedisPassChange: PropTypes.func.isRequired,
  redisFormValid: PropTypes.func.isRequired,
});

APIForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  polkadotAPIEndpointValid: PropTypes.func.isRequired,
  handleChangeInPolkadotAPIEndpoint: PropTypes.func.isRequired,
  APIFormValid: PropTypes.func.isRequired,
});

MainUserConfigForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  handleChangeInAlerterIdentifier: PropTypes.func.isRequired,
  alerterIdentifierValid: PropTypes.func.isRequired,
  handleEnableTelegramAlerts: PropTypes.func.isRequired,
  handleChangeInAlertsBotToken: PropTypes.func.isRequired,
  telegramAlertsBotTokenValid: PropTypes.func.isRequired,
  telegramAlertsChatIdValid: PropTypes.func.isRequired,
  handleChangeInAlertsChatId: PropTypes.func.isRequired,
  handleEnableEmailAlerts: PropTypes.func.isRequired,
  SMTPServerAddressValid: PropTypes.func.isRequired,
  handleChangeInSMTPServerAddress: PropTypes.func.isRequired,
  handleChangeInFromAddress: PropTypes.func.isRequired,
  fromAddressValid: PropTypes.func.isRequired,
  handleChangeInToAddresses: PropTypes.func.isRequired,
  toAddressesValid: PropTypes.func.isRequired,
  handleUsernameChange: PropTypes.func.isRequired,
  handleEmailAlertsPasswordChange: PropTypes.func.isRequired,
  emailAlertsFormValid: PropTypes.func.isRequired,
  handleEnableTwilioAlerts: PropTypes.func.isRequired,
  accountSIDValid: PropTypes.func.isRequired,
  handleChangeInTwilioAccountSID: PropTypes.func.isRequired,
  accountAuthTokenValid: PropTypes.func.isRequired,
  handleChangeInTwilioAccountAuthToken: PropTypes.func.isRequired,
  twilioPhoneNumberValid: PropTypes.func.isRequired,
  handleChangeInTwilioPhoneNumber: PropTypes.func.isRequired,
  twilioPhoneNumbersToDialValid: PropTypes.func.isRequired,
  handleChangeInTwilioPhoneNumbersToDial: PropTypes.func.isRequired,
  twilioAlertsFormValid: PropTypes.func.isRequired,
  handleEnableMongoAlerts: PropTypes.func.isRequired,
  mongoHostValid: PropTypes.func.isRequired,
  handleChangeInMongoHost: PropTypes.func.isRequired,
  handleChangeInMongoPort: PropTypes.func.isRequired,
  mongoPortValid: PropTypes.func.isRequired,
  handleChangeInMongoDBName: PropTypes.func.isRequired,
  mongoDBNameValid: PropTypes.func.isRequired,
  handleChangeInMongoUser: PropTypes.func.isRequired,
  handleMongoPassChange: PropTypes.func.isRequired,
  handleEnablePAR: PropTypes.func.isRequired,
  PARIntervalSecValid: PropTypes.func.isRequired,
  handleChangeInPARIntervalSec: PropTypes.func.isRequired,
  handleEnablePAREmailAlerts: PropTypes.func.isRequired,
  handleEnablePARTelegramAlerts: PropTypes.func.isRequired,
  handleEnablePARMongoAlerts: PropTypes.func.isRequired,
  handleEnableTelegramCommands: PropTypes.func.isRequired,
  handleChangeInCommandsBotToken: PropTypes.func.isRequired,
  telegramCommandsBotTokenValid: PropTypes.func.isRequired,
  telegramCommandsChatIdValid: PropTypes.func.isRequired,
  handleChangeInCommandsChatId: PropTypes.func.isRequired,
  handleEnableRedis: PropTypes.func.isRequired,
  redisHostValid: PropTypes.func.isRequired,
  handleChangeInRedisHost: PropTypes.func.isRequired,
  handleChangeInRedisPort: PropTypes.func.isRequired,
  redisPortValid: PropTypes.func.isRequired,
  handleRedisPassChange: PropTypes.func.isRequired,
  redisFormValid: PropTypes.func.isRequired,
  polkadotAPIEndpointValid: PropTypes.func.isRequired,
  handleChangeInPolkadotAPIEndpoint: PropTypes.func.isRequired,
  APIFormValid: PropTypes.func.isRequired,
  mongoFormValid: PropTypes.func.isRequired,
});

export {
  MainUserConfig, CollapsibleForm, createFormLabel, createColumnForm,
  createColumnWithContent, Trigger,
};
