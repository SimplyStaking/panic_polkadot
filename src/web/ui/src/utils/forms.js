import React from 'react';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheck } from '@fortawesome/free-solid-svg-icons/faCheck';
import { faTimes } from '@fortawesome/free-solid-svg-icons/faTimes';
import { fieldEmpty } from './configs';
import { toBool } from './string';
import '../style/style.css';

function createColumnFormContentWithSubmit(
  labels, columns, onSubmit, buttonName,
) {
  const form = [];
  for (let i = 0; i < labels.length; i += 1) {
    form.push(
      <Form.Group as={Row} key={i} controlId={i}>
        {labels[i]}
        {columns[i]}
      </Form.Group>,
    );
  }

  return (
    <Form onSubmit={onSubmit}>
      {form}
      <div className="div-content-centre-style">
        <Button className="button-style2" type="submit">
          {buttonName}
        </Button>
      </div>
    </Form>
  );
}

function createColumnForm(labels, columns) {
  const form = [];

  for (let i = 0; i < labels.length; i += 1) {
    form.push(
      <Form.Group as={Row} key={i}>
        {labels[i]}
        {columns[i]}
      </Form.Group>,
    );
  }
  return <Form onSubmit={(e) => { e.preventDefault(); }}>{form}</Form>;
}

function generateAddedTableValues(savedValue, isBoolean) {
  if (isBoolean) {
    return (
      <td className="column-style">
        {
          toBool(savedValue) ? (
            <FontAwesomeIcon icon={faCheck} color="green" />
          ) : (
            <FontAwesomeIcon icon={faTimes} color="red" />
          )
        }
      </td>
    );
  }

  return fieldEmpty(savedValue) ? <td>N/a</td> : <td>{savedValue}</td>;
}

// sm represents the total number of columns to take
function createFormLabel(column, sm, label) {
  return <Form.Label column={column} sm={sm}>{label}</Form.Label>;
}

function createColumnWithContent(sm, content, key) {
  return <Col sm={sm} key={key}>{content}</Col>;
}

export {
  createColumnFormContentWithSubmit, generateAddedTableValues,
  createColumnForm, createColumnWithContent, createFormLabel,
};
