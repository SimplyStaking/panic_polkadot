import requests

# defining the api-endpoint
API_ENDPOINT = "http://localhost:3000"
# API_ENDPOINT = "http://172.16.151.78:3000"

# Miscellaneous Endpoints
print('Miscellaneous Endpoints:')

print('/api/pingApi')
r = requests.get(url=API_ENDPOINT + '/api/pingApi')
print(r.text)

print('/api/pingNode')
r = requests.get(url=API_ENDPOINT + '/api/pingNode',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/getConnectionsList')
r = requests.get(url=API_ENDPOINT + '/api/getConnectionsList')
print(r.text)

print()

# RPC API
# Chain
print('Chain:')

print('/api/rpc/chain/getBlockHash')
r = requests.get(url=API_ENDPOINT + '/api/rpc/chain/getBlockHash',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)
r = requests.get(url=API_ENDPOINT + '/api/rpc/chain/getBlockHash',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'block_number': '36430'})
print(r.text)

print('/api/rpc/chain/getFinalizedHead')
r = requests.get(url=API_ENDPOINT + '/api/rpc/chain/getFinalizedHead',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/rpc/chain/getHeader')
r = requests.get(url=API_ENDPOINT + '/api/rpc/chain/getHeader',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)
r = requests.get(url=API_ENDPOINT + '/api/rpc/chain/getHeader',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'hash': '0xdd661348a4971e0cf75d89da69de01907e81070cb8099dddc12b611c18371679'})
print(r.text)

# System
print('System:')

print('/api/rpc/system/chain')
r = requests.get(url=API_ENDPOINT + '/api/rpc/system/chain',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/rpc/system/health')
r = requests.get(url=API_ENDPOINT + '/api/rpc/system/health',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print()

# Query API
# Council
print('Council:')

print('/api/query/council/members')
r = requests.get(url=API_ENDPOINT + '/api/query/council/members',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/query/council/proposalCount')
r = requests.get(url=API_ENDPOINT + '/api/query/council/proposalCount',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/query/council/proposalOf')
r = requests.get(url=API_ENDPOINT + '/api/query/council/proposalOf',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'hash': 'boq'})
print(r.text)

print('/api/query/council/proposals')
r = requests.get(url=API_ENDPOINT + '/api/query/council/proposals',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

# Democracy
print('Democracy:')

print('/api/query/democracy/publicPropCount')
r = requests.get(url=API_ENDPOINT + '/api/query/democracy/publicPropCount',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/query/democracy/referendumCount')
r = requests.get(url=API_ENDPOINT + '/api/query/democracy/referendumCount',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/query/democracy/referendumInfoOf')
r = requests.get(url=API_ENDPOINT + '/api/query/democracy/referendumInfoOf',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'referendum_index': '1'})
print(r.text)

# ImOnline
print('ImOnline:')

print('/api/query/imOnline/authoredBlocks')
r = requests.get(url=API_ENDPOINT + '/api/query/imOnline/authoredBlocks',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'session_index': '3',
                         'validator_id': 'DNDBcYD8zzqAoZEtgNzouVp2sVxsvqzD4UdB5WrAUwjqpL8'})
print(r.text)

print('/api/query/imOnline/receivedHeartbeats')
r = requests.get(url=API_ENDPOINT + '/api/query/imOnline/receivedHeartbeats',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'session_index': '3',
                         'auth_index': '0'})
print(r.text)

# Session
print('Session:')

print('/api/query/session/currentIndex')
r = requests.get(url=API_ENDPOINT + '/api/query/session/currentIndex',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/query/session/disabledValidators')
r = requests.get(url=API_ENDPOINT + '/api/query/session/disabledValidators',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/query/session/validators')
r = requests.get(url=API_ENDPOINT + '/api/query/session/validators',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

# Staking
print('Staking:')

print('/api/query/staking/currentElected')
r = requests.get(url=API_ENDPOINT + '/api/query/staking/currentElected',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)

print('/api/query/staking/stakers')
r = requests.get(url=API_ENDPOINT + '/api/query/staking/stakers',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'account_address': 'DNDBcYD8zzqAoZEtgNzouVp2sVxsvqzD4UdB5WrAUwjqpL8'})
print(r.text)

# System
print('System:')

print('/api/query/system/events')
r = requests.get(url=API_ENDPOINT + '/api/query/system/events',
                 params={'websocket': 'ws://172.25.10.107:9944'})
print(r.text)
r = requests.get(url=API_ENDPOINT + '/api/query/system/events',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'block_hash': '0xdfee729e21118c625573189df270659e4513732224726a217cf323114db8cccd'})
print(r.text)

print()

# Custom
print('Custom:')

print('/api/custom/getSlashAmount')
r = requests.get(url=API_ENDPOINT + '/api/custom/getSlashAmount',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'account_address': 'HsGrsqL4nCBCW2ovc4kKG98c4mFp99BHRFkBSRZW1ETDe3U'})
print(r.text)
r = requests.get(url=API_ENDPOINT + '/api/custom/getSlashAmount',
                 params={'websocket': 'ws://172.25.10.107:9944',
                         'block_hash': '0xdfee729e21118c625573189df270659e4513732224726a217cf323114db8cccd',
                         'account_address': 'HsGrsqL4nCBCW2ovc4kKG98c4mFp99BHRFkBSRZW1ETDe3U'})
print(r.text)

print()
# Misc
print('Misc:')
r = requests.get(url=API_ENDPOINT + '/api/query/session/validators',
                 params={'websocket': 'ws://172.26.10.27:9944'})
print(r.text)

print()

# Invalid IP
r = requests.get(url=API_ENDPOINT + '/api/query/session/validators',
                 params={'websocket': 'ws://172.26.123.123:9944'})
print(r.text)

# r_text = r.text
# r_json = json.loads(r_text)
#
# print(r.text)
# print(r_json)
# print(r_json['result'])
