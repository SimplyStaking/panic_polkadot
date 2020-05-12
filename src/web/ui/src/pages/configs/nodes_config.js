import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Table from 'react-bootstrap/Table';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Tooltip from 'react-bootstrap/Tooltip';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import Spinner from 'react-bootstrap/Spinner';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { faCheck } from '@fortawesome/free-solid-svg-icons/faCheck';
import { faInfoCircle } from '@fortawesome/free-solid-svg-icons/faInfoCircle';
import { faTimes } from '@fortawesome/free-solid-svg-icons/faTimes';
import { faTimesCircle } from '@fortawesome/free-solid-svg-icons/faTimesCircle';
import {
  ToastsContainer,
  ToastsContainerPosition,
  ToastsStore,
} from 'react-toasts';
import '../../style/style.css';
import {
  CollapsibleForm,
  createColumnWithContent,
  createFormLabel,
  Trigger,
} from './main_user_config';
import {
  getConfig,
  pingNode,
  sendConfig,
} from '../../utils/data';
import { nodeConfig } from '../../utils/templates';
import { toBool } from '../../utils/string';
import {
  fieldEmpty,
  fieldValueUniqueAmongAllfieldsInJSON,
  fixSpecificSectionsOfConfig,
  highestItemIndexInConfig,
  keepSpecificSectionsFromConfig,
} from '../../utils/configs';

function createColumnFormWithSubmit(labels, columns, onSubmit, buttonName) {
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

function AddNodeForm({
  currentNodeConfig, handleChangeInNodeName, handleChangeInChainName,
  handleChangeInWsUrl, handleChangeInNodeType, handleChangeInStashAddress,
  handleChangeInMonitorNodeStatus, handleChangeInDataSourceStatus,
  handleChangeInArchiveStatus, handleAddNode, currentNodeIndex,
  validated, nodeNameValid, chainNameValid, wsUrlValid, stashValid,
}) {
  const labels = [
    createFormLabel(true, '3', 'Name'),
    createFormLabel(true, '3', 'Chain'),
    createFormLabel(true, '3', 'Web Socket URL'),
    createFormLabel(true, '3', 'Is a validator'),
    createFormLabel(true, '3', 'Stash account address'),
    createFormLabel(true, '3', 'Monitor node'),
    createFormLabel(true, '3', 'Use as data source'),
    createFormLabel(true, '3', 'Is archive'),
  ];
  const columns = [
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            onChange={event => handleChangeInNodeName(event)}
            placeholder={`node_${currentNodeIndex}`}
            value={currentNodeConfig.node_name}
            isInvalid={validated && !nodeNameValid()}
            isValid={validated && nodeNameValid()}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          {fieldEmpty(currentNodeConfig.node_name)
            ? (
              <Form.Control.Feedback type="invalid">
                Node name cannot be empty!
              </Form.Control.Feedback>
            )
            : (
              <Form.Control.Feedback type="invalid">
                Node names must be unique
              </Form.Control.Feedback>
            )}
        </div>,
        1,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="stash-overlay"
            placement="right"
            overlay={(
              <Tooltip id="stash-tooltip">Node names must be unique</Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        2,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            onChange={event => handleChangeInChainName(event)}
            placeholder="Kusama"
            value={currentNodeConfig.chain_name}
            isInvalid={validated && !chainNameValid()}
            isValid={validated && chainNameValid()}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Chain name cannot be empty!
          </Form.Control.Feedback>
        </div>,
        3,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="stash-overlay"
            placement="right"
            overlay={(
              <Tooltip id="stash-tooltip">Chain that node runs on</Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        4,
      ),
    ],
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            onChange={event => handleChangeInWsUrl(event)}
            placeholder="ws://NODE_IP:9944"
            isInvalid={validated && !wsUrlValid()}
            isValid={validated && wsUrlValid()}
            value={currentNodeConfig.node_ws_url}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Web Socket URL cannot be empty!
          </Form.Control.Feedback>
        </div>,
        5,
      ),
      createColumnWithContent(
        '4',
        <div>
          <Button
            className="button-style2"
            disabled={!wsUrlValid()}
            onClick={async () => {
              try {
                ToastsStore.info(`Pinging node ${
                  currentNodeConfig.node_ws_url
                }`, 5000);
                await pingNode(currentNodeConfig.node_ws_url);
                ToastsStore.success('Ping successful', 5000);
              } catch (e) {
                if (e.response) {
                  // The request was made and the server responded
                  // with a status code that falls out of the
                  // range of 2xx
                  ToastsStore.error(
                    `Ping request failed. Error: ${e.response.data.error}`,
                    5000,
                  );
                } else {
                  // Something happened in setting up the request
                  // that triggered an Error
                  ToastsStore.error(
                    `Ping request failed. Error: ${e.message}`, 5000,
                  );
                }
              }
            }
            }
          >
            Test via API
          </Button>
        </div>,
        6,
      ),
    ],
    createColumnWithContent(
      '2',
      <div>
        <div style={{ display: 'inline-block' }}>
          <Form.Check
            type="checkbox"
            id="is-validator-check-box"
            aria-label="checkbox"
            className="checkbox-style"
            onChange={() => handleChangeInNodeType()}
            checked={toBool(currentNodeConfig.node_is_validator)}
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <OverlayTrigger
            key="is-validator-overlay"
            placement="right"
            overlay={(
              <Tooltip id="is-validator-tooltip">
                Tick box if your node is a validator.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>
      </div>,
      7,
    ),
    [
      createColumnWithContent(
        '5',
        <div>
          <Form.Control
            type="text"
            disabled={!toBool(currentNodeConfig.node_is_validator)}
            onChange={event => handleChangeInStashAddress(event)}
            placeholder="Jg7lsfddsfsdhDGSDHFDsGsHGADGDSGSDgdsgsdgdsgds5A"
            value={currentNodeConfig.stash_account_address}
            // Only show feedback in the case of validators
            isInvalid={validated && !stashValid()
            && toBool(currentNodeConfig.node_is_validator)}
            isValid={validated && stashValid()
            && toBool(currentNodeConfig.node_is_validator)}
          />
          <Form.Control.Feedback>Looks good!</Form.Control.Feedback>
          <Form.Control.Feedback type="invalid">
            Stash account address must be non-empty for validators!
          </Form.Control.Feedback>
        </div>,
        8,
      ),
      createColumnWithContent(
        '1',
        <div className="info-tooltip-div-style">
          <OverlayTrigger
            key="stash-overlay"
            placement="right"
            overlay={(
              <Tooltip id="stash-tooltip">Only for validators.</Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>,
        9,
      ),
    ],
    createColumnWithContent(
      '2',
      <div>
        <div style={{ display: 'inline-block' }}>
          <Form.Check
            type="checkbox"
            id="monitor-node-check-box"
            aria-label="checkbox"
            className="checkbox-style"
            onChange={() => handleChangeInMonitorNodeStatus()}
            checked={toBool(currentNodeConfig.monitor_node)}
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <OverlayTrigger
            key="monitor-node-overlay"
            placement="right"
            overlay={(
              <Tooltip id="monitor-node-tooltip">
                Tick if you would like your node to be node monitored.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>
      </div>,
      10,
    ),
    createColumnWithContent(
      '2',
      <div>
        <div style={{ display: 'inline-block' }}>
          <Form.Check
            type="checkbox"
            id="data-source-check-box"
            aria-label="checkbox"
            className="checkbox-style"
            onChange={() => handleChangeInDataSourceStatus()}
            checked={toBool(currentNodeConfig.use_as_data_source)}
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <OverlayTrigger
            key="data-source-overlay"
            placement="right"
            overlay={(
              <Tooltip id="data-source-tooltip">
                Tick if you would like your node to be used as data source for
                indirect monitoring
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>
      </div>,
      11,
    ),
    createColumnWithContent(
      '2',
      <div>
        <div style={{ display: 'inline-block' }}>
          <Form.Check
            type="checkbox"
            id="is-archive-check-box"
            aria-label="checkbox"
            className="checkbox-style"
            disabled={!toBool(currentNodeConfig.use_as_data_source)}
            onChange={() => handleChangeInArchiveStatus()}
            checked={toBool(currentNodeConfig.is_archive_node)}
          />
        </div>
        <div
          className="info-tooltip-div-style2"
          style={{ display: 'inline-block' }}
        >
          <OverlayTrigger
            key="is-archive-overlay"
            placement="right"
            overlay={(
              <Tooltip id="is-archive-tooltip">
                Tick if your node is an archive node and you would like it to be
                a data source for archive monitoring. Available only if the
                &apos;Use as data source&apos; field is ticked.
              </Tooltip>
            )}
          >
            <FontAwesomeIcon icon={faInfoCircle} />
          </OverlayTrigger>
        </div>
      </div>,
      12,
    ),
  ];
  return (
    <div className="div-style">
      <CollapsibleForm
        trigger={(<Trigger name="Node" />)}
        triggerClassName="collapsible-style"
        triggerOpenedClassName="collapsible-style"
        open
        content={(
          <div>
            <Form.Text className="text-muted info-div-style">
              You may include nodes from multiple Substrate chains in any order,
              PANIC will group them automatically. Please make sure that the API
              Server is setup and running at the provided IP with
              <strong> ALL</strong>
              {' '}
              desired nodes before proceeding further. Also, please first set-up
              PANIC using the Settings-&gt;Main page before proceeding any
              further, otherwise, this setup page would not know where the API
              is running.
            </Form.Text>
            {createColumnFormWithSubmit(
              labels, columns, handleAddNode, 'Add Node',
            )}
          </div>
        )}
      />
    </div>
  );
}

function NodesConfigForm({
  handleAddNode, handleChangeInNodeName, handleChangeInChainName,
  handleChangeInWsUrl, handleChangeInNodeType, handleChangeInStashAddress,
  handleChangeInMonitorNodeStatus, handleChangeInDataSourceStatus,
  handleChangeInArchiveStatus, currentNodeConfig, currentNodeIndex, validated,
  nodeNameValid, chainNameValid, wsUrlValid, stashValid,
}) {
  return (
    <div>
      <h1 className="heading-style-1">Nodes Configuration</h1>
      <AddNodeForm
        handleAddNode={handleAddNode}
        handleChangeInNodeName={handleChangeInNodeName}
        handleChangeInChainName={handleChangeInChainName}
        handleChangeInWsUrl={handleChangeInWsUrl}
        handleChangeInNodeType={handleChangeInNodeType}
        handleChangeInStashAddress={handleChangeInStashAddress}
        handleChangeInMonitorNodeStatus={handleChangeInMonitorNodeStatus}
        handleChangeInDataSourceStatus={handleChangeInDataSourceStatus}
        handleChangeInArchiveStatus={handleChangeInArchiveStatus}
        currentNodeConfig={currentNodeConfig}
        currentNodeIndex={currentNodeIndex}
        validated={validated}
        nodeNameValid={nodeNameValid}
        chainNameValid={chainNameValid}
        wsUrlValid={wsUrlValid}
        stashValid={stashValid}
      />
    </div>
  );
}

function NodesTableContent(props) {
  const content = [];
  const nodes = props.nodesConfigJson;

  if (Object.keys(nodes).length === 0) {
    content.push(
      <tr key="no-content-key">
        <td colSpan="9" className="date-style">
          No nodes for monitoring added yet! Use the form above to add nodes.
        </td>
      </tr>,
    );
    return content;
  }

  Object.entries(nodes).forEach(([node, data]) => {
    content.push(
      <tr key={node}>
        {fieldEmpty(data.node_name) ? <td>N/a</td> : <td>{data.node_name}</td>}
        {
          fieldEmpty(data.chain_name) ? <td>N/a</td>
            : <td>{data.chain_name}</td>
        }
        {
          fieldEmpty(data.node_ws_url) ? <td>N/a</td>
            : <td>{data.node_ws_url}</td>
        }
        <td className="column-style">
          {
            toBool(data.monitor_node) ? (
              <FontAwesomeIcon icon={faCheck} color="green" />
            ) : (<FontAwesomeIcon icon={faTimes} color="red" />)
          }
        </td>
        <td className="column-style">
          {
            toBool(data.use_as_data_source) ? (
              <FontAwesomeIcon icon={faCheck} color="green" />)
              : (<FontAwesomeIcon icon={faTimes} color="red" />)
          }
        </td>
        <td className="column-style">
          {
            toBool(data.is_archive_node) ? (
              <FontAwesomeIcon icon={faCheck} color="green" />)
              : (<FontAwesomeIcon icon={faTimes} color="red" />)
          }
        </td>
        <td className="column-style">
          {
            toBool(data.node_is_validator) ? (
              <FontAwesomeIcon icon={faCheck} color="green" />)
              : (<FontAwesomeIcon icon={faTimes} color="red" />)
          }
        </td>
        {fieldEmpty(data.stash_account_address)
          ? <td>N/a</td>
          : <td>{data.stash_account_address}</td>}
        <td>
          <button
            className="delete-button-style"
            onClick={() => props.handleRemoveNode(parseInt(node.substr(
              node.length - 1,
            ), 10))}
            type="button"
          >
            <FontAwesomeIcon
              icon={faTimesCircle}
              color="red"
              className="fa-remove"
            />
          </button>
        </td>
      </tr>,
    );
  });

  return content;
}

function NodesTable({ nodesConfigJson, handleRemoveNode }) {
  return (
    <div>
      <h1 className="heading-style-2" style={{ marginBottom: '-10px' }}>
        Added Nodes
      </h1>
      <Table responsive className="tables-style">
        <thead>
          <tr>
            <th>Name</th>
            <th>Chain</th>
            <th>Web Socket</th>
            <th className="column-style">Monitor Node</th>
            <th className="column-style">Data Source</th>
            <th className="column-style">Archive</th>
            <th className="column-style">Validator</th>
            <th>Stash Address</th>
            <th>{}</th>
          </tr>
        </thead>
        <tbody>
          <NodesTableContent
            nodesConfigJson={nodesConfigJson}
            handleRemoveNode={handleRemoveNode}
          />
        </tbody>
      </Table>
    </div>
  );
}

class NodesConfig extends Component {
  constructor(props) {
    super(props);
    // We need to set a timer that tries to get data periodically until the
    // data is fetched. This must be done since data from the config must be
    // fetched once.
    this.dataTimer = null;
    this.state = {
      nodesConfigJson: {},
      currentNodeConfig: Object.create(
        nodeConfig, Object.getOwnPropertyDescriptors(nodeConfig),
      ),
      isFetchingData: true,
      currentNodeIndex: 0,
      validated: false,
    };
  }

  componentDidMount() {
    this.fetchNodesConfig();
    this.dataTimer = setInterval(this.fetchNodesConfig.bind(this), 5000);
  }

  async fetchNodesConfig() {
    let response;
    try {
      response = await getConfig('user_config_nodes.ini');
    } catch (e) {
      if (e.response) {
        // The request was made and the server responded
        // with a status code that falls out of the range of
        // 2xx
        ToastsStore.error(
          `Error: ${e.response.data.error}`, 5000,
        );
      } else {
        // Something happened in setting up the request that
        // triggered an Error
        ToastsStore.error(`Error: ${e.message}`, 5000);
      }
      return;
    }
    // Remove timer since data was obtained
    clearInterval(this.dataTimer);
    this.dataTimer = null;
    const nodesConfigJson = response.data.result;
    if (nodesConfigJson !== undefined
      && Object.keys(nodesConfigJson).length !== 0) {
      // Since we need to store nodes in the config under the section 'node_i',
      // the current index must always be one greater than the highest i in
      // 'node_i' from the nodes_config.
      const highestNodeIndex = highestItemIndexInConfig(
        nodesConfigJson, 'node_',
      );
      let checkedConfig = fixSpecificSectionsOfConfig(
        response.data.result, nodeConfig, 'node_',
      );
      checkedConfig = keepSpecificSectionsFromConfig(checkedConfig, 'node_');
      this.setState({
        nodesConfigJson: checkedConfig,
        isFetchingData: false,
        currentNodeIndex: highestNodeIndex + 1,
      });
    } else {
      this.setState({ isFetchingData: false });
    }
  }

  handleAddNode(event) {
    // If the form has invalid input set the validation to true so that correct
    // and incorrect input fields can be displayed. If the form has valid inputs
    // save the input
    event.preventDefault();
    if (!this.nodeDataValid()) {
      this.setState({ validated: true });
      event.stopPropagation();
      return;
    }
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const { nodesConfigJson, currentNodeConfig } = prevState;
      const currentNodeIndex = prevState.currentNodeIndex.toString();
      // If node is not a validator do not store a stash account as it does not
      // make sense
      if (!toBool(currentNodeConfig.node_is_validator)) {
        currentNodeConfig.stash_account_address = '';
      }
      // If node is not a data source, the node will not be used as archive
      // source, therefore need to set it to false.
      if (!toBool(currentNodeConfig.use_as_data_source)) {
        currentNodeConfig.is_archive_node = 'false';
      }
      nodesConfigJson[`node_${currentNodeIndex}`] = currentNodeConfig;
      return {
        nodesConfigJson,
        currentNodeConfig: Object.create(
          nodeConfig, Object.getOwnPropertyDescriptors(nodeConfig),
        ),
        currentNodeIndex: prevState.currentNodeIndex + 1,
        validated: false,
      };
    });
  }

  nodeNameValid() {
    const { state } = this;
    return !fieldEmpty(state.currentNodeConfig.node_name)
      && fieldValueUniqueAmongAllfieldsInJSON(
        state.nodesConfigJson, 'node_name', state.currentNodeConfig.node_name,
      );
  }

  wsUrlValid() {
    const { state } = this;
    return !fieldEmpty(state.currentNodeConfig.node_ws_url);
  }

  stashValid() {
    const { state } = this;
    // If node is not a validator, the stash field does not apply.
    if (!toBool(state.currentNodeConfig.node_is_validator)) {
      return true;
    }
    // Otherwise it must not be empty.
    return !fieldEmpty(state.currentNodeConfig.stash_account_address);
  }

  chainNameValid() {
    const { state } = this;
    return !fieldEmpty(state.currentNodeConfig.chain_name);
  }

  nodeDataValid() {
    return this.nodeNameValid() && this.chainNameValid() && this.wsUrlValid()
      && this.stashValid();
  }

  handleChangeInNodeName(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.currentNodeConfig;
      newConfig.node_name = event.target.value;
      return { currentNodeConfig: newConfig };
    });
  }

  handleChangeInChainName(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.currentNodeConfig;
      newConfig.chain_name = event.target.value;
      return { currentNodeConfig: newConfig };
    });
  }

  handleChangeInWsUrl(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.currentNodeConfig;
      newConfig.node_ws_url = event.target.value;
      return { currentNodeConfig: newConfig };
    });
  }

  handleChangeInNodeType() {
    this.setState((prevState) => {
      const newConfig = prevState.currentNodeConfig;
      newConfig.node_is_validator = (!toBool(
        prevState.currentNodeConfig.node_is_validator,
      )).toString();
      return { currentNodeConfig: newConfig };
    });
  }

  handleChangeInStashAddress(event) {
    // For the event to be used in the => function it must be persisted,
    // otherwise, it would be nullified.
    event.persist();
    this.setState((prevState) => {
      const newConfig = prevState.currentNodeConfig;
      newConfig.stash_account_address = event.target.value;
      return { currentNodeConfig: newConfig };
    });
  }

  handleChangeInMonitorNodeStatus() {
    this.setState((prevState) => {
      const newConfig = prevState.currentNodeConfig;
      newConfig.monitor_node = (!toBool(
        prevState.currentNodeConfig.monitor_node,
      )).toString();
      return { currentNodeConfig: newConfig };
    });
  }

  handleChangeInDataSourceStatus() {
    this.setState((prevState) => {
      const newConfig = prevState.currentNodeConfig;
      newConfig.use_as_data_source = (!toBool(
        prevState.currentNodeConfig.use_as_data_source,
      )).toString();
      return { currentNodeConfig: newConfig };
    });
  }

  handleChangeInArchiveStatus() {
    this.setState((prevState) => {
      const newConfig = prevState.currentNodeConfig;
      newConfig.is_archive_node = (!toBool(
        prevState.currentNodeConfig.is_archive_node,
      )).toString();
      return { currentNodeConfig: newConfig };
    });
  }

  handleRemoveNode(index) {
    this.setState((prevState) => {
      const updatedNodesConfig = prevState.nodesConfigJson;
      delete updatedNodesConfig[`node_${index}`];
      const highestNodeIndex = highestItemIndexInConfig(
        updatedNodesConfig, 'node_',
      );
      return {
        nodesConfigJson: updatedNodesConfig,
        currentNodeIndex: highestNodeIndex + 1,
      };
    });
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
              <Container>
                <NodesConfigForm
                  handleAddNode={event => this.handleAddNode(event)}
                  handleChangeInChainName={
                    event => this.handleChangeInChainName(event)
                  }
                  handleChangeInNodeName={
                    event => this.handleChangeInNodeName(event)
                  }
                  handleChangeInWsUrl={
                    event => this.handleChangeInWsUrl(event)
                  }
                  handleChangeInNodeType={() => this.handleChangeInNodeType()}
                  handleChangeInStashAddress={
                    event => this.handleChangeInStashAddress(event)
                  }
                  handleChangeInMonitorNodeStatus={
                    () => this.handleChangeInMonitorNodeStatus()
                  }
                  handleChangeInDataSourceStatus={
                    () => this.handleChangeInDataSourceStatus()
                  }
                  handleChangeInArchiveStatus={
                    () => this.handleChangeInArchiveStatus()
                  }
                  currentNodeConfig={state.currentNodeConfig}
                  currentNodeIndex={state.currentNodeIndex}
                  validated={state.validated}
                  nodeNameValid={() => this.nodeNameValid()}
                  chainNameValid={() => this.chainNameValid()}
                  wsUrlValid={() => this.wsUrlValid()}
                  stashValid={() => this.stashValid()}
                />
                <NodesTable
                  nodesConfigJson={state.nodesConfigJson}
                  handleRemoveNode={index => this.handleRemoveNode(index)}
                />
                {
                  Object.keys(state.nodesConfigJson).length > 0 && (
                    <div className="div-content-centre-style-margin-top">
                      <Button
                        className="button-style2"
                        onClick={async () => {
                          try {
                            ToastsStore.info('Saving config', 5000);
                            await sendConfig(
                              'user_config_nodes.ini',
                              state.nodesConfigJson,
                            );
                            ToastsStore.success('Config saved', 5000);
                          } catch (e) {
                            if (e.response) {
                              // The request was made and the server responded
                              // with a status code that falls out of the
                              // range of 2xx
                              ToastsStore.error(
                                `Saving failed. Error: ${
                                  e.response.data.error
                                }`, 5000,
                              );
                            } else {
                              // Something happened in setting up the request
                              // that triggered an Error
                              ToastsStore.error(
                                `Saving failed. Error: ${e.message}`, 5000,
                              );
                            }
                          }
                        }
                        }
                      >
                        Save Config
                      </Button>
                    </div>
                  )
                }
              </Container>
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

const nodeConfigType = PropTypes.shape({
  node_name: PropTypes.string,
  chain_name: PropTypes.string,
  node_ws_url: PropTypes.string,
  node_is_validator: PropTypes.string,
  is_archive_node: PropTypes.string,
  monitor_node: PropTypes.string,
  use_as_data_source: PropTypes.string,
  stash_account_address: PropTypes.string,
});

AddNodeForm.propTypes = forbidExtraProps({
  currentNodeConfig: nodeConfigType.isRequired,
  handleChangeInNodeName: PropTypes.func.isRequired,
  handleChangeInChainName: PropTypes.func.isRequired,
  handleChangeInWsUrl: PropTypes.func.isRequired,
  handleChangeInNodeType: PropTypes.func.isRequired,
  handleChangeInStashAddress: PropTypes.func.isRequired,
  handleChangeInMonitorNodeStatus: PropTypes.func.isRequired,
  handleChangeInDataSourceStatus: PropTypes.func.isRequired,
  handleChangeInArchiveStatus: PropTypes.func.isRequired,
  handleAddNode: PropTypes.func.isRequired,
  currentNodeIndex: PropTypes.number.isRequired,
  validated: PropTypes.bool.isRequired,
  nodeNameValid: PropTypes.func.isRequired,
  chainNameValid: PropTypes.func.isRequired,
  wsUrlValid: PropTypes.func.isRequired,
  stashValid: PropTypes.func.isRequired,
});

NodesConfigForm.propTypes = forbidExtraProps({
  currentNodeConfig: nodeConfigType.isRequired,
  handleChangeInNodeName: PropTypes.func.isRequired,
  handleChangeInWsUrl: PropTypes.func.isRequired,
  handleChangeInNodeType: PropTypes.func.isRequired,
  handleChangeInStashAddress: PropTypes.func.isRequired,
  handleChangeInMonitorNodeStatus: PropTypes.func.isRequired,
  handleChangeInDataSourceStatus: PropTypes.func.isRequired,
  handleChangeInArchiveStatus: PropTypes.func.isRequired,
  handleAddNode: PropTypes.func.isRequired,
  handleChangeInChainName: PropTypes.func.isRequired,
  currentNodeIndex: PropTypes.number.isRequired,
  validated: PropTypes.bool.isRequired,
  nodeNameValid: PropTypes.func.isRequired,
  chainNameValid: PropTypes.func.isRequired,
  wsUrlValid: PropTypes.func.isRequired,
  stashValid: PropTypes.func.isRequired,
});

NodesTable.propTypes = forbidExtraProps({
  nodesConfigJson: PropTypes.objectOf(PropTypes.object).isRequired,
  handleRemoveNode: PropTypes.func.isRequired,
});

export { NodesConfig, createColumnFormWithSubmit };
