# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2021-07-28
### Changed
- Default assumption for `base_fee_process` System Parameter
- Default assumption for `priority_fee_process` System Parameter
- Experiment notebook 2, "Validator Revenue and Profit Yields": updated time-domain simulations to run over all stages

### Added
- `realized_mev_per_block` System Parameter
- Maximum Extractable Value (MEV) Policy Function
- "Ethereum Network Assumptions" and "Ethereum Transaction & EIP-1559 Assumptions" added to [ASSUMPTIONS.md](ASSUMPTIONS.md) doc
- Additional datasets in [data/](data/): Historical Ethereum Average Gas Price, Historical Ethereum Block Rewards, Daily Extracted MEV, Historical Ethereum Gas Used

## [1.0.0] - 2021-07-15
### Changed
- The model is public!

## [0.1.2] - 2021-04-29
### Changed
- Refactor of EIP1559 mechanism
- Various refactors post-review

## [0.1.1] - 2021-04-05
### Added
- Test for Proof of Stake inclusion distance

### Changed
- Reformatting of model code according to Black/PEP8 standards
- Minor refactors after milestone 1 mathematical specification submission

### Removed
- Removed unused system parameters

## [0.1.0] - 2021-03-21
### Added
- Initial MVP model implementation

## Example version log: [0.0.0] - XXXX-XX-XX
### Added
- foo

### Changed
- bar

### Removed
- foo bar
