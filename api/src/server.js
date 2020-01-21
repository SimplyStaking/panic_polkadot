const express = require('express');
const ConfigParser = require('configparser');
const {ApiPromise, WsProvider} = require('@polkadot/api');
const Timeout = require('await-timeout');

const substrateRPC = require('./substrate_rpc_interface');
const substrateQuery = require('./substrate_query_interface');


const TIMEOUT_TIME_MS = 10000;
const REQUEST_SUCCESS_STATUS = 200;
const REQUEST_ERROR_STATUS = 400;


function errorNeedToSetUpAPIMsg(websocket) {
    return {'error': `An API for ${websocket} `
            + 'needs to be setup before it can be queried'}
}

async function startListen(websocket) {
    try {
        console.log(`Connecting to ${websocket}`);
        // connect to the WebSocket once and reuse that connection
        let provider = new WsProvider(websocket);
        // open an API connection with the provider
        const api = await Promise.race([
            ApiPromise.create({provider}),
            Timeout.set(TIMEOUT_TIME_MS,
                'Connection could not be established.')]);
        // return the api
        return api;
    } catch (e) {
        console.log(e.toString());
    }
}

async function startPolkadotAPI() {
    // Start up the API
    const app = express();
    await app.use(express.json());

    // declare a dictionary which will contain all the apis that correspond to
    // the IPs submitted by the user in the format websocket_ip -> api
    let apis = {};

    // Read the configuration file (user_config_main.ini)
    // create a ConfigParser object which can read the config file
    const user_config_main = new ConfigParser();
    // specify the config file from which to read the configuration
    user_config_main.read('../config/user_config_main.ini');

    // read which API Port to use from the main config
    const API_PORT = await user_config_main.get('api_server', 'port');

    // Read the configuration file (user_config_nodes.ini)
    // create a ConfigParser object which can read the config file
    const user_config_nodes = new ConfigParser();
    // specify the config file from which to read the configuration
    user_config_nodes.read('../config/user_config_nodes.ini');

    // iterate over every node defined in the nodes config
    for (let i = 0; i < user_config_nodes.sections().length; i++) {
        // read the node's websocket from the config file
        const websocket = user_config_nodes.get(
            user_config_nodes.sections()[i], 'ws_url');

        // check whether an api has already been connected for that websocket_ip
        if (websocket in apis) {
            console.log(`An API for ${websocket} has already been set up`);
        } else {
            // add the api to the dictionary of apis so that it can be accessed
            // using its websocket ip as its key
            apis[websocket] = await startListen(websocket);
            // check if an API connection was successfully established
            if (apis.hasOwnProperty(websocket) && apis[websocket]) {
                console.log(`Successfully Connected to ${websocket}`);
            }
        }
    }

    await app.listen(API_PORT);
    console.log(`API running on port ${API_PORT}`);

    // Miscellaneous Endpoints
    app.get('/api/pingApi', async function (req, res) {
        console.log('Received request for /api/pingApi');
        try {
            return res.status(REQUEST_SUCCESS_STATUS).send({'result': 'pong'});
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/pingNode', async function (req, res) {
        console.log('Received request for /api/pingNode');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateRPC.rpcAPI(apis[websocket],
                    "system/chain");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(
                        {'result': 'pong'});
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(
                        {'error': 'no reply from node'});
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/getConnectionsList', async function (req, res) {
        console.log('Received request for /api/getConnectionsList');
        try {
            let websocket_api_list = [];
            // iterate over each key in the map of websocket_ip -> api
            for (websocket_ip in apis) {
                // check if API is defined (so it is not returned in the list
                // if a connection was never established)
                if (apis.hasOwnProperty(websocket_ip) && apis[websocket_ip]) {
                    // add the ip to the list of ips
                    websocket_api_list.push(websocket_ip)
                }
            }
            return res.status(REQUEST_SUCCESS_STATUS).send(
                {'result': websocket_api_list});
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    // RPC API Endpoints
    // Chain
    app.get('/api/rpc/chain/getBlockHash', async function (req, res) {
        console.log('Received request for /api/rpc/chain/getBlockHash');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // extract the blockNumber passed in the query (optional)
            const blockNumber = req.query.block_number;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateRPC.rpcAPI(apis[websocket],
                    "chain/getBlockHash", blockNumber);
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/rpc/chain/getFinalizedHead', async function (req, res) {
        console.log('Received request for /api/rpc/chain/getFinalizedHead');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateRPC.rpcAPI(apis[websocket],
                    "chain/getFinalizedHead");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/rpc/chain/getHeader', async function (req, res) {
        console.log('Received request for /api/rpc/chain/getHeader');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // extract the hash passed in the query (optional)
            const hash = req.query.hash;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateRPC.rpcAPI(apis[websocket],
                    "chain/getHeader", hash);
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    // System
    app.get('/api/rpc/system/chain', async function (req, res) {
        console.log('Received request for /api/rpc/system/chain');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateRPC.rpcAPI(apis[websocket],
                    "system/chain");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/rpc/system/health', async function (req, res) {
        console.log('Received request for /api/rpc/system/health');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateRPC.rpcAPI(apis[websocket],
                    "system/health");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    // Query API Endpoints
    // Council
    app.get('/api/query/council/members', async function (req, res) {
        console.log('Received request for /api/query/council/members');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "council/members");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/query/council/proposalCount', async function (req, res) {
        console.log('Received request for /api/query/council/proposalCount');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "council/proposalCount");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/query/council/proposalOf', async function (req, res) {
        console.log('Received request for /api/query/council/proposalOf');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // extract the hash passed in the query
            const hash = req.query.hash;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "council/proposalOf", hash);
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/query/council/proposals', async function (req, res) {
        console.log('Received request for /api/query/council/proposals');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "council/proposals");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    // Democracy
    app.get('/api/query/democracy/publicPropCount', async function (req, res) {
        console.log('Received request for ' +
            '/api/query/democracy/publicPropCount');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "democracy/publicPropCount");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/query/democracy/referendumCount', async function (req, res) {
        console.log('Received request for ' +
            '/api/query/democracy/referendumCount');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "democracy/referendumCount");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/query/democracy/referendumInfoOf', async function (req, res) {
        console.log('Received request for ' +
            '/api/query/democracy/referendumInfoOf');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // extract the referendumIndex passed in the query
            const referendumIndex = req.query.referendum_index;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "democracy/referendumInfoOf", referendumIndex);
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    // ImOnline
    app.get('/api/query/imOnline/authoredBlocks', async function (req, res) {
        console.log('Received request for /api/query/imOnline/authoredBlocks');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // extract the sessionIndex passed in the query
            const sessionIndex = req.query.session_index;
            // extract the validatorId passed in the query
            const validatorId = req.query.validator_id;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "imOnline/authoredBlocks", sessionIndex, validatorId);
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/query/imOnline/receivedHeartbeats', async function (req, res) {
        console.log('Received request for ' +
            '/api/query/imOnline/receivedHeartbeats');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // extract the sessionIndex passed in the query
            const sessionIndex = req.query.session_index;
            // extract the validatorId passed in the query
            const authIndex = req.query.auth_index;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "imOnline/receivedHeartbeats", sessionIndex, authIndex);
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    // Session
    app.get('/api/query/session/currentIndex', async function (req, res) {
        console.log('Received request for /api/query/session/currentIndex');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "session/currentIndex");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/query/session/disabledValidators', async function (req, res) {
        console.log('Received request for ' +
            '/api/query/session/disabledValidators');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "session/disabledValidators");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/query/session/validators', async function (req, res) {
        console.log('Received request for /api/query/session/validators');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "session/validators");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    // Staking
    app.get('/api/query/staking/currentElected', async function (req, res) {
        console.log('Received request for /api/query/staking/currentElected');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "staking/currentElected");
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    app.get('/api/query/staking/stakers', async function (req, res) {
        console.log('Received request for /api/query/staking/stakers');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // extract the accountAddress passed in the query
            const accountAddress = req.query.account_address;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "staking/stakers", accountAddress);
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    // System
    app.get('/api/query/system/events', async function (req, res) {
        console.log('Received request for /api/query/system/events');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // extract the blockHash passed in the query (optional)
            const blockHash = req.query.block_hash;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "system/events", blockHash);
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });

    // Custom Endpoints
    app.get('/api/custom/getSlashAmount', async function (req, res) {
        console.log('Received request for /api/custom/getSlashAmount');
        try {
            // extract the web socket passed in the query
            const websocket = req.query.websocket;
            // extract the blockHash passed in the query (optional)
            const blockHash = req.query.block_hash;
            // extract the accountAddress passed in the query
            const accountAddress = req.query.account_address;
            // check whether an api has been connected for that websocket
            if (websocket in apis){
                const apiResult = await substrateQuery.queryAPI(apis[websocket],
                    "custom/getSlashAmount", blockHash, accountAddress);
                if ('result' in apiResult) {
                    return res.status(REQUEST_SUCCESS_STATUS).send(apiResult);
                } else {
                    return res.status(REQUEST_ERROR_STATUS).send(apiResult);
                }
            } else {
                return res.status(REQUEST_ERROR_STATUS).send(
                    errorNeedToSetUpAPIMsg(websocket))
            }
        } catch (e) {
            return res.status(REQUEST_ERROR_STATUS).send(
                {'error': e.toString()});
        }
    });
}

startPolkadotAPI();
