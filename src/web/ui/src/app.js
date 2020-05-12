import React from 'react';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Row from 'react-bootstrap/Row';
import Routes from './routing/routes';
import './style/style.css';

function NavigationTab() {
  return (
    <header>
      <Navbar
        collapseOnSelect
        expand="lg"
        variant="dark"
        className="navbar-header"
      >
        <Container className="align-items-end">
          <Navbar.Brand href="/">PANIC</Navbar.Brand>
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="ml-auto">
              <Nav.Link href="/">Dashboard</Nav.Link>
              <NavDropdown title="Alerts" id="alerts-nav-dropdown">
                <NavDropdown.Item href="/alerts/logs" className="navbar-item">
                  Logs
                </NavDropdown.Item>
                <NavDropdown.Item
                  href="/alerts/preferences"
                  className="navbar-item"
                >
                  Preferences
                </NavDropdown.Item>
              </NavDropdown>
              <NavDropdown title="Settings" id="settings-nav-dropdown">
                <NavDropdown.Item href="/settings/main" className="navbar-item">
                  Main
                </NavDropdown.Item>
                <NavDropdown.Item
                  href="/settings/nodes"
                  className="navbar-item"
                >
                  Nodes
                </NavDropdown.Item>
                <NavDropdown.Item
                  href="/settings/repositories"
                  className="navbar-item"
                >
                  Repos
                </NavDropdown.Item>
              </NavDropdown>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>
      <Routes />
    </header>
  );
}

function FooterBanner() {
  return (
    <footer className="footer-style">
      <Container className="py-3">
        <Row className="align-items-center justify-content-between">
          <Col xs="auto" className="align-self-start">
            <a
              className="link-style footer-style"
              href="https://simply-vc.com.mt"
              target="blank"
            >
              Powered by Simply VC
            </a>
          </Col>
        </Row>
      </Container>
    </footer>

  );
}

function App() {
  return (
    <div className="page-container">
      <div className="content-wrap">
        <NavigationTab />
      </div>
      <FooterBanner />
    </div>
  );
}

export default App;
