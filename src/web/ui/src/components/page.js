import React from 'react';
import Spinner from 'react-bootstrap/Spinner';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import '../style/style.css';

function Page({ spinnerCondition, component }) {
  return (
    spinnerCondition
      ? (
        <div className="div-spinner-style">
          <Spinner
            animation="border"
            role="status"
            className="spinner-style"
          />
        </div>
      )
      : component
  );
}

Page.propTypes = forbidExtraProps({
  spinnerCondition: PropTypes.bool.isRequired,
  component: PropTypes.oneOfType([
    PropTypes.symbol, PropTypes.object,
  ]).isRequired,
});

export default Page;
