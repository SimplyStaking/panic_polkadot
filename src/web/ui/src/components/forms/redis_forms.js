import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import {
  createColumnForm, createColumnWithContent, createFormLabel,
} from '../../utils/forms';
import { toBool } from '../../utils/string';
import { fieldEmpty } from '../../utils/configs';
import { CollapsibleForm, Trigger } from './collapsible_form';
import TooltipOverlay from '../overlays';
import { ConnectWithRedisButton } from '../buttons';
import '../../style/style.css';

function RedisForm({
  mainUserConfigJson, validated, redisHostValid, redisPortValid, redisFormValid,
  handleChangeInNonBooleanField, handleChangeInBooleanField,
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
          onChange={
            event => handleChangeInBooleanField(event, 'redis', 'enabled')
          }
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
            onChange={
              event => handleChangeInNonBooleanField(event, 'redis', 'host')
            }
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
          <TooltipOverlay
            identifier="Redis-host-ip"
            placement="right"
            tooltipText={'The IP of the Redis server. If you will be running '
            + 'PANIC using Docker, do not use \'localhost\', instead use the '
            + 'full IP address (local or external) of the machine that the '
            + 'Redis container will be running on.'}
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
            placeholder="6379"
            disabled={!toBool(mainUserConfigJson.redis.enabled)}
            onChange={
              event => handleChangeInNonBooleanField(event, 'redis', 'port')
            }
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
          <TooltipOverlay
            identifier="Redis-host-port"
            placement="right"
            tooltipText={'The port of the Redis server. If you will be running '
            + 'PANIC using Docker, you should leave the port as 6379. If you '
            + 'wish to run the Redis container on another port, please input '
            + 'this port number here and change the \'REDIS_HOST_PORT\' value '
            + 'inside the \'panic_polkadot/.env\' file.'}
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
            type="password"
            disabled={!toBool(mainUserConfigJson.redis.enabled)}
            onChange={
              event => handleChangeInNonBooleanField(event, 'redis', 'password')
            }
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
          <TooltipOverlay
            identifier="Redis-password"
            placement="right"
            tooltipText={'Redis authentication password. Leave blank if no '
            + 'authentication was set up.'}
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
              <ConnectWithRedisButton
                disabled={!toBool(mainUserConfigJson.redis.enabled)
                || !redisFormValid()}
                host={mainUserConfigJson.redis.host}
                port={mainUserConfigJson.redis.port}
                password={mainUserConfigJson.redis.password}
              />
            </div>
          </div>
        )}
      />
    </div>
  );
}

RedisForm.propTypes = forbidExtraProps({
  mainUserConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  validated: PropTypes.bool.isRequired,
  redisHostValid: PropTypes.func.isRequired,
  redisPortValid: PropTypes.func.isRequired,
  redisFormValid: PropTypes.func.isRequired,
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
  handleChangeInBooleanField: PropTypes.func.isRequired,
});

export default RedisForm;
