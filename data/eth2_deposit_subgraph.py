# For parsing the data from the API
import json
# For downloading data from API
import requests as req


API_URI = 'https://thegraph.com/explorer/subgraph/attestantio/eth2deposits'

GRAPH_QUERY = '''
{
  deposits(orderBy: index, orderDirection: asc) {
    id
    index
    transactionHash
    validatorPubKey
    amount
  }
}
'''

JSON = {'query': GRAPH_QUERY}

response = req.post(API_URI, json=JSON)
data = json.loads(response.content)['data']

from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/<infura-project-id>'))

# > web3.eth.getTransaction(tx).blockNumber
# 1920050
# > web3.eth.getBlock(1920050).timestamp
# 1469021581
