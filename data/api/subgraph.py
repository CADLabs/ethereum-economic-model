import requests
import diskcache
import json
import logging
import os
from statistics import mean
from dotenv import load_dotenv
from collections import defaultdict

from model.constants import epochs_per_day, gwei, eth_deposited_per_validator

load_dotenv()
cache = diskcache.Cache(".api.cache")


@cache.memoize(expire=(24 * 60 * 60))  # cached for 24 hours
def get_6_month_validator_deposit_data():
    SUBGRAPH_API_KEY = os.getenv("SUBGRAPH_API_KEY")
    if SUBGRAPH_API_KEY:
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
            return r.json().get("data", {})
        except requests.exceptions.HTTPError as err:
            logging.error(err)
            return {}
    else:
        logging.warn("SUBGRAPH_API_KEY not defined")
        return {}


def get_6_month_mean_validator_deposits_per_epoch(default=None):
    data = get_6_month_validator_deposit_data()
    if not data:
        return default

    daily_deposits_data = data["dailyDeposits"]
    res = defaultdict(list)
    {res[key].append(sub[key]) for sub in daily_deposits_data for key in sub}
    daily_deposits = dict(res)
    daily_deposits["dailyAmountDepositedValidators"] = [
        float(x) / (eth_deposited_per_validator * gwei)
        for x in daily_deposits["dailyAmountDeposited"]
    ]
    mean_validator_deposits_per_epoch = (
        mean(daily_deposits["dailyAmountDepositedValidators"]) / epochs_per_day
    )
    return mean_validator_deposits_per_epoch
