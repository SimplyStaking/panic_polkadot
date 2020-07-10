import React, { Component } from 'react';
import Spinner from 'react-bootstrap/Spinner';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import {
  ToastsContainer, ToastsContainerPosition, ToastsStore,
} from 'react-toasts';
import {
  FooterBanner, HeaderNavigationBar,
} from './components/layout';
import { getAuthenticationStatus } from './utils/data';
import './style/style.css';

function App({ isAuthenticated, setAuthentication }) {
  return (
    <div className="page-container">
      <div className="content-wrap">
        <HeaderNavigationBar
          brand="PANIC"
          isAuthenticated={isAuthenticated}
          setAuthentication={setAuthentication}
        />
      </div>
      <FooterBanner
        text="Developed by Simply VC"
        href="https://simply-vc.com.mt"
      />
    </div>
  );
}

class AppLauncher extends Component {
  constructor(props) {
    super(props);
    // We need to set a timer that checks the authentication status. If the
    // password changes, the user is immediately logged out after 5 seconds.
    this.dataTimer = null;
    this.state = {
      isAuthenticated: false,
      isFetchingData: true,
    };
  }

  componentDidMount() {
    this.testAndSetAuthentication();
    this.dataTimer = setInterval(
      this.testAndSetAuthentication.bind(this), 5000,
    );
  }

  componentWillUnmount() {
    clearInterval(this.dataTimer);
    this.dataTimer = null;
  }

  setAuthentication(auth) {
    this.setState({
      isAuthenticated: auth,
    });
  }

  async testAndSetAuthentication() {
    try {
      const res = await getAuthenticationStatus();
      this.setState({
        isAuthenticated: res.data.result.authenticated, isFetchingData: false,
      });
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code that
        // falls out of the range of 2xx
        ToastsStore.error(
          `Could not get authentication status. Error: ${
            e.response.data.error}`, 5000,
        );
      } else {
        // Something happened in setting up the request that triggered an Error
        ToastsStore.error(
          `Could not get authentication status. Error: ${e.message}`, 5000,
        );
      }
    }
  }

  render() {
    const { state } = this;
    return (
      <div>
        {
        state.isFetchingData
          ? (
            <div className="div-spinner-style">
              <Spinner
                animation="border"
                role="status"
                className="spinner-style"
              />
            </div>
          )
          : (
            <App
              isAuthenticated={state.isAuthenticated}
              setAuthentication={auth => this.setAuthentication(auth)}
            />
          )
      }
        <ToastsContainer
          store={ToastsStore}
          position={ToastsContainerPosition.TOP_CENTER}
          lightBackground
        />
      </div>
    );
  }
}

App.propTypes = forbidExtraProps({
  isAuthenticated: PropTypes.bool.isRequired,
  setAuthentication: PropTypes.func.isRequired,
});

export default AppLauncher;
