import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import { CollapsibleForm, Trigger } from './collapsible_form';
import { fieldEmpty } from '../../utils/configs';
import {
  createColumnForm, createColumnWithContent, createFormLabel,
} from '../../utils/forms';
import { toBool } from '../../utils/string';
import TooltipOverlay from '../overlays';
import { ConnectWithMongoButton } from '../buttons';
import '../../style/style.css';

function MongoForm({
  mainUserConfigJson, validated, mongoHostValid, mongoPortValid,
  mongoDBNameValid, mongoFormValid, handleChangeInNonBooleanField,
  handleChangeInBooleanField,
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
          onChange={
            event => handleChangeInBooleanField(event, 'mongo', 'enabled')
          }
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
            onChange={
              event => handleChangeInNonBooleanField(event, 'mongo', 'host')
            }
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
          <TooltipOverlay
            identifier="mongo-host-ip"
            placement="right"
            tooltipText={'The IP of the Mongo server. If you will be running '
            + 'PANIC using Docker, do not use \'localhost\', instead use the '
            + 'full IP address (local or external) of the machine that the '
            + 'Mongo container will be running on.'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
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
            placeholder="27017"
            disabled={!toBool(mainUserConfigJson.mongo.enabled)}
            onChange={
              event => handleChangeInNonBooleanField(event, 'mongo', 'port')
            }
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
          <TooltipOverlay
            identifier="mongo-host-port"
            placement="right"
            tooltipText={'The port of the Mongo server. If you will be running '
            + 'PANIC using Docker, you should leave the port as 27017. If you '
            + 'wish to run the Mongo container on another port, please input '
            + 'this port number here and change the \'MONGO_HOST_PORT\' value '
            + 'inside the \'panic_polkadot/.env\' file'}
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
            placeholder="panic"
            disabled={!toBool(mainUserConfigJson.mongo.enabled)}
            onChange={
              event => handleChangeInNonBooleanField(event, 'mongo', 'db_name')
            }
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
          <TooltipOverlay
            identifier="mongo-database-name"
            placement="right"
            tooltipText={'The database you wish to use to store the alerts. '
            + 'This will be auto-created if it does not exist. You can re-use '
            + 'the same database if another PANIC is installed.'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
            onChange={
              event => handleChangeInNonBooleanField(event, 'mongo', 'user')
            }
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
          <TooltipOverlay
            identifier="mongo-username"
            placement="right"
            tooltipText={'Username for authentication. Leave blank for no '
            + 'authentication.'}
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
            disabled={
              (!toBool(mainUserConfigJson.mongo.enabled))
              || (fieldEmpty(mainUserConfigJson.mongo.user))
            }
            onChange={
              event => handleChangeInNonBooleanField(event, 'mongo', 'pass')
            }
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
          <TooltipOverlay
            identifier="mongo-password"
            placement="right"
            tooltipText="Password for authentication."
            component={<FontAwesomeIcon icon={faInfoCircle} />}
          />
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
              <ConnectWithMongoButton
                disabled={!toBool(mainUserConfigJson.mongo.enabled)
                || !mongoFormValid()}
                host={mainUserConfigJson.mongo.host}
                port={mainUserConfigJson.mongo.port}
                user={mainUserConfigJson.mongo.user}
                pass={mainUserConfigJson.mongo.pass}
              />
            </div>
          </div>
        )}
      />
    </div>
  );
}

MongoForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  mongoHostValid: PropTypes.func.isRequired,
  mongoPortValid: PropTypes.func.isRequired,
  mongoDBNameValid: PropTypes.func.isRequired,
  mongoFormValid: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
});

export default MongoForm;
