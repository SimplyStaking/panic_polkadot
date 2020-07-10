import React from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import NavDropdown from 'react-bootstrap/NavDropdown';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { createChainDropDownItems } from '../utils/dashboard';

function ChainsDropDown({ chainNames, activeChainIndex, handleSelectChain }) {
  return (
    <Navbar collapseOnSelect expand="lg" variant="light" bg="light">
      <Container>
        <Nav activeKey={activeChainIndex} onSelect={handleSelectChain}>
          <NavDropdown title={chainNames[activeChainIndex]} id="chain-nav">
            {createChainDropDownItems(chainNames, activeChainIndex)}
          </NavDropdown>
        </Nav>
      </Container>
    </Navbar>
  );
}

ChainsDropDown.propTypes = forbidExtraProps({
  chainNames: PropTypes.arrayOf(PropTypes.string).isRequired,
  activeChainIndex: PropTypes.number.isRequired,
  handleSelectChain: PropTypes.func.isRequired,
});

export default ChainsDropDown;
