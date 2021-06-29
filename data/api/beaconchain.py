import requests
import diskcache

from model.types import Gwei


cache = diskcache.Cache('.beaconchain_api.cache')


@cache.memoize(expire=(6 * 60 * 60))  # cached for 6 hours
def get_epoch_data(epoch="latest"):
    return requests.get(f"https://beaconcha.in/api/v1/epoch/{epoch}", headers={"accept":"application/json"}).json()["data"]


def get_total_validator_balance(default=None) -> Gwei:
    result = int(get_epoch_data()["totalvalidatorbalance"])
    return result if result else default


def get_validators_count(default=None) -> int:
    result = int(get_epoch_data()["validatorscount"])
    return result if result else default
