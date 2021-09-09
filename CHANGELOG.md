# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.7] - 2021-09-09
### Changed
- Fixed circular dependency in notebooks causing tests to fail

## [1.1.6] - 2021-09-06
### Added
- The Graph Subgraph for validator adoption

## [1.1.5] - 2021-09-04
### Changed
- Updated to radCAD v0.8.4
- Published cadCAD Masterclass Capstone Exercise notebook

## [1.1.4] - 2021-09-03
### Changed
- Various minor tweaks for cadCAD Edu, cadCAD Masterclass: Ethereum Validator Economics

## [1.1.3] - 2021-08-30
### Changed
- Update radCAD from v0.8.2 to v0.8.3
- Update `date_pos` parameter to frontend default of 2022/03/1
- Update cumulative yield chart experiment template from daily to monthly aggregation

## [1.1.2] - 2021-08-28
### Added
- Documentation for 5th chart of notebook 2, "Validator Revenue and Profit Yields", analysis 1
- Anaconda environment setup docs and `environment_setup.ipynb` notebook

### Changed
- Updated radCAD from version 0.8.1 to 0.8.2
- Default `stage` System Parameter from `PROOF_OF_STAKE` to `ALL`
- Moved `model.simulation_configuration` to `experiments.simulation_configuration`
- Renamed `inspect_module(...)` function to `display_code(...)`

## [1.1.1] - 2021-08-09
### Changed
- Updated System Parameter configuration for `mev_per_block` in notebook 2, "Validator Revenue and Profit Yields", from 0.13 to 0.02 ETH/block

## [1.1.0] - 2021-07-28
### Changed
- Default assumption for `base_fee_process` System Parameter
- Default assumption for `priority_fee_process` System Parameter
- Experiment notebook 2, "Validator Revenue and Profit Yields": updated time-domain simulations to run over all stages

### Added
- `mev_per_block` System Parameter
- Maximum Extractable Value (MEV) Policy Function
- "Ethereum Network Assumptions" and "Ethereum Transaction & EIP-1559 Assumptions" added to [ASSUMPTIONS.md](ASSUMPTIONS.md) doc
- Additional datasets in [data/](data/): Historical Ethereum Average Gas Price, Historical Ethereum Block Rewards, Daily Extracted MEV, Historical Ethereum Gas Used

## [1.0.0] - 2021-07-15
### Changed
- The model is public!

## [0.1.2] - 2021-04-29
### Changed
- Refactor of EIP-1559 mechanism
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
