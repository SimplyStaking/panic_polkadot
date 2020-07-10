import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import { fieldEmpty } from '../../utils/configs';
import { CollapsibleForm, Trigger } from './collapsible_form';
import { toBool } from '../../utils/string';
import {
  createColumnForm,
  createColumnWithContent,
  createFormLabel,
} from '../../utils/forms';
import '../../style/style.css';
import TooltipOverlay from '../overlays';
import { SendTestEmailButton } from '../buttons';

function EmailAlertsForm({
  mainUserConfigJson, SMTPServerAddressValid, validated, fromAddressValid,
  toAddressesValid, emailAlertsFormValid, handleChangeInNonBooleanField,
  handleChangeInBooleanField,
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
          onChange={
            event => handleChangeInBooleanField(
              event, 'email_alerts', 'enabled',
            )
          }
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
          onChange={
            event => handleChangeInNonBooleanField(
              event, 'email_alerts', 'smtp',
            )
          }
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'email_alerts', 'from',
              )
            }
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
          <TooltipOverlay
            identifier="email-alerts-sender"
            placement="right"
            tooltipText="Specify the details of the sender"
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'email_alerts', 'to',
              )
            }
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
          <TooltipOverlay
            identifier="email-alerts-to"
            placement="right"
            tooltipText={'Specify the e-mail addresses where you want to '
            + 'receive alerts.'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'email_alerts', 'user',
              )
            }
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
          <TooltipOverlay
            identifier="email-alerts-username"
            placement="right"
            tooltipText={'Username for SMTP authentication. Leave blank for '
            + 'no authentication.'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
            disabled={(!toBool(mainUserConfigJson.email_alerts.enabled))
            || (fieldEmpty(mainUserConfigJson.email_alerts.user))}
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'email_alerts', 'pass',
              )
            }
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
          <TooltipOverlay
            identifier="email-alerts-password"
            placement="right"
            tooltipText="Password for SMTP authentication."
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
              <SendTestEmailButton
                disabled={!toBool(mainUserConfigJson.email_alerts.enabled)
                || !emailAlertsFormValid()}
                to={mainUserConfigJson.email_alerts.to.split(';')[0]}
                from={mainUserConfigJson.email_alerts.from}
                smtp={mainUserConfigJson.email_alerts.smtp}
                user={mainUserConfigJson.email_alerts.user}
                pass={mainUserConfigJson.email_alerts.pass}
              />
            </div>
          </div>
        )}
      />
    </div>
  );
}

EmailAlertsForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  SMTPServerAddressValid: PropTypes.func.isRequired,
  validated: PropTypes.bool.isRequired,
  fromAddressValid: PropTypes.func.isRequired,
  toAddressesValid: PropTypes.func.isRequired,
  emailAlertsFormValid: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
});

export default EmailAlertsForm;
