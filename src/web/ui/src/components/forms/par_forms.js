import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import { CollapsibleForm, Trigger } from './collapsible_form';
import { fieldEmpty } from '../../utils/configs';
import { toBool } from '../../utils/string';
import {
  createColumnForm, createColumnWithContent, createFormLabel,
} from '../../utils/forms';
import TooltipOverlay from '../overlays';
import '../../style/style.css';

function PARForm({
  mainUserConfigJson, validated, PARIntervalSecValid,
  handleChangeInBooleanField, handleChangeInNonBooleanField,
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
          onChange={
            event => handleChangeInBooleanField(
              event, 'periodic_alive_reminder', 'enabled',
            )
          }
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'periodic_alive_reminder', 'interval_seconds',
              )
            }
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
          <TooltipOverlay
            identifier="par-interval"
            placement="right"
            tooltipText={'The number of seconds to pass before sending an '
            + 'alive reminder alert.'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
            onChange={
              event => handleChangeInBooleanField(
                event, 'periodic_alive_reminder', 'email_enabled',
              )
            }
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
          <TooltipOverlay
            identifier="mpar-email-enabled"
            placement="right"
            tooltipText={'Tick box if you wish to receive reminder alerts via '
            + 'e-mail. Only applicable if e-mail alerts are enabled.'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
            onChange={
              event => handleChangeInBooleanField(
                event, 'periodic_alive_reminder', 'telegram_enabled',
              )
            }
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
          <TooltipOverlay
            identifier="par-telegram-enabled"
            placement="right"
            tooltipText={'Tick box if you wish to receive reminder alerts via '
            + 'Telegram. Only applicable if Telegram alerts are enabled.'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
            onChange={
              event => handleChangeInBooleanField(
                event, 'periodic_alive_reminder', 'mongo_enabled',
              )
            }
            checked={
              toBool(mainUserConfigJson.periodic_alive_reminder.mongo_enabled)
            }
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <TooltipOverlay
            identifier="par-mongo-enabled"
            placement="right"
            tooltipText={'Tick box if you wish to save reminder alerts in a '
            + 'Mongo database. Only applicable if Mongo was set up.'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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

PARForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  PARIntervalSecValid: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
});

export default PARForm;
