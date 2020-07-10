import React, { Component } from 'react';
import Container from 'react-bootstrap/Container';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import '../style/style.css';
import AuthenticationForm from '../components/forms/authentication_forms';

class AuthenticationPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      credentials: { username: '', password: '' },
      validated: false,
      credentialsValid: true,
    };
  }

  handleChangeInNonBooleanField(event, field) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newCredentials = prevState.credentials;
      newCredentials[field] = event.target.value;
      return { credentials: newCredentials };
    });
  }

  handleSetValidated(validated) {
    this.setState({ validated });
  }

  handleSetCredentialsValid(credentialsValid) {
    this.setState({ credentialsValid });
  }

  render() {
    const { state } = this;
    const { props } = this;
    return (
      <Container>
        <AuthenticationForm
          handleChangeInNonBooleanField={
            (event, field) => {
              this.handleChangeInNonBooleanField(event, field);
            }
          }
          handleSetValidated={
            (validated) => { this.handleSetValidated(validated); }
          }
          handleSetCredentialsValid={
            (credentialsValid) => {
              this.handleSetCredentialsValid(credentialsValid);
            }
          }
          credentials={state.credentials}
          setAuthentication={props.setAuthentication}
          validated={state.validated}
          credentialsValid={state.credentialsValid}
        />
      </Container>
    );
  }
}

AuthenticationPage.propTypes = forbidExtraProps({
  setAuthentication: PropTypes.func.isRequired,
});

export default AuthenticationPage;
