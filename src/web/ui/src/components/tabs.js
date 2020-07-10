import React from 'react';
import Tabs from 'react-bootstrap/Tabs';
import Tab from 'react-bootstrap/Tab';
import { forbidExtraProps } from 'airbnb-prop-types';
import PropTypes from 'prop-types';
import { BLOCKCHAIN_TYPE, NODE_TYPE } from '../utils/constants';
import '../style/style.css';
import { NodeDataGrid } from './grids';

function createNodeTabs(nodes, activeChain) {
  const tabs = [];
  for (let i = 0; i < nodes.length; i += 1) {
    if (nodes[i].chain === activeChain.name) {
      tabs.push(
        <Tab eventKey={i} title={nodes[i].name} key={nodes[i].name}>
          <NodeDataGrid node={nodes[i]} />
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

NodeSelectionTabs.propTypes = forbidExtraProps({
  nodes: PropTypes.arrayOf(NODE_TYPE).isRequired,
  activeNodeIndex: PropTypes.number.isRequired,
  activeChain: BLOCKCHAIN_TYPE.isRequired,
  handleSelectNode: PropTypes.func.isRequired,
});

export default NodeSelectionTabs;
