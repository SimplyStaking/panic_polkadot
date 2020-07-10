import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import { CollapsibleForm, Trigger } from './collapsible_form';
import {
  createColumnForm, createColumnWithContent, createFormLabel,
} from '../../utils/forms';
import '../../style/style.css';
import TooltipOverlay from '../overlays';
import { PingApiButton } from '../buttons';

function APIServerForm({
  mainUserConfigJson, validated, polkadotAPIEndpointValid, APIFormValid,
  handleChangeInNonBooleanField,
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
            onChange={
              event => handleChangeInNonBooleanField(
                event, 'api', 'polkadot_api_endpoint',
              )
            }
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
          <TooltipOverlay
            identifier="API-server-endpoint"
            placement="right"
            tooltipText={'The API server\'s address. If you will be running '
            + 'PANIC using Docker, do not use \'localhost\', instead use the '
            + 'full IP address (local or external) of the machine that the API '
            + 'container will be running on. You should also set the port to '
            + '3000. Otherwise, you must run the API Docker using '
            + '-p <port>:3000.'}
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
              <PingApiButton
                disabled={!APIFormValid()}
                endpoint={mainUserConfigJson.api.polkadot_api_endpoint}
              />
            </div>
          </div>
        )}
      />
    </div>
  );
}

APIServerForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  polkadotAPIEndpointValid: PropTypes.func.isRequired,
  APIFormValid: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
});

export default APIServerForm;
