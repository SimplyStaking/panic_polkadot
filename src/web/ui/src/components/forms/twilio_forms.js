import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import { CollapsibleForm, Trigger } from './collapsible_form';
import { fieldEmpty } from '../../utils/configs';
import {
  createColumnForm,
  createColumnWithContent,
  createFormLabel,
} from '../../utils/forms';
import { toBool } from '../../utils/string';
import '../../style/style.css';
import TooltipOverlay from '../overlays';
import { TestCallButton } from '../buttons';

function TwilioAlertsForm({
  mainUserConfigJson, validated, accountSIDValid, accountAuthTokenValid,
  twilioPhoneNumberValid, twilioPhoneNumbersToDialValid, twilioAlertsFormValid,
  handleChangeInNonBooleanField, handleChangeInBooleanField,
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
          onChange={
            event => handleChangeInBooleanField(
              event, 'twilio_alerts', 'enabled',
            )
          }
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
          onChange={
            event => handleChangeInNonBooleanField(
              event, 'twilio_alerts', 'account_sid',
            )
          }
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
          onChange={
            event => handleChangeInNonBooleanField(
              event, 'twilio_alerts', 'auth_token',
            )
          }
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'twilio_alerts', 'twilio_phone_number',
              )
            }
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
          <TooltipOverlay
            identifier="twilio-alerts-phone-no"
            placement="right"
            tooltipText="Your registered Twilio phone number"
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
            placeholder="+12025551235;+12025551236;+12025551237"
            disabled={!toBool(mainUserConfigJson.twilio_alerts.enabled)}
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'twilio_alerts', 'phone_numbers_to_dial',
              )
            }
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
          <TooltipOverlay
            identifier="twilio-alerts-to-dial-no"
            placement="right"
            tooltipText="Phone numbers to receive alerts"
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
              <TestCallButton
                disabled={!toBool(mainUserConfigJson.twilio_alerts.enabled)
                || !twilioAlertsFormValid()}
                phoneNoToDial={
                  mainUserConfigJson.twilio_alerts.phone_numbers_to_dial
                    .split(';')[0]
                }
                accountSid={mainUserConfigJson.twilio_alerts.account_sid}
                authToken={mainUserConfigJson.twilio_alerts.auth_token}
                twilioPhoneNo={
                  mainUserConfigJson.twilio_alerts.twilio_phone_number
                }
              />
            </div>
          </div>
        )}
      />
    </div>
  );
}

TwilioAlertsForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  accountSIDValid: PropTypes.func.isRequired,
  accountAuthTokenValid: PropTypes.func.isRequired,
  twilioPhoneNumberValid: PropTypes.func.isRequired,
  twilioPhoneNumbersToDialValid: PropTypes.func.isRequired,
  twilioAlertsFormValid: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
});

export default TwilioAlertsForm;
