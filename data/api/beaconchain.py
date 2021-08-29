import requests
import diskcache
import logging

from model.types import Gwei


cache = diskcache.Cache(".api.cache")


@cache.memoize(expire=(6 * 60 * 60))  # cached for 6 hours
def get_epoch_data(epoch="latest"):
    try:
        req = requests.get(
            f"https://beaconcha.in/api/v1/epoch/{epoch}",
            headers={"accept": "application/json"},
        )
        req.raise_for_status()
        return req.json()["data"]
    except requests.exceptions.HTTPError as err:
        logging.error(err)
        return {}


def get_total_validator_balance(default=None) -> Gwei:
    data = get_epoch_data()
    result = int(data.get("totalvalidatorbalance", default))
    return result


def get_validators_count(default=None) -> int:
    data = get_epoch_data()
    result = int(data.get("validatorscount", default))
    return result
