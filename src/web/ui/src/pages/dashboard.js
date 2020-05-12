import React, { Component } from 'react';
import Badge from 'react-bootstrap/Badge';
import Card from 'react-bootstrap/Card';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Row from 'react-bootstrap/Row';
import Tab from 'react-bootstrap/Tab';
import Table from 'react-bootstrap/Table';
import Tabs from 'react-bootstrap/Tabs';
import Spinner from 'react-bootstrap/Spinner';
import Tooltip from 'react-bootstrap/Tooltip';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import PropTypes from 'prop-types';
import { forbidExtraProps } from 'airbnb-prop-types';
import {
  ToastsContainer,
  ToastsContainerPosition,
  ToastsStore,
} from 'react-toasts';
import moment from 'moment';
import '../style/style.css';
import Blockchain from '../components/blockchain';
import Node from '../components/node';
import Monitor from '../components/monitor';
import { getAllChainInfo, getChainNames } from '../utils/data';
import { MONITOR_TYPES } from '../utils/constants';
import scaleToPico from '../utils/scaling';

moment.locale('en');
moment.updateLocale('en', {
  relativeTime: {
    future: 'just now',
    s: '%d seconds',
    ss: '%d seconds',
  },
});

// obtained from here: https://github.com/moment/moment/issues/1968
moment.relativeTimeThreshold('s', 59);
moment.relativeTimeThreshold('m', 60);
moment.relativeTimeThreshold('h', 24);
moment.relativeTimeThreshold('d', 28);
moment.relativeTimeThreshold('M', 12);
moment.relativeTimeThreshold('ss', 59);
moment.relativeTimeThreshold('mm', 60);
moment.relativeTimeThreshold('hh', 24);
moment.relativeTimeThreshold('dd', 28);
moment.relativeTimeThreshold('MM', 12);
moment.relativeTimeRounding(Math.floor);

function createChainDropDownItems(elements, activeChainIndex) {
  const items = [];
  for (let i = 0; i < elements.length; i += 1) {
    if (i !== activeChainIndex) {
      items.push(
        <NavDropdown.Item
          eventKey={i}
          className="navbar-item"
          key={elements[i]}
        >
          {elements[i]}
        </NavDropdown.Item>,
      );
    }
  }
  return items;
}

function createCard(title, data) {
  return (
    <Card className="cards-style" bg="light">
      <Card.Body>
        <Card.Title>{title}</Card.Title>
        <Card.Text>{data}</Card.Text>
      </Card.Body>
    </Card>
  );
}

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


function BlockchainDataGrid({ activeChain }) {
  const referendumCount = activeChain.referendumCount === -1
    ? 'N/a' : activeChain.referendumCount;
  const publicPropCount = activeChain.publicPropCount === -1
    ? 'N/a' : activeChain.publicPropCount;
  const councilPropCount = activeChain.councilPropCount === -1
    ? 'N/a' : activeChain.councilPropCount;
  const validatorSetSize = activeChain.validatorSetSize === -1
    ? 'N/a' : activeChain.validatorSetSize;
  return (
    <Container>
      <Row>
        <Col>
          {createCard('Total Referendums', referendumCount)}
        </Col>
        <Col>
          {createCard(
            'Total Public Proposals', publicPropCount,
          )}
        </Col>
        <Col>
          {createCard(
            'Total Council Proposals', councilPropCount,
          )}
        </Col>
        <Col>
          {createCard('Validator Set Size', validatorSetSize)}
        </Col>
      </Row>
    </Container>
  );
}

function createNodeTabs(nodes, activeChain) {
  const tabs = [];
  for (let i = 0; i < nodes.length; i += 1) {
    if (nodes[i].chain === activeChain.name) {
      tabs.push(
        <Tab eventKey={i} title={nodes[i].name} key={nodes[i].name}>
          <NodeContent node={nodes[i]} />
        </Tab>,
      );
    }
  }
  return tabs;
}

function NodeSelectionTabs({
  nodes, activeNodeIndex, activeChain, handleSelectNode,
}) {
  return (
    <Tabs
      id="nodes-tabs"
      activeKey={activeNodeIndex}
      onSelect={handleSelectNode}
      className="tabs-style"
    >
      {createNodeTabs(nodes, activeChain)}
    </Tabs>
  );
}

function NodeDataGrid({ node }) {
  const noOfPeers = node.noOfPeers === -1 ? 'N/a' : node.noOfPeers;
  const height = node.height === -1 ? 'N/a' : node.height;
  const bondedBalance = node.bondedBalance === -1
    ? 'N/a' : scaleToPico(node.bondedBalance);
  const noOfBlocksAuthored = node.noOfBlocksAuthored === -1
    ? 'N/a' : node.noOfBlocksAuthored;

  const content = [
    <Col key="Peers">{createCard('Peers', noOfPeers)}</Col>,
    <Col key="Height Update">
      {
        node.lastHeightUpdate === -1
          ? createCard('Finalized Height Update', 'no update')
          : (
            <OverlayTrigger
              placement="top"
              overlay={(
                <Tooltip id="tooltip-top">
                  {moment.unix(node.lastHeightUpdate).format(
                    'DD-MM-YYYY HH:mm:ss',
                  )
                  }
                </Tooltip>
                )}
            >
              { createCard('Finalized Height Update', moment.unix(
                node.lastHeightUpdate,
              ).fromNow())}
            </OverlayTrigger>
          )
      }
    </Col>,
    <Col key="Finalized Height">{createCard('Finalized Height', height)}</Col>,
  ];
  if (node.isDown) {
    content.push(
      <Col key="Down Since">
        <OverlayTrigger
          placement="top"
          overlay={(
            <Tooltip id="tooltip-top">
              {moment.unix(node.wentDownAt).format('DD-MM-YYYY HH:mm:ss')}
            </Tooltip>
            )}
        >
          {
            createCard('Down Since', moment.unix(node.wentDownAt).fromNow())
          }
        </OverlayTrigger>
      </Col>,
    );
  }

  if (node.isValidator) {
    content.push(
      <Col key="Blocks Authored">
        {createCard('Blocks Authored', noOfBlocksAuthored)}
      </Col>,
    );
    content.push(
      <Col key="Bonded Balance">
        {createCard('Bonded Balance', bondedBalance)}
      </Col>,
    );
  }

  return (
    <div>
      <Row>{content}</Row>
    </div>
  );
}

function NodeContent({ node }) {
  return (
    <div>
      <NodeDataGrid node={node} />
    </div>
  );
}

function MoreDetails({
  nodes, activeNodeIndex, activeChain, handleSelectNode,
}) {
  return (
    <div>
      <h1 className="heading-style-2">More Details</h1>
      <NodeSelectionTabs
        nodes={nodes}
        activeNodeIndex={activeNodeIndex}
        activeChain={activeChain}
        handleSelectNode={handleSelectNode}
      />
    </div>
  );
}

function createBadge(name, variant, key) {
  return (
    <Badge variant={variant} className="badges-style" key={key}>
      {name}
    </Badge>
  );
}

function NodeBadges(props) {
  const { node } = props;
  let syncingBadge = null;
  let activeBadge = null;
  let disabledBadge = null;
  let electedBadge = null;
  let councilMemberBadge = null;
  if (node.isSyncing !== -1) {
    syncingBadge = node.isSyncing
      ? createBadge('Syncing', 'warning', 'Syncing')
      : createBadge('Synced', 'success', 'Synced');
  }
  const badges = [
    node.isDown ? createBadge('Down', 'danger', 'Down')
      : createBadge('Up', 'success', 'Up'),
    syncingBadge,
  ];
  if (node.isValidator) {
    if (node.isActive !== -1) {
      activeBadge = node.isActive ? createBadge('Active', 'success', 'Active')
        : createBadge('Inactive', 'danger', 'Inactive');
    }
    if (node.isDisabled !== -1) {
      disabledBadge = node.isDisabled
        ? createBadge('Disabled', 'danger', 'Disabled')
        : createBadge('Enabled', 'success', 'Enabled');
    }
    if (node.isElected !== -1) {
      electedBadge = node.isElected
        ? createBadge('Elected', 'success', 'Elected')
        : createBadge('Not Elected', 'warning', 'Not Elected');
    }
    if (node.isCouncilMember !== -1) {
      councilMemberBadge = node.isCouncilMember
        && createBadge('Council Member', 'primary', 'Council Member');
    }
    badges.push(activeBadge, disabledBadge, electedBadge, councilMemberBadge);
  }
  return badges;
}

function NodesOverviewTableContent({ nodes, activeChain }) {
  const content = [];

  for (let i = 0; i < nodes.length; i += 1) {
    if (nodes[i].chain === activeChain.name) {
      content.push(
        <tr key={nodes[i].name}>
          <td>{nodes[i].name}</td>
          <td>
            <NodeBadges node={nodes[i]} />
          </td>
        </tr>,
      );
    }
  }
  return content;
}

function NodesOverviewTable({ nodes, activeChain }) {
  return (
    <Table responsive className="tables-style-3">
      <thead>
        <tr>
          <th>Node</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <NodesOverviewTableContent
          nodes={nodes}
          activeChain={activeChain}
        />
      </tbody>
    </Table>
  );
}

function NodesOverview({
  nodes, activeChain, activeNodeIndex, handleSelectNode,
}) {
  return (
    <Container>
      <h1 className="heading-style-1">Nodes Overview</h1>
      <NodesOverviewTable nodes={nodes} activeChain={activeChain} />
      <MoreDetails
        nodes={nodes}
        activeNodeIndex={activeNodeIndex}
        activeChain={activeChain}
        handleSelectNode={handleSelectNode}
      />
    </Container>
  );
}

function BlockchainStats({ activeChain }) {
  return (
    <div>
      <Container>
        <h1 className="heading-style-1">Blockchain Statistics</h1>
      </Container>
      <BlockchainDataGrid
        activeChain={activeChain}
      />
    </div>
  );
}

function MonitorsStatusTableContent({ monitors }) {
  const content = [];

  for (let i = 0; i < monitors.length; i += 1) {
    const monitor = monitors[i];
    content.push(
      <tr key={monitor.name}>
        <td>{monitor.name}</td>
        <td>{monitor.type}</td>
        {
          monitor.lastUpdate === -1
            ? <td className="time-style">no recent update</td>
            : (
              <OverlayTrigger
                placement="top"
                overlay={(
                  <Tooltip id="tooltip-top">
                    {moment.unix(monitor.lastUpdate).format(
                      'DD-MM-YYYY HH:mm:ss',
                    )}
                  </Tooltip>
                )}
              >
                <td className="time-style">
                  {moment.unix(monitor.lastUpdate).fromNow()}
                </td>
              </OverlayTrigger>
            )
          }
      </tr>,
    );
  }
  return content;
}

function MonitorsStatusTable({ monitors }) {
  return (
    <Table responsive className="tables-style-3">
      <thead>
        <tr>
          <th>Monitor</th>
          <th>Type</th>
          <th className="column-style">Last Update</th>
        </tr>
      </thead>
      <tbody>
        <MonitorsStatusTableContent monitors={monitors} />
      </tbody>
    </Table>
  );
}

function MonitorsStatus({ monitors }) {
  return (
    <Container>
      <h1 className="heading-style-1">Monitors Status</h1>
      <MonitorsStatusTable monitors={monitors} />
    </Container>
  );
}

class Dashboard extends Component {
  constructor(props) {
    super(props);
    this.dataTimer = null;
    this.clockTimer = null;
    this.state = {
      chainNames: [],
      activeChain: null,
      activeChainJson: {},
      isFetchingData: true,
      // By default select the first chain if there are chains
      activeChainIndex: 0,
      nodes: [],
      // By default select the first node of the active chain
      activeNodeIndex: 0,
      monitors: [],
      updateClock: false,
      redisErrorOnChainChange: false,
    };
  }

  componentDidMount() {
    const { state } = this;
    this.fetchData();
    this.dataTimer = setInterval(this.fetchData.bind(this), 5000);
    this.clockTimer = setInterval(() => this.setState({
      updateClock: !state.updateClock,
    }), 500);
  }

  componentWillUnmount() {
    clearInterval(this.dataTimer);
    clearInterval(this.clockTimer);
    this.dataTimer = null;
    this.clockTimer = null;
  }

  async fetchData() {
    const response = await this.fetchAlerterObjects();
    if (response === 0) {
      return 0;
    }
    return -1;
  }

  async fetchAlerterObjects() {
    const response = await this.fetchChains();
    if (response === 0) {
      this.fetchNodes();
      this.fetchMonitors();
      this.setState({ isFetchingData: false });
      return 0;
    }
    this.setState({ isFetchingData: false });
    return -1;
  }

  async fetchChains() {
    const { state } = this;
    let response;
    try {
      response = await getChainNames();
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        ToastsStore.error(`Error: ${e.response.data.error}`, 5000);
      } else {
        // Something happened in setting up the request that triggered an Error
        ToastsStore.error(`Error: ${e.message}`, 5000);
      }
      return -1;
    }
    const chainNames = response.data.result;
    // If chainNames is empty, the config is deleted/emptied/not filled yet.
    // Therefore, no new data to display, hence return. If dashboard data is
    // already loaded, give an error message to the user.
    if (chainNames.length === 0) {
      if (state.chainNames.length !== 0) {
        ToastsStore.error('The user_config_nodes.ini file must be '
          + 'mis-configured as PANIC has no blockchains/nodes to '
          + 'monitor. Please solve this using the Settings->Nodes page and '
          + '(re)start PANIC if you want to continue using the dashboard',
        5000);
      }
      return -1;
    }
    const { activeChainIndex } = state;
    const activeChainName = chainNames[activeChainIndex];
    try {
      response = await getAllChainInfo(activeChainName);
    } catch (e) {
      if (state.chainNames.length !== 0) {
        if (e.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          ToastsStore.error(`Error: ${e.response.data.error}`, 5000);
        } else {
          // Something happened in setting up the request that triggered an
          // error
          ToastsStore.error(`Error: ${e.message}`, 5000);
        }
      }
      return -1;
    }
    const chainInfo = response.data.result;
    const referendumCount = chainInfo.blockchain.referendum_count === null
    || chainInfo.blockchain.referendum_count === 'None'
      ? -1 : parseInt(chainInfo.blockchain.referendum_count, 10);
    const publicPropCount = chainInfo.blockchain.public_prop_count === null
    || chainInfo.blockchain.public_prop_count === 'None'
      ? -1 : parseInt(chainInfo.blockchain.public_prop_count, 10);
    const councilPropCount = chainInfo.blockchain.council_prop_count === null
    || chainInfo.blockchain.council_prop_count === 'None'
      ? -1 : parseInt(chainInfo.blockchain.council_prop_count, 10);
    const validatorSetSize = chainInfo.blockchain.validator_set_size === null
    || chainInfo.blockchain.validator_set_size === 'None'
      ? -1 : parseInt(chainInfo.blockchain.validator_set_size, 10);
    this.setState({
      chainNames,
      activeChain: new Blockchain(activeChainName, referendumCount,
        publicPropCount, councilPropCount, validatorSetSize),
      activeChainJson: chainInfo,
      redisErrorOnChainChange: false,
    });
    return 0;
  }

  fetchNodes() {
    const { state } = this;
    const nodes = [];
    const nodesJson = state.activeChainJson.nodes;
    Object.entries(nodesJson).forEach(([node, data]) => {
      const chain = state.activeChain.name;
      const isDown = data.went_down_at === null ? false
        : data.went_down_at !== 'None';
      const isValidator = data.is_validator === null ? -1
        : data.is_validator.toLowerCase() === 'true';
      const wentDownAt = data.went_down_at === null ? -1
        : parseFloat(data.went_down_at);
      const isSyncing = data.is_syncing === null ? -1
        : data.is_syncing.toLowerCase() === 'true';
      const noOfPeers = data.no_of_peers === null
      || data.no_of_peers === 'None' ? -1 : parseInt(data.no_of_peers, 10);
      const timeOfLastHeightChange = data.time_of_last_height_change === null
        ? -1 : parseFloat(data.time_of_last_height_change);
      const finalizedBlockHeight = data.finalized_block_height === null ? -1
        : parseInt(data.finalized_block_height, 10);
      const bondedBalance = data.bonded_balance === null
      || data.bonded_balance === 'None' ? -1
        : parseInt(data.bonded_balance, 10);
      const active = data.active === null || data.active === 'None' ? -1
        : data.active.toLowerCase() === 'true';
      const disabled = data.disabled === null || data.disabled === 'None' ? -1
        : data.disabled.toLowerCase() === 'true';
      const elected = data.elected === null || data.elected === 'None' ? -1
        : data.elected.toLowerCase() === 'true';
      const councilMember = data.council_member === null
      || data.council_member === 'None' ? -1
        : data.council_member.toLowerCase() === 'true';
      const noOfBlocksAuthored = data.noOfBlocksAuthored === null ? -1
        : parseInt(data.no_of_blocks_authored, 10);

      nodes.push(
        new Node(node, chain, isValidator, wentDownAt, isDown, isSyncing,
          noOfPeers, timeOfLastHeightChange, finalizedBlockHeight,
          bondedBalance, active, disabled, elected, councilMember,
          noOfBlocksAuthored),
      );
    });
    this.setState({ nodes });
  }

  fetchMonitors() {
    const { state } = this;
    const monitors = [];
    const nodeMonitorsJson = state.activeChainJson.monitors.node;
    const blockchainMonitorsJson = state.activeChainJson.monitors.blockchain;
    Object.entries(nodeMonitorsJson).forEach(([monitor, data]) => {
      const chain = state.activeChain.name;
      const monitorName = `${monitor}`;
      const lastUpdate = data.alive === null ? -1 : parseFloat(data.alive);
      monitors.push(new Monitor(
        monitorName, chain, lastUpdate, MONITOR_TYPES.node_monitor,
      ));
    });
    Object.entries(blockchainMonitorsJson).forEach(([monitor, data]) => {
      const chain = state.chainNames[state.activeChainIndex];
      const monitorName = `${monitor}`;
      const lastUpdate = data.alive === null ? -1 : parseFloat(data.alive);
      monitors.push(new Monitor(
        monitorName, chain, lastUpdate, MONITOR_TYPES.blockchain_monitor,
      ));
    });
    this.setState({ monitors });
  }

  handleSelectChain(selectedChain) {
    // This must be done because the 'selectedChain' value is passed as string.
    const selectedChainParsed = parseInt(selectedChain, 10);

    // Set the active node to the first node of the selected chain
    this.setState({
      isFetchingData: true,
      activeChainIndex: selectedChainParsed,
      activeNodeIndex: 0,
    }, async () => {
      const response = await this.fetchData();
      if (response === -1) {
        this.setState({ redisErrorOnChainChange: true });
      }
    });
  }

  handleSelectNode(selectedNode) {
    this.setState({ activeNodeIndex: parseInt(selectedNode, 10) });
  }

  render() {
    const { state } = this;
    return (
      <div>
        {state.isFetchingData || state.redisErrorOnChainChange
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
            <div>
              {state.chainNames.length > 0
                ? (
                  <div>
                    <ChainsDropDown
                      chainNames={state.chainNames}
                      activeChainIndex={state.activeChainIndex}
                      handleSelectChain={chain => this.handleSelectChain(chain)}
                    />
                    {Object.keys(state.activeChainJson.monitors.blockchain)
                      .length > 0 && (
                        <BlockchainStats
                          activeChain={state.activeChain}
                        />
                    )
                    }
                    { state.nodes.length > 0
                    && (
                    <NodesOverview
                      nodes={state.nodes}
                      activeChain={state.activeChain}
                      activeNodeIndex={state.activeNodeIndex}
                      handleSelectNode={node => this.handleSelectNode(node)}
                    />
                    )
                    }
                    <MonitorsStatus monitors={state.monitors} />
                  </div>
                )
                : (
                  <Container
                    className="my-auto text-center error d-flex
                    align-items-center"
                  >
                    <Row className="m-auto justify-content-center
                    align-items-center"
                    >
                      <Col xs="auto">
                        <p className="lead">
                          The nodes&apos; user config or Redis must be
                          mis-configured. Please set up PANIC and Redis using
                          the Settings pages and do not forget to (re)start
                          PANIC afterwards! Also please make sure that Redis is
                          running.
                        </p>
                      </Col>
                    </Row>
                  </Container>
                )
              }
            </div>
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

// TODO: Need to organize code in sections, components etc.. example folder
//      dashboard. Chain info must also have component on its own with its
//      heading like others. Copy format like last two sections.

const blockchainType = PropTypes.shape({
  name: PropTypes.string,
  referendumCount: PropTypes.number,
  publicPropCount: PropTypes.number,
  councilPropCount: PropTypes.number,
  validatorSetSize: PropTypes.number,
});

const nodeType = PropTypes.shape({
  name: PropTypes.string,
  chain: PropTypes.string,
  isValidator: PropTypes.bool,
  wentDownAt: PropTypes.number,
  isDown: PropTypes.bool,
  isSyncing: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  noOfPeers: PropTypes.number,
  lastHeightUpdate: PropTypes.number,
  height: PropTypes.number,
  bondedBalance: PropTypes.number,
  isActive: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  isDisabled: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  isElected: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  isCouncilMember: PropTypes.oneOfType([PropTypes.number, PropTypes.bool]),
  noOfBlocksAuthored: PropTypes.number,
});

const monitorType = PropTypes.shape({
  name: PropTypes.string,
  chain: PropTypes.string,
  lastUpdate: PropTypes.number,
});

ChainsDropDown.propTypes = forbidExtraProps({
  chainNames: PropTypes.arrayOf(PropTypes.string).isRequired,
  activeChainIndex: PropTypes.number.isRequired,
  handleSelectChain: PropTypes.func.isRequired,
});

BlockchainDataGrid.propTypes = forbidExtraProps({
  activeChain: blockchainType.isRequired,
});

NodeSelectionTabs.propTypes = forbidExtraProps({
  nodes: PropTypes.arrayOf(nodeType).isRequired,
  activeNodeIndex: PropTypes.number.isRequired,
  activeChain: blockchainType.isRequired,
  handleSelectNode: PropTypes.func.isRequired,
});

NodeDataGrid.propTypes = forbidExtraProps({
  node: nodeType.isRequired,
});

NodeContent.propTypes = forbidExtraProps({
  node: nodeType.isRequired,
});

MoreDetails.propTypes = forbidExtraProps({
  nodes: PropTypes.arrayOf(nodeType).isRequired,
  activeNodeIndex: PropTypes.number.isRequired,
  activeChain: blockchainType.isRequired,
  handleSelectNode: PropTypes.func.isRequired,
});

NodesOverviewTable.propTypes = forbidExtraProps({
  nodes: PropTypes.arrayOf(nodeType).isRequired,
  activeChain: blockchainType.isRequired,
});

NodesOverview.propTypes = forbidExtraProps({
  nodes: PropTypes.arrayOf(nodeType).isRequired,
  activeNodeIndex: PropTypes.number.isRequired,
  activeChain: blockchainType.isRequired,
  handleSelectNode: PropTypes.func.isRequired,
});

BlockchainStats.propTypes = forbidExtraProps({
  activeChain: blockchainType.isRequired,
});

MonitorsStatusTable.propTypes = forbidExtraProps({
  monitors: PropTypes.arrayOf(monitorType).isRequired,
});

MonitorsStatus.propTypes = forbidExtraProps({
  monitors: PropTypes.arrayOf(monitorType).isRequired,
});

export default Dashboard;
