# Introduction

A modular dynamical-systems model of Ethereum's validator economics, based on the open-source Python library [radCAD](https://github.com/CADLabs/radCAD), an extension to [cadCAD](https://cadcad.org).

This open-source model was developed in collaboration with the Ethereum Robust Incentives Group and funded by an Ethereum ESP (Ecosystem Support Program) grant. While originally scoped with purely modelling-educational intent as part of the cadCAD Edu online course "[cadCAD Masterclass: Ethereum Validator Economics](https://www.cadcad.education/course/masterclass-ethereum)", it has evolved to become a highly versatile, customizable and extensible research model that includes a list of [model extension ideas](#Model-Extension-Roadmap). The model is focused on epoch- and population-level Ethereum validator economics across different deployment types and – at least in its initial setup – abstracts from slot- and agent-level dynamics. Please see [Model Assumptions](ASSUMPTIONS.md) for further context.

* GitHub repo: [CADLabs Ethereum Economic Model](https://github.com/CADLabs/ethereum-economic-model)
* Latest model release version: [Subgraph / v1.1.7](https://github.com/CADLabs/ethereum-economic-model/releases/tag/v1.1.7)
* Implements the official Ethereum [Altair](https://github.com/ethereum/eth2.0-specs#altair) spec updates in the [Blue Loop / v1.1.0-alpha.7](https://github.com/ethereum/eth2.0-specs/releases/tag/v1.1.0-alpha.7) release

## Model Features

* Configurable to reflect protocol behaviour at different points in time of the development roadmap (referred to as "upgrade stages"):
  * Post Beacon Chain launch, pre EIP-1559, pre PoS (validators receive PoS incentives, EIP-1559 disabled, and PoW still in operation)
  * Post Beacon Chain launch, post EIP-1559, pre PoS (validators receive PoS incentives, EIP-1559 enabled with miners receiving priority fees, and PoW still in operation)
  * Post Beacon Chain launch, post EIP-1559, post PoS (validators receive PoS incentives, EIP-1559 enabled with validators receiving priority fees, and PoW deprecated)
* Flexible calculation granularity: By default, State Variables, System Metrics, and System Parameters are calculated at epoch level and aggregated daily (~= 225 epochs). Users can easily change epoch aggregation using the delta-time (`dt`) parameter. The model can be extended for slot-level granularity and analysis if that is desired (see [Model Extension Roadmap](#Model-Extension-Roadmap)).
* Supports [state-space analysis](https://en.wikipedia.org/wiki/State-space_representation) (i.e. simulation of system state over time) and [phase-space analysis](https://en.wikipedia.org/wiki/Phase_space) (i.e. generation of all unique system states in a given experimental setup).
* Customizable processes to set important variables such as ETH price, ETH staked, and EIP-1559 transaction pricing.
* Modular model structure for convenient extension and modification. This allows different user groups to refactor the model for different purposes, rapidly test new incentive mechanisms, or update the model as Ethereum implements new protocol improvements.
* References to official [Eth2 specs](https://github.com/ethereum/eth2.0-specs) in Policy and State Update Function logic. This enables seamless onboarding of protocol developers and allows the more advanced cadCAD user to dig into the underlying protocol design that inspired the logic.
