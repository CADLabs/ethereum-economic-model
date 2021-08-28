import requests
import diskcache
import json
import logging
import os
from statistics import mean
from dotenv import load_dotenv
from collections import defaultdict

from model.constants import epochs_per_day

load_dotenv()
cache = diskcache.Cache(".beaconchain_api.cache")


@cache.memoize(expire=(6 * 60 * 60))  # cached for 6 hours
def get_6_month_eth_deposit_data():
    SUBGRAPH_API_KEY = os.getenv("SUBGRAPH_API_KEY")
    API_URI = (
        "https://gateway.thegraph.com/api/"
        + SUBGRAPH_API_KEY
        + "/subgraphs/id/0x540b14e4bd871cfe59e48d19254328b5ff11d820-0"
    )
    GRAPH_QUERY = """
    {
    dailyDeposits(first: 180) {
        id
        dailyAmountDeposited
        }
    }
    """
    try:
        JSON = {"query": GRAPH_QUERY}
        r = requests.post(API_URI, json=JSON)
        return r.json()["data"]
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return {}


def get_6_month_mean_validator_deposits_per_epoch(default=None):
    data = get_6_month_eth_deposit_data()
    daily_deposits_data = data["dailyDeposits"]
    res = defaultdict(list)
    {res[key].append(sub[key]) for sub in daily_deposits_data for key in sub}
    daily_deposits = dict(res)
    daily_deposits["dailyAmountDepositedValidators"] = [
        (float(x) * 1e-9) / 32 for x in daily_deposits["dailyAmountDeposited"]
    ]
    mean_validator_deposits_per_epoch = (
        mean(daily_deposits["dailyAmountDepositedValidators"]) / epochs_per_day
    )
    return mean_validator_deposits_per_epoch
