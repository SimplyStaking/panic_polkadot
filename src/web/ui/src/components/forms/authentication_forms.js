import React from 'react';
import Form from 'react-bootstrap/Form';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import {
  createColumnForm,
  createColumnWithContent,
  createFormLabel,
} from '../../utils/forms';
import { LoginButton } from '../buttons';
import { CollapsibleForm, Trigger } from './collapsible_form';
import '../../style/style.css';

function AuthenticationForm({
  handleChangeInNonBooleanField, credentials, setAuthentication,
  credentialsValid, validated, handleSetValidated, handleSetCredentialsValid,
}) {
  const labels = [
    createFormLabel(true, '3', 'Username'),
    createFormLabel(true, '3', 'Password'),
  ];
  const columns = [
    createColumnWithContent(
      '5',
      <div>
        <Form.Control
          type="text"
          onChange={event => handleChangeInNonBooleanField(event, 'username')}
          value={credentials.username}
          isValid={validated && credentialsValid}
          isInvalid={validated && !credentialsValid}
        />
      </div>,
      1,
    ),
    createColumnWithContent(
      '5',
      <div>
        <Form.Control
          type="password"
          onChange={event => handleChangeInNonBooleanField(event, 'password')}
          value={credentials.password}
          isValid={validated && credentialsValid}
          isInvalid={validated && !credentialsValid}
        />
        <Form.Control.Feedback>
          Authentication details are correct!
        </Form.Control.Feedback>
        <Form.Control.Feedback type="invalid">
          Your username or password must be incorrect.
        </Form.Control.Feedback>
      </div>,
      2,
    ),
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(<Trigger name="Login" />)}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        triggerDisabled
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              {'Please input the authentication credentials you have set for '
              + 'the UI. If you have not set them up yet, the UI server has '
              + 'set up a default random password which you can access from '
              + 'the console. However, we suggest you set up your own username '
              + 'and password as described in the doc. Do not forget to '
              + 'restart the UI server afterwards!'}
            </Form.Text>
            {createColumnForm(labels, columns)}
            <div className="div-content-centre-style">
              <LoginButton
                credentials={credentials}
                setAuthentication={setAuthentication}
                handleSetCredentialsValid={handleSetCredentialsValid}
                handleSetValidated={handleSetValidated}
              />
            </div>
          </div>
        )}
      />
    </div>
  );
}

AuthenticationForm.propTypes = forbidExtraProps({
  handleChangeInNonBooleanField: PropTypes.func.isRequired,
  credentials: PropTypes.shape({
    username: PropTypes.string,
    password: PropTypes.string,
  }).isRequired,
  setAuthentication: PropTypes.func.isRequired,
  handleSetValidated: PropTypes.func.isRequired,
  handleSetCredentialsValid: PropTypes.func.isRequired,
  credentialsValid: PropTypes.bool.isRequired,
  validated: PropTypes.bool.isRequired,
});

export default AuthenticationForm;
