const Timeout = require('await-timeout');

const TIMEOUT_TIME_MS = 10000;

// From: https://polkadot.js.org/api/substrate/storage.html
// Council
async function getCouncilMembers(api) {
    return await Promise.race([
        api.query.council.members(),
        Timeout.set(TIMEOUT_TIME_MS, 'API call council/members failed.')]);
}

async function getCouncilProposalCount(api) {
    return await Promise.race([
        api.query.council.proposalCount(),
        Timeout.set(TIMEOUT_TIME_MS,
            'API call council/proposalCount failed.')]);
}

async function getCouncilProposalOf(api, hash) {
    return await Promise.race([
        api.query.council.proposalOf(hash),
        Timeout.set(TIMEOUT_TIME_MS, 'API call council/proposalOf failed.')]);
}

async function getCouncilProposals(api) {
    return await Promise.race([
        api.query.council.proposals(),
        Timeout.set(TIMEOUT_TIME_MS, 'API call council/proposals failed.')]);
}

// Democracy
async function getDemocracyPublicPropCount(api) {
    return await Promise.race([
        api.query.democracy.publicPropCount(),
        Timeout.set(TIMEOUT_TIME_MS,
            'API call democracy/publicPropCount failed.')]);
}

async function getDemocracyReferendumCount(api) {
    return await Promise.race([
        api.query.democracy.referendumCount(),
        Timeout.set(TIMEOUT_TIME_MS,
            'API call democracy/referendumCount failed.')]);
}

async function getDemocracyReferendumInfoOf(api, referendumIndex) {
    return await Promise.race([
        api.query.democracy.referendumInfoOf(referendumIndex),
        Timeout.set(TIMEOUT_TIME_MS,
            'API call democracy/referendumInfoOf failed.')]);
}

// ImOnline
async function getImOnlineAuthoredBlocks(api, sessionIndex, validatorId) {
    return await Promise.race([
        api.query.imOnline.authoredBlocks(sessionIndex, validatorId),
        Timeout.set(TIMEOUT_TIME_MS,
            'API call imOnline/authoredBlocks failed.')]);
}

async function getImOnlineReceivedHeartBeats(api, sessionIndex, authIndex) {
    return await Promise.race([
        api.query.imOnline.receivedHeartbeats(sessionIndex, authIndex),
        Timeout.set(TIMEOUT_TIME_MS,
            'API call imOnline/receivedHeartbeats failed.')]);
}

// Session
async function getSessionCurrentIndex(api) {
    return await Promise.race([
        api.query.session.currentIndex(),
        Timeout.set(TIMEOUT_TIME_MS, 'API call session/currentIndex failed.')]);
}

async function getSessionDisabledValidators(api) {
    return await Promise.race([
        api.query.session.disabledValidators(),
        Timeout.set(TIMEOUT_TIME_MS,
            'API call session/disabledValidators failed.')]);
}

async function getSessionValidators(api) {
    return await Promise.race([
        api.query.session.validators(),
        Timeout.set(TIMEOUT_TIME_MS, 'API call session/validators failed.')]);
}

// Staking
async function getStakingCurrentElected(api) {
    return await Promise.race([
        api.query.staking.currentElected(),
        Timeout.set(TIMEOUT_TIME_MS,
            'API call staking/currentElected failed.')]);
}

async function getStakingStakers(api, accountAddress) {
    return await Promise.race([
        api.query.staking.stakers(accountAddress),
        Timeout.set(TIMEOUT_TIME_MS, 'API call staking/stakers failed.')]);
}

// System
async function getSystemEvents(api, blockHash) {
    // check if blockHash has been provided or not
    if (blockHash) {
        return await Promise.race([
            api.query.system.events.at(blockHash),
            Timeout.set(TIMEOUT_TIME_MS, 'API call system/events failed.')]);
    } else {
        return await Promise.race([
            api.query.system.events(),
            Timeout.set(TIMEOUT_TIME_MS, 'API call system/events failed.')]);
    }
}

// Custom
async function getSlashAmount(api, blockHash, accountAddress) {
    let events;
    try {
        events = await getSystemEvents(api, blockHash);
    } catch (e) {
        throw 'API call custom/getSlashAmount failed.';
    }

    let slashAmount = 0;

    // check every event to look for a staking:Slash event
    for (const record of events) {
        // extract the event and the event types
        const event = record.event;

        // check if the current event is a staking:Slash event
        if (event.section == 'staking' && event.method == 'Slash') {
            const event_str = event.data.toString();
            // remove the [ and ] from the string.
            // split the string into two elements by the ','
            const event_arr = event_str.slice(1, event_str.length-1).split(',');
            // remove the " from the ends of the account id
            event_arr[0] = event_arr[0].slice(1,event_arr[0].length-1);

            // check if the accountAddress of the current slashing event is the
            // one being queried
            if (event_arr[0] == accountAddress) {
                // if it is, add the slashed amount in the event to the total
                slashAmount += parseInt(event_arr[1]);
            }
        }
    }
    return slashAmount;
}


module.exports = {
    queryAPI: async function (api, param1=null, param2=null, param3=null) {
        switch (param1) {
            // Council
            case 'council/members':
                try {
                    return {'result': await getCouncilMembers(api)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            case 'council/proposalCount':
                try {
                    return {'result': await getCouncilProposalCount(api)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            case 'council/proposalOf':
                if (!param2) {
                    return {'error': 'You did not enter the hash.'};
                }
                try {
                    return {'result': await getCouncilProposalOf(api, param2)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            case 'council/proposals':
                try {
                    return {'result': await getCouncilProposals(api)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            // Democracy
            case 'democracy/publicPropCount':
                try {
                    return {'result': await getDemocracyPublicPropCount(api)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            case 'democracy/referendumCount':
                try {
                    return {'result': await getDemocracyReferendumCount(api)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            case 'democracy/referendumInfoOf':
                if (!param2) {
                    return {'error': 'You did not enter the referendum index.'};
                }
                try {
                    return {'result': await getDemocracyReferendumInfoOf(api,
                            param2)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            // ImOnline
            case 'imOnline/authoredBlocks':
                if (!param2) {
                    return {'error': 'You did not enter the session index.'};
                }
                if (!param3){
                    return {'error': 'You did not enter the stash account '
                            + 'address of the validator that needs to be '
                            + 'queried'};
                }
                try {
                    return {'result': await getImOnlineAuthoredBlocks(api,
                            param2, param3)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            case 'imOnline/receivedHeartbeats':
                if (!param2) {
                    return {'error': 'You did not enter the session index.'};
                }
                if (!param3){
                    return {'error': 'You did not enter the index of the ' +
                            'validator in the list returned by ' +
                            'session.validators()'};
                }
                try {
                    return {'result': await getImOnlineReceivedHeartBeats(api,
                            param2, param3)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            // Session
            case 'session/currentIndex':
                try {
                    return {'result': await getSessionCurrentIndex(api)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            case 'session/disabledValidators':
                try {
                    return {'result': await getSessionDisabledValidators(api)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            case 'session/validators':
                try {
                    return {'result': await getSessionValidators(api)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            // Staking
            case 'staking/currentElected':
                try {
                    return {'result': await getStakingCurrentElected(api)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            case 'staking/stakers':
                if (!param2) {
                    return {'error': 'You did not enter the stash account '
                            + 'address of the validator that needs to be '
                            + 'queried'};
                }
                try {
                    return {'result': await getStakingStakers(api, param2)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            // System
            case 'system/events':
                try {
                    return {'result': await getSystemEvents(api, param2)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            // Custom Endpoints
            case 'custom/getSlashAmount':
                try {
                    if (!param3) {
                        return {'error': 'You did not enter the account '
                                + 'address of the validator that needs to be '
                                + 'queried'};
                    }
                    return {'result': await getSlashAmount(api, param2,
                            param3)};
                } catch (e) {
                    return {'error': e.toString()};
                }
            default:
                if (!param1) {
                    return {'error': 'You did not enter a method.'};
                } else {
                    return {'error': 'Invalid API method.'};
                }
        }
    }
};
