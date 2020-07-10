import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import {
  createColumnForm, createColumnWithContent, createFormLabel,
} from '../../utils/forms';
import { CollapsibleForm, Trigger } from './collapsible_form';
import TooltipOverlay from '../overlays';
import '../../style/style.css';

function GeneralForm({
  mainUserConfigJson, validated, handleChangeInNonBooleanField,
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'general', 'unique_alerter_identifier',
              )
            }
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
          <TooltipOverlay
            identifier="general-unique-alerter-identifier"
            placement="right"
            tooltipText={'Please make sure that uniqueness is observed since '
            + 'this setup cannot detect other PANIC configurations'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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

GeneralForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
  alerterIdentifierValid: PropTypes.func.isRequired,
});

export default GeneralForm;
