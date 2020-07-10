import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import {
  createColumnForm, createColumnWithContent, createFormLabel,
} from '../../utils/forms';
import { toBool } from '../../utils/string';
import { CollapsibleForm, Trigger } from './collapsible_form';
import {
  ConnectWithBotButton,
  PingBotButton,
  SendTestAlertButton,
} from '../buttons';
import '../../style/style.css';

function TelegramAlertsForm({
  mainUserConfigJson, validated, telegramAlertsBotTokenValid,
  telegramAlertsChatIdValid, handleChangeInBooleanField,
  handleChangeInNonBooleanField,
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
          onChange={
            event => handleChangeInBooleanField(
              event, 'telegram_alerts', 'enabled',
            )
          }
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'telegram_alerts', 'bot_token',
              )
            }
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
          <ConnectWithBotButton
            disabled={!toBool(mainUserConfigJson.telegram_alerts.enabled)
            || !telegramAlertsBotTokenValid()}
            botToken={mainUserConfigJson.telegram_alerts.bot_token}
          />
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'telegram_alerts', 'bot_chat_id',
              )
            }
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
          <SendTestAlertButton
            disabled={!toBool(mainUserConfigJson.telegram_alerts.enabled)
            || !telegramAlertsChatIdValid()}
            botChatID={mainUserConfigJson.telegram_alerts.bot_chat_id}
            botToken={mainUserConfigJson.telegram_alerts.bot_token}
          />
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

function TelegramCommandsForm({
  mainUserConfigJson, validated, telegramCommandsBotTokenValid,
  telegramCommandsChatIdValid, handleChangeInNonBooleanField,
  handleChangeInBooleanField,
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
          onChange={
            event => handleChangeInBooleanField(
              event, 'telegram_commands', 'enabled',
            )
          }
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'telegram_commands', 'bot_token',
              )
            }
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
          <ConnectWithBotButton
            disabled={!toBool(mainUserConfigJson.telegram_commands.enabled)
            || !telegramCommandsBotTokenValid()}
            botToken={mainUserConfigJson.telegram_commands.bot_token}
          />
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'telegram_commands', 'bot_chat_id',
              )
            }
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
          <PingBotButton
            disabled={!toBool(mainUserConfigJson.telegram_commands.enabled)
            || !telegramCommandsChatIdValid()}
            botToken={mainUserConfigJson.telegram_commands.bot_token}
            botChatID={mainUserConfigJson.telegram_commands.bot_chat_id}
          />
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
                + 'alerter\'s current status. Once again, this requires you to '
                + 'set up a Telegram bot, which is free and easy. You can '
                + 'reuse the Telegram bot set up for alerts. However, if you '
                + 'are running more than one instance of the alerter, '
                + 'do not use the same telegram bot as the other instance(s).'
              }
            </Form.Text>
            {createColumnForm(labels, columns)}
          </div>
        )}
      />
    </div>
  );
}

TelegramAlertsForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  telegramAlertsBotTokenValid: PropTypes.func.isRequired,
  telegramAlertsChatIdValid: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
});

TelegramCommandsForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  telegramCommandsBotTokenValid: PropTypes.func.isRequired,
  telegramCommandsChatIdValid: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
});

export { TelegramAlertsForm, TelegramCommandsForm };
