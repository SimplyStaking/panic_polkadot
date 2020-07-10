import React, { Component } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { DEFAULT_ERROR } from '../utils/error';
import '../style/style.css';

class ErrorPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      error: props.err,
    };
  }

  render() {
    const { error } = this.state;
    return (
      <Container
        className="my-auto text-center error d-flex align-items-center"
      >
        <Row className="m-auto justify-content-center align-items-center">
          <Col xs="auto" className="border-right text-right">
            <h1>{error.code}</h1>
          </Col>
          <Col xs="auto">
            <p className="lead">{error.message}</p>
          </Col>
        </Row>
      </Container>
    );
  }
}

ErrorPage.propTypes = forbidExtraProps({
  err: PropTypes.shape({ code: PropTypes.number, message: PropTypes.string }),
});

ErrorPage.defaultProps = {
  err: DEFAULT_ERROR,
};

export default ErrorPage;
