import React from 'react';
import Badge from 'react-bootstrap/Badge';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Blockchain from '../components/blockchain';
import Node from '../components/node';
import Monitor from '../components/monitor';
import { MONITOR_TYPES } from './constants';
import scaleToPico from './scaling';
import '../style/style.css';

function createBlockchainFromJson(name, chainInfo) {
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

  return new Blockchain(name, referendumCount, publicPropCount,
    councilPropCount, validatorSetSize);
}

function createNodesFromJson(activeChain, nodesJson) {
  const nodes = [];
  Object.entries(nodesJson).forEach(([node, data]) => {
    const chain = activeChain.name;
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

  return nodes;
}

function createMonitorTypeFromJson(activeChain, monitorsJson, monitorType) {
  const monitors = [];
  let monitorTypeJson;

  if (monitorType === MONITOR_TYPES.node_monitor) {
    monitorTypeJson = monitorsJson.node;
  } else if (monitorType === MONITOR_TYPES.blockchain_monitor) {
    monitorTypeJson = monitorsJson.blockchain;
  } else {
    return monitors;
  }
  Object.entries(monitorTypeJson).forEach(([monitor, data]) => {
    const chain = activeChain.name;
    const monitorName = `${monitor}`;
    const lastUpdate = data.alive === null ? -1 : parseFloat(data.alive);
    monitors.push(new Monitor(monitorName, chain, lastUpdate, monitorType));
  });

  return monitors;
}

function createActiveChainStats(activeChain) {
  const referendumCount = activeChain.referendumCount === -1
    ? 'N/a' : activeChain.referendumCount;
  const publicPropCount = activeChain.publicPropCount === -1
    ? 'N/a' : activeChain.publicPropCount;
  const councilPropCount = activeChain.councilPropCount === -1
    ? 'N/a' : activeChain.councilPropCount;
  const validatorSetSize = activeChain.validatorSetSize === -1
    ? 'N/a' : activeChain.validatorSetSize;

  return {
    referendumCount,
    publicPropCount,
    councilPropCount,
    validatorSetSize,
  };
}

function createActiveNodeStats(node) {
  const noOfPeers = node.noOfPeers === -1 ? 'N/a' : node.noOfPeers;
  const height = node.height === -1 ? 'N/a' : node.height;
  const bondedBalance = node.bondedBalance === -1
    ? 'N/a' : scaleToPico(node.bondedBalance);
  const noOfBlocksAuthored = node.noOfBlocksAuthored === -1
    ? 'N/a' : node.noOfBlocksAuthored;
  const wentDownAt = node.wentDownAt === -1 ? 'N/a' : node.wentDownAt;
  const lastHeightUpdate = node.lastHeightUpdate === -1
    ? 'no update' : node.lastHeightUpdate;

  return {
    noOfPeers,
    height,
    bondedBalance,
    noOfBlocksAuthored,
    wentDownAt,
    lastHeightUpdate,
  };
}

function createMonitorStats(monitor) {
  const lastUpdate = monitor.lastUpdate === -1
    ? 'no recent update' : monitor.lastUpdate;

  return { lastUpdate };
}

function createBadge(name, variant, key) {
  return (
    <Badge variant={variant} className="badges-style" key={key}>
      {name}
    </Badge>
  );
}

function createChainDropDownItems(elements, activeChainIndex) {
  const items = [];

  // If there is only one chain configured, the user is informed that there
  // are no other options
  if (elements.length === 1) {
    items.push(
      <NavDropdown.Item
        key="no-option-key"
        style={{ 'font-size': '15px' }}
        disabled
      >
        -- No other option --
      </NavDropdown.Item>,
    );
    return items;
  }

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

export {
  createBlockchainFromJson, createNodesFromJson, createMonitorTypeFromJson,
  createActiveChainStats, createBadge, createChainDropDownItems, createActiveNodeStats,
  createMonitorStats,
};
