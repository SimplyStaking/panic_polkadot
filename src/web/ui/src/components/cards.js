import React from 'react';
import Card from 'react-bootstrap/Card';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import '../style/style.css';

function DataCard({ title, data }) {
  return (
    <Card className="cards-style" bg="light">
      <Card.Body>
        <Card.Title>{title}</Card.Title>
        <Card.Text>{data}</Card.Text>
      </Card.Body>
    </Card>
  );
}

DataCard.propTypes = forbidExtraProps({
  title: PropTypes.string.isRequired,
  data: PropTypes.oneOfType([
    PropTypes.number, PropTypes.bool, PropTypes.string,
  ]).isRequired,
});

export default DataCard;
