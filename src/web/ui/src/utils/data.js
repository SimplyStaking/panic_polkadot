const axios = require('axios');

function sendData(url, params, body) {
  return axios.post(url, body, { params });
}

function fetchData(url, params) {
  return axios.get(url, { params });
}

function pingNode(wsUrl) {
  return sendData('/server/polkadot_api_server/ping_node', {},
    { websocket: wsUrl });
}

function pingMongoDB(host, port, user, pass) {
  return sendData('/server/ping_mongo', {}, {
    host, port, user, pass,
  });
}

function pingRedis(host, port, password) {
  return sendData('/server/ping_redis',
    {}, { host, port, password });
}

function pingAPIServer(endpoint) {
  return sendData('/server/polkadot_api_server/ping_api', {}, { endpoint });
}

function getChainNames() {
  return fetchData('/server/chains', { onlyIfMonitored: true });
}

function getAllChainInfo(chainName) {
  return fetchData('/server/all_chain_info', { chainName });
}

function sendTestEmail(smtp, from, to, user, pass) {
  return sendData('/server/test_email', {}, {
    smtp, from, to, user, pass,
  });
}

function testCall(accountSid, authToken, twilioPhoneNumber,
  phoneNumberToDial) {
  return sendData('/server/test_twilio', {}, {
    accountSid, authToken, twilioPhoneNumber, phoneNumberToDial,
  });
}

function getAlerts(size, pageNo) {
  return fetchData('/server/alerts', { size, pageNo });
}

function getConfig(file) {
  return fetchData('/server/config', { file });
}

function sendConfig(file, config) {
  return sendData('/server/config', { file }, { config });
}

export {
  pingNode, sendData, fetchData, pingMongoDB, pingRedis, pingAPIServer,
  getChainNames, getAllChainInfo, sendTestEmail, testCall, getAlerts,
  getConfig, sendConfig,
};

// TODO: Do safe (with try catch) and unsafe (without try catch) if it makes
//       sense during refactoring to avoid having duplicated code
