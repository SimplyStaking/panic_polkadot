/* eslint-disable no-console */
const express = require('express');
const path = require('path');
const axios = require('axios');
const nodemailer = require('nodemailer');
const twilio = require('twilio');
const mongoClient = require('mongodb').MongoClient;
const utils = require('./server/utils');
const cfg = require('./server/configs');
const redis = require('./server/redis');
const mongo = require('./server/mongo');
const msg = require('./server/msgs');
const files = require('./server/files');
const filters = require('./server/filters');

const app = express();
app.disable('x-powered-by');
app.use(express.json());
app.use(express.static(path.join(__dirname, 'build')));

// ---------------------------------------- Info from config files

let alerterID;
let redisDB;
let polkadotApiEndpoint;
let chainNodesMap = {};
let repoNameList = [];
let mongoInfo;
let redisInfo;

function resetInfoFromUserConfigMain() {
  alerterID = undefined;
  mongoInfo = undefined;
  redisInfo = undefined;
  console.debug('Set main user config values to default.');
}

function resetInfoFromUserNodesConfig() {
  chainNodesMap = {};
  console.debug('Set nodes user config values to default.');
}

function resetInfoFromUserReposConfig() {
  repoNameList = {};
  console.debug('Set repos user config values to default.');
}

function resetInfoFromInternalMainConfig() {
  redisDB = undefined;
  console.debug('Set main internal config values to default.');
}

function loadInfoFromUserConfigMain() {
  const configName = cfg.USER_CONFIG_MAIN;
  try {
    const config = cfg.readConfig(configName);

    // Get unique alerter identifier
    if (config.general && config.general.unique_alerter_identifier) {
      alerterID = config.general.unique_alerter_identifier;
      console.debug('Set alerter ID to %s', alerterID);
    } else {
      console.error('Missing alerter ID from %s. Using %s',
        configName, alerterID);
    }

    // Get polkadot api endpoint
    if (config.api && config.api.polkadot_api_endpoint) {
      polkadotApiEndpoint = config.api.polkadot_api_endpoint;
      console.debug('Set polkadot API endpoint to %s', polkadotApiEndpoint);
    } else {
      console.error('Missing api.polkadot_api_endpoint from %s. Using %s',
        configName, polkadotApiEndpoint);
    }

    // Get whole mongo info section
    if (config.mongo) {
      mongoInfo = config.mongo;
      console.debug('Set mongo info to %s', JSON.stringify(mongoInfo));
    } else {
      console.error('Missing mongo info from %s. Using %s',
        configName, mongoInfo);
    }

    // Get whole redis info section
    if (config.redis) {
      redisInfo = config.redis;
      console.debug('Set redis info to %s', JSON.stringify(redisInfo));
    } else {
      console.error('Missing redis info from %s. Using %s',
        configName, redisInfo);
    }
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.error('Config %s not found. Using alerterID=%s, mongoInfo=%s, '
        + 'redisInfo=%s', configName, alerterID, mongoInfo, redisInfo);
    } else {
      throw err;
    }
  }
}

function loadInfoFromUserNodesConfig() {
  const configName = cfg.USER_CONFIG_NODES;
  try {
    const nodes = cfg.readConfig(configName);
    const cnMap = {}; // node-chain map

    // Form map of chain names to node names by iterating over nodes
    Object.values(nodes)
      .forEach((n) => {
        if (n.node_name && n.chain_name) {
          if (!cnMap[n.chain_name]) {
            cnMap[n.chain_name] = {};
          }
          cnMap[n.chain_name][n.node_name] = n;
        } else {
          console.error('Skipping node %s with no chain_name or node_name.', n);
        }
      });

    chainNodesMap = cnMap;
    console.debug('Set chain nodes map to %s', chainNodesMap);
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.error('Config %s not found. Using nodes list "%s".',
        configName, chainNodesMap);
    } else {
      throw err;
    }
  }
}

function loadInfoFromUserReposConfig() {
  const configName = cfg.USER_CONFIG_REPOS;
  try {
    const repos = cfg.readConfig(configName);
    const repoNames = new Set();

    // Form list of repo names by iterating over repos
    Object.values(repos)
      .forEach((r) => {
        if (r.repo_name) {
          repoNames.add(r.repo_name);
        } else {
          console.error('Skipping repo %s with no repo_name field.', r);
        }
      });

    repoNameList = Array.from(repoNames);
    console.debug('Set repo list to %s', repoNameList);
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.error('Config %s not found. Using repos list "%s".',
        configName, repoNameList);
    } else {
      throw err;
    }
  }
}

function loadInfoFromInternalMainConfig() {
  const configName = cfg.INTERNAL_CONFIG_MAIN;
  try {
    const config = cfg.readConfig(configName);

    // Get redis database
    if (config.redis && config.redis.redis_database) {
      redisDB = config.redis.redis_database;
      console.debug('Set redis DB to %s', redisDB);
    } else {
      console.error('Missing redis.redis_database from %s. Using %s',
        configName, redisDB);
    }
  } catch (err) {
    if (err.code === 'ENOENT') {
      console.error('Config %s not found. Using redis DB "%s".',
        configName, redisDB);
    } else {
      throw err;
    }
  }
}

// ---------------------------------------- Config get

app.get('/server/config', async (req, res) => {
  console.log('Received GET request for %s', req.url);
  const { file } = req.query;

  if (!file) {
    return res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
  }

  if (cfg.ALL_CONFIG_FILES.includes(file)) {
    try {
      const data = cfg.readConfig(file);
      return res.status(utils.SUCCESS_STATUS)
        .send(utils.resultJson(data));
    } catch (err) {
      if (err.code === 'ENOENT') {
        return res.status(utils.SUCCESS_STATUS)
          .send(utils.errorJson(msg.MSG_CONFIG_NOT_FOUND));
      }
      throw err;
    }
  }
  return res.status(utils.ERR_STATUS)
    .send(utils.errorJson(msg.MSG_CONFIG_UNRECOGNIZED));
});

// ---------------------------------------- Config post

app.post('/server/config', async (req, res) => {
  console.log('Received POST request for %s', req.url);
  const { file } = req.query;
  const { config } = req.body;

  if (!(file && config)) {
    return res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
  }

  if (cfg.ALL_CONFIG_FILES.includes(file)) {
    cfg.writeConfig(file, config);
    loadInfoFromUserConfigMain();
    return res.status(utils.SUCCESS_STATUS)
      .send(utils.resultJson(msg.MSG_CONFIG_SUBMITTED));
  }
  return res.status(utils.ERR_STATUS)
    .send(utils.errorJson(msg.MSG_CONFIG_UNRECOGNIZED));
});

// ---------------------------------------- Redis

function getRedisKeyPrefix() {
  return `${alerterID}:`;
}

// ---------------------------------------- Alerts log

app.get('/server/alerts', async (req, res) => {
  console.log('Received GET request for %s', req.url);
  const { pageNo, size } = req.query;

  if (!(pageNo && size)) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
    return;
  }

  if (!mongoInfo || (mongoInfo.enabled && !utils.toBool(mongoInfo.enabled))) {
    console.error(msg.MSG_MONGO_NOT_SET_UP_LONG);
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MONGO_NOT_SET_UP));
    return;
  }

  const parsedPageNo = parseInt(pageNo, 10);
  const parsedSize = parseInt(size, 10);
  if (parsedPageNo <= 0) {
    const errMsg = 'invalid page number; should be greater than 0';
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(errMsg));
    return;
  }
  if (parsedSize <= 0) {
    const errMsg = 'invalid page size; should be greater than 0';
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(errMsg));
    return;
  }

  const query = {};
  query.skip = parsedSize * (parsedPageNo - 1);
  query.limit = parsedSize;
  query.sort = { $natural: -1 };

  const authPass = mongoInfo.pass ? `:${mongoInfo.pass}` : '';
  const authFull = mongoInfo.user ? `${mongoInfo.user}${authPass}@` : '';
  const url = `mongodb://${authFull}${mongoInfo.host}:${mongoInfo.port}`;
  await mongoClient.connect(url, mongo.options, (err, client) => {
    if (err != null) {
      res.status(utils.ERR_STATUS)
        .send(utils.errorJson(msg.MSG_MONGO_ERROR));
      return;
    }

    const db = client.db(mongoInfo.db_name);
    const colName = `alerts_${alerterID}`;
    mongo.findDocuments(db, colName, query, (totalCount, alerts) => {
      client.close();
      const totalPages = (
        parsedSize > 0 ? Math.ceil(totalCount / parsedSize) : 1);
      res.status(utils.SUCCESS_STATUS)
        .send(utils.resultJson({
          total_pages: totalPages,
          alerts,
        }));
    });
  });
});

// ---------------------------------------- Chains and Nodes

app.get('/server/chains', async (req, res) => {
  console.log('Received GET request for %s', req.url);
  const onlyIfMonitored = req.query.onlyIfMonitored || '';

  // Apply filter if we only want chains for
  // which the nodes are involved in monitoring
  if (utils.toBool(onlyIfMonitored)) {
    const chains = filters.getMonitoredChainsConsideringNodes(chainNodesMap);
    res.status(utils.SUCCESS_STATUS)
      .send(utils.resultJson(chains));
    return;
  }
  res.status(utils.SUCCESS_STATUS)
    .send(utils.resultJson(Object.keys(chainNodesMap)));
});

app.get('/server/chain_nodes_map', async (req, res) => {
  console.log('Received GET request for %s', req.url);
  const onlyIfMonitored = req.query.onlyIfMonitored || '';

  // Apply filter if we only want chains for
  // which the nodes are involved in monitoring
  if (utils.toBool(onlyIfMonitored)) {
    res.status(utils.SUCCESS_STATUS)
      .send(utils.resultJson(filters.getMonitoredNodes(chainNodesMap)));
    return;
  }
  res.status(utils.SUCCESS_STATUS)
    .send(utils.resultJson(chainNodesMap));
});

app.get('/server/all_chain_info', async (req, res) => {
  console.log('Received GET request for %s', req.url);

  if (!redisInfo || (redisInfo.enabled && !utils.toBool(redisInfo.enabled))) {
    console.error(msg.MSG_REDIS_NOT_SET_UP_LONG);
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_REDIS_NOT_SET_UP));
    return;
  }

  const { chainName } = req.query;

  if (!chainName) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
    return;
  }

  // Filter map and get nodes list
  const filteredCNMap = filters.getMonitoredNodes(chainNodesMap);
  const monitoredChains = filters.getMonitoredChains(chainNodesMap);
  const nodesList = filteredCNMap[chainName] || [];

  // Check that chain is recognized
  if (!filteredCNMap[chainName]) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_CHAIN_NOT_FOUND));
    return;
  }

  // Initialise allInfo with general template
  const allInfo = {
    blockchain: {
      referendum_count: null,
      public_prop_count: null,
      council_prop_count: null,
      validator_set_size: null,
    },
    nodes: {},
    monitors: {
      node: {},
      blockchain: {},
    },
  };

  // List of values to get from Redis
  const valuesToGetNormally = []; // mget to be used
  const valuesToGetFromHash = []; // hmget to be used

  // ----------------------------- Blockchain

  // Create redis keys for blockchain
  let keysBc = redis.getKeysBlockchain();
  if (monitoredChains.indexOf(chainName) >= 0) {
    keysBc = redis.addPostfixToDictValues(keysBc, `_${chainName}`);
  } else {
    // Replace keys with dummy key so that values get set to null
    Object.keys(keysBc)
      .forEach((k) => {
        keysBc[k] = redis.DUMMY_KEY;
      });
  }

  // Add keys to the values-to-get list
  Object.keys(keysBc)
    .forEach(k => valuesToGetFromHash.push(keysBc[k]));

  // Create blockchain section
  allInfo.blockchain = keysBc;

  if (monitoredChains.indexOf(chainName) >= 0) {
    // Create redis keys for blockchain monitor
    let keysBcMonitor = redis.getKeysBlockchainMonitor();
    keysBcMonitor = redis.addPrefixToDictValues(keysBcMonitor,
      getRedisKeyPrefix()); // Add prefix
    keysBcMonitor = redis.addPostfixToDictValues(keysBcMonitor,
      `_Blockchain monitor (${chainName})`); // Add postfix

    // Add keys to the values-to-get list
    Object.keys(keysBcMonitor)
      .forEach((k) => {
        valuesToGetNormally.push(keysBcMonitor[k]);
      });

    // Create blockchain monitor section
    allInfo.monitors.blockchain[chainName] = keysBcMonitor;
  }

  // ----------------------------- Nodes

  Object.keys(nodesList)
    .forEach((n) => {
      // Create redis keys for node
      let keysNode = redis.getKeysNode();
      keysNode = redis.addPostfixToDictValues(keysNode, `_${n}`);

      // Add keys to the values-to-get list
      Object.keys(keysNode)
        .forEach((k) => {
          valuesToGetFromHash.push(keysNode[k]);
        });

      // Create redis keys for node monitor
      let keysNodeMonitor = redis.getKeysNodeMonitor();
      keysNodeMonitor = redis.addPrefixToDictValues(keysNodeMonitor,
        getRedisKeyPrefix()); // Add prefix
      keysNodeMonitor = redis.addPostfixToDictValues(keysNodeMonitor,
        `_Node monitor (${n})`); // Add postfix

      // Add keys to the values-to-get list
      Object.keys(keysNodeMonitor)
        .forEach((k) => {
          valuesToGetNormally.push(keysNodeMonitor[k]);
        });

      // Create node and node monitor sections
      allInfo.nodes[n] = keysNode;
      allInfo.monitors.node[n] = keysNodeMonitor;
    });

  // ----------------------------- Get values

  const bcHash = redis.getHashes().blockchain;
  const hash = `${getRedisKeyPrefix()}${bcHash}_${chainName}`;
  const valuesDict = {};

  const redisClient = redis.getRedisClient(
    redisInfo.host, redisInfo.port, redisInfo.password,
  );
  redisClient.select(redisDB, (err, _) => {
    if (err != null) {
      redisClient.quit();
      console.error(err);
      const errMsg = err.code === 'NOAUTH'
        ? msg.MSG_REDIS_AUTH_INCORRECT : msg.MSG_REDIS_ERROR;
      res.status(utils.ERR_STATUS)
        .send(utils.errorJson(errMsg));
      return;
    }

    redisClient
      .multi()
      .mget(valuesToGetNormally, (err1, values) => {
        valuesToGetNormally.forEach((key, i) => {
          valuesDict[key] = values[i];
        });
      })
      .hmget(hash, valuesToGetFromHash, (err2, values) => {
        valuesToGetFromHash.forEach((key, i) => {
          valuesDict[key] = values[i];
        });
      })
      // eslint-disable-next-line no-unused-vars
      .exec((err3, replies) => {
        if (err3 != null) {
          res.status(utils.ERR_STATUS)
            .send(utils.errorJson(msg.MSG_REDIS_ERROR));
          return;
        }

        // Replace keys in blockchain sections with value in valuesDict
        Object.keys(allInfo.blockchain)
          .forEach((k) => {
            allInfo.blockchain[k] = valuesDict[allInfo.blockchain[k]];
          });

        // Replace keys in blockchain monitor sections with value in valuesDict
        if (allInfo.monitors.blockchain[chainName]) {
          Object.keys(allInfo.monitors.blockchain[chainName])
            .forEach((k) => {
              allInfo.monitors.blockchain[chainName][k] = valuesDict[
                allInfo.monitors.blockchain[chainName][k]];
            });
        }

        // Replace keys in node sections with value in valuesDict
        Object.keys(allInfo.nodes)
          .forEach((n) => {
            Object.keys(allInfo.nodes[n])
              .forEach((k) => {
                allInfo.nodes[n][k] = valuesDict[allInfo.nodes[n][k]];
              });
          });

        // Replace keys in node monitor sections with value in valuesDict
        Object.keys(allInfo.monitors.node)
          .forEach((n) => {
            Object.keys(allInfo.monitors.node[n])
              .forEach((k) => {
                allInfo.monitors.node[n][k] = valuesDict[
                  allInfo.monitors.node[n][k]];
              });
          });

        // Add extra information to each node (is_validator)
        Object.keys(nodesList)
          .forEach((n) => {
            if (nodesList[n] && nodesList[n].node_is_validator) {
              allInfo.nodes[n].is_validator = nodesList[n].node_is_validator;
            } else {
              console.error('Missing node_is_validator for node %s. '
                + 'Defaulting to False.', n);
              allInfo.nodes[n].is_validator = false.toString();
            }
          });

        redisClient.quit();
        res.status(utils.SUCCESS_STATUS)
          .send(utils.resultJson(allInfo));
      });
  });
});

// ---------------------------------------- Repos

app.get('/server/repos', async (req, res) => {
  console.log('Received GET request for %s', req.url);
  const repos = Array.from(repoNameList);
  return res.status(utils.SUCCESS_STATUS)
    .send(utils.resultJson(repos));
});

// ---------------------------------------- Pings and Tests

app.post('/server/ping_server', async (req, res) => {
  console.log('Received POST request for %s', req.url);
  try {
    return res.status(utils.SUCCESS_STATUS)
      .send(utils.resultJson(msg.MSG_PONG));
  } catch (err) {
    return res.status(utils.ERR_STATUS)
      .send(utils.errorJson(err));
  }
});

app.post('/server/ping_redis', async (req, res) => {
  console.log('Received POST request for %s', req.url);
  const { host, port, password } = req.body;

  if (!(host && port)) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
    return;
  }

  const redisClient = redis.getRedisClient(host, port, password);
  redisClient.ping((err, result) => {
    redisClient.quit();

    if (err == null && result.toLowerCase() === 'pong') {
      res.status(utils.SUCCESS_STATUS)
        .send(utils.resultJson(msg.MSG_PONG));
      return;
    }

    if (err == null) {
      console.log('Unexpected Redis ping result: %s', result);
      res.status(utils.ERR_STATUS)
        .send(utils.errorJson(msg.MSG_REDIS_ERROR));
      return;
    }

    console.error(err);
    const errMsg = err.code === 'NOAUTH'
      ? msg.MSG_REDIS_AUTH_INCORRECT : msg.MSG_REDIS_ERROR;
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(errMsg));
  });
});

app.post('/server/ping_mongo', async (req, res) => {
  console.log('Received POST request for %s', req.url);
  const {
    host, port, user, pass,
  } = req.body;

  if (!(host && port)) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
    return;
  }

  const authPass = pass ? `:${pass}` : '';
  const authFull = user ? `${user}${authPass}@` : '';
  const url = `mongodb://${authFull}${host}:${port}`;
  await mongoClient.connect(url, mongo.options, (err, _) => {
    if (err == null) {
      res.status(utils.SUCCESS_STATUS)
        .send(utils.resultJson(msg.MSG_PONG));
      return;
    }
    console.error(err);
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_NO_CONNECTION));
  });
});

app.post('/server/polkadot_api_server/ping_api', async (req, res) => {
  console.log('Received POST request for %s', req.url);
  const { endpoint } = req.body;

  if (!endpoint) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
    return;
  }

  const url = `${endpoint}/api/pingApi`;
  axios.get(url)
    .then((_) => {
      res.status(utils.SUCCESS_STATUS)
        .send(utils.resultJson(msg.MSG_PONG));
    })
    .catch((err) => {
      console.error(err);
      if (err.code === 'ECONNREFUSED') {
        res.status(utils.ERR_STATUS)
          .send(utils.errorJson(msg.MSG_NO_CONNECTION));
      } else {
        // Connection made but error occurred
        res.status(utils.ERR_STATUS)
          .send(utils.errorJson(msg.MSG_POLKADOT_API_SERVER_ERROR));
      }
    });
});

app.post('/server/polkadot_api_server/ping_node', async (req, res) => {
  console.log('Received POST request for %s', req.url);
  const { websocket } = req.body;

  if (!websocket) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
    return;
  }
  if (!polkadotApiEndpoint) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_POLKADOT_API_SERVER_NOT_CONFIGURED));
    return;
  }

  const url = `${polkadotApiEndpoint}/api/pingNode`;
  axios.get(url, { params: { websocket } })
    .then((_) => {
      res.status(utils.SUCCESS_STATUS)
        .send(utils.resultJson(msg.MSG_PONG));
    })
    .catch((err) => {
      console.error(err);
      if (err.code === 'ECONNREFUSED') {
        res.status(utils.ERR_STATUS)
          .send(utils.errorJson(msg.MSG_NO_CONNECTION));
      } else {
        // Connection made but error occurred (typically means node is missing)
        res.status(utils.ERR_STATUS)
          .send(utils.errorJson(msg.MSG_POLKADOT_API_SERVER_ERROR));
      }
    });
});

app.post('/server/test_twilio', async (req, res) => {
  console.log('Received POST request for %s', req.url);
  const {
    accountSid, authToken,
    twilioPhoneNumber, phoneNumberToDial,
  } = req.body;

  if (!(accountSid && authToken && twilioPhoneNumber && phoneNumberToDial)) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
    return;
  }

  const twilioClient = twilio(accountSid, authToken);
  twilioClient.calls
    .create({
      twiml: '<Response><Reject /></Response>',
      to: phoneNumberToDial,
      from: twilioPhoneNumber,
    })
    .then(() => res.status(utils.SUCCESS_STATUS)
      .send(utils.resultJson(msg.MSG_PONG)))
    .catch((err) => {
      console.error(err);
      res.status(utils.ERR_STATUS)
        .send(utils.errorJson(msg.MSG_TWILIO_ERROR));
    });
});

app.post('/server/test_email', async (req, res) => {
  console.log('Received POST request for %s', req.url);
  const {
    smtp, from, to, user, pass,
  } = req.body;

  if (!(smtp && from && to)) {
    res.status(utils.ERR_STATUS)
      .send(utils.errorJson(msg.MSG_MISSING_ARGUMENTS));
    return;
  }

  const transport = nodemailer.createTransport({
    host: smtp,
    auth: (user && pass) ? {
      user,
      pass,
    } : undefined,
  });

  transport.verify((err, _) => {
    if (err) {
      console.log(err);
      res.status(utils.ERR_STATUS)
        .send(utils.errorJson(msg.MSG_SMTP_ERROR));
      return;
    }

    const message = {
      from,
      to,
      subject: 'Test Email from PANIC',
      text: 'Test Email from PANIC',
    };

    transport.sendMail(message, (err2, info) => {
      if (err2) {
        console.log(err2);
        res.status(utils.ERR_STATUS)
          .send(utils.errorJson(msg.MSG_SMTP_ERROR));
        return;
      }
      console.debug(info);
      res.status(utils.SUCCESS_STATUS)
        .send(utils.resultJson(msg.MSG_PONG));
    });
  });
});

// ---------------------------------------- Server default

app.get('/server/*', async (req, res) => {
  console.log('Received GET request for %s', req.url);
  res.status(utils.ERR_STATUS)
    .send(utils.errorJson(msg.MSG_INVALID_ENDPOINT));
});

app.post('/server/*', async (req, res) => {
  console.log('Received POST request for %s', req.url);
  res.status(utils.ERR_STATUS)
    .send(utils.errorJson(msg.MSG_INVALID_ENDPOINT));
});

// ---------------------------------------- PANIC UI

app.get('/*', (req, res) => {
  console.log('Received GET request for %s', req.url);
  res.sendFile(path.join(__dirname, 'build', 'index.html'));
});

// ---------------------------------------- Start info-from-config loaders

// First batch of data loads
loadInfoFromUserConfigMain();
loadInfoFromUserNodesConfig();
loadInfoFromUserReposConfig();
loadInfoFromInternalMainConfig();

// Asynchronous data loads
files.listenFileChanges(cfg.toConfigPath(cfg.USER_CONFIG_MAIN),
  loadInfoFromUserConfigMain, resetInfoFromUserConfigMain);
files.listenFileChanges(cfg.toConfigPath(cfg.USER_CONFIG_NODES),
  loadInfoFromUserNodesConfig, resetInfoFromUserNodesConfig);
files.listenFileChanges(cfg.toConfigPath(cfg.USER_CONFIG_REPOS),
  loadInfoFromUserReposConfig, resetInfoFromUserReposConfig);
files.listenFileChanges(cfg.toConfigPath(cfg.INTERNAL_CONFIG_MAIN),
  loadInfoFromInternalMainConfig, resetInfoFromInternalMainConfig);

// ---------------------------------------- Start listen

const port = process.env.PORT || 9000;
app.listen(port, () => {
  console.log('Listening on %s', port);
});
