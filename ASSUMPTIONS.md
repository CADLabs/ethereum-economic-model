# Model Assumptions

While the model implements the official Ethereum Specification wherever possible – see [README](README.md) for latest implemented release version – and allows for the computational simulation of many different assumption scenarios, the model does rest on a few validator-level assumptions by default, described in this document and to a large degree sourced from the extensive research done in the context of the well-known [Hoban/Borgers Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). We adapted some of these assumptions to reflect the evolution of the Ethereum protocol (e.g., Altair updates) and added new ones due to the nature of our dynamical-systems-modelling paradigm (e.g. time-dependent, dynamic variables). The [Experiment Notebook: Model Validation](experiments\notebooks\1_model_validation.ipynb) validates selected outputs of the CADLabs model against the Hoban/Borgers model to allow for efficient sanity checks. 

* [Validator Environment Assumptions](#Validator-Environment-Assumptions)
    * [Validator Environment Categories and Cost Structures](#Validator-Environment-Categories-and-Cost-Structures)
    * [Validator Environment Relative Weights](#Validator-Environment-Relative-Weights)
    * [Validator Environment Equal-slashing Assumption](#Validator-Environment-Equal-slashing-Assumption)
    * [Validator Environment Equal-uptime Assumption](#Validator-Environment-Equal-uptime-Assumption)
* [Validator Performance Assumptions](#Validator-Performance-Assumptions)
    * [Average Uptime](#Average-Uptime)
    * [Frequency of Slashing Events](#Frequency-of-Slashing-Events)
    * [Participation Rate](#Participation-Rate)

## Validator Environment Assumptions

The model supports the simulation of validator economics across different "validator environments" to account for the different deployment setups validators are using to access the network, each with slightly different economics. 

### Validator Environment Categories and Cost Structures

By default, the model implements the 7 validator environment categories as suggested by 
[Hoban/Borgers Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). Below is a short characterization of each category. For the respective cost-assumption details, please refer to ["Cost of Validating"](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE).

The following recommended specifications were used for guidance across both hardware and cloud setups. See report for a more detailed breakdown.
- Processor: Intel Core i7–4770 or AMD FX-8310 or better
- Memory: 8GB RAM
- Storage: 100GB available space SSD
- Internet: Broadband connection

1. **Run own hardware validator ("DIY-Hardware")**
- Setup: Individual running a Beacon Node and Validator Client with multiple Validators on their own hardware
- Economics: Individual receives full revenue yields and carries full hardware, electricity, and bandwidth cost
- Example: Self-managed hardware (see hardware/cloud specifications above)

2. **Run own cloud validator ("DIY-Cloud")**
- Setup: Individual running a Beacon Node and Validator Client with multiple Validators on a cloud service
- Economics: Individual receives full revenue yields and carries cost of cloud service, with costs shared amongst multiple Validators for a lower cost per Validator compared to DIY hardware
- Example: AWS (see hardware/cloud specifications above)

3. **Validate via a pool Staking-as-a-Service provider ("Pool-StaaS")**
- Setup: Individual staking less than 32 ETH indirectly in a pool of Validators via a Staking-as-a-Service provider with infrastructure (Beacon Node and Validator Client) and keys managed by provider
- Economics: Costs (hardware, electricity, and bandwidth) carried by StaaS provider who charges a fee (percentage of revenue) to the Validators in pool
- Example: Rocket Pool (Pool) - https://www.rocketpool.net/

4. **Validate via a pool hardware service provider ("Pool-Hardware")**
- Setup: A node operator hosts both a Beacon Node and Validator Client on their own hardware infrastructure, and pools ETH together from Stakers to create multiple Validators
- Economics: Costs (hardware, electricity, and bandwidth) and revenue yields shared amongst Validators in pool
- Example: Self-managed hardware (see hardware/cloud specifications above)

5. **Validate via a pool cloud provider ("Pool-Cloud")**
- Setup: A node operator hosts both a Beacon Node and Validator Client on their own cloud infrastructure, and pools ETH together from Stakers to create multiple Validators
- Economics: Costs (hardware, electricity, and bandwidth) and revenue yields shared amongst Validators in pool
- Example: AWS (see hardware/cloud specifications above)

6. **Validate via a custodial Staking-as-a-Service provider ("StaaS-Full")**
- Setup: Validator stakes full amounts of 32 ETH via a custodial Staking-as-a-Service provider, that manages both the Validator Client and Beacon Node
- Economics: Operational costs (hardware, electricity, and bandwidth) carried by StaaS provider who charges a fee (percentage of revenue) to the Validators
- Example: Attestant "Managed Staking Service" - https://www.attestant.io/service/

7. **Validate via a non-custodial Staking-as-a-Service provider ("StaaS-Self-custodied")**
- Setup: Validator stakes full amounts of 32 ETH using own Validator Client, but instead of running a Beacon Node themselves they opt to use a StaaS Beacon Node provider via an API
- Economics: Beacon Node operational costs (hardware, electricity, and bandwidth) carried by StaaS provider who charges a fee (percentage of revenue) to the Validators (assumes lower cost than Staas-Full environment)
- Example: Attestant "Managed Staking Service" - https://www.attestant.io/service/

The model allows for the creation of **custom validator environments and cost-structures**. These can be configured in the model's [System Parameters](model/system_parameters.py) as part of the `validator_environments` variable.

For more information about currently active validator staking services, see https://beaconcha.in/stakingServices.

### Validator Environment Relative Weights

By default, the model assumes the following relative weights for the calculation of average validator revenue and profit yields, as defined by 
[Hoban/Borgers' Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). These values could change substantially and the user is encouraged to experiment with other assumptions. 

1. **Run own hardware validator ("DIY-Hardware")**: 37%
2. **Run own cloud validator ("DIY-Cloud")**: 13%
3. **Validate via a pool Staking-as-a-Service provider ("Pool-Staas")**: 27%
4. **Validate via a pool hardware service provider ("Pool-Hardware")**: 5%
5. **Validate via a pool Cloud provider ("Pool-Cloud")**: 2%
6. **Validate via a custodial Staking-as-a-Service provider ("StaaS-Full")**: 8%
7. **Validate via a non-custodial Staking-as-a-Service provider ("StaaS-Self-custodied")**: 8%

### Validator Environment Equal-slashing Assumption

Whereas in reality slashing events have occurred more often in some validator environments (e.g. institutional players getting their setup wrong and double-signing), we make the simplifying assumption that slashing events are applied equally across all validator-environment types.

This assumption is adequate for calculations of validator economics under steady-state conditions but might fail if slashing events increase significantly for a specific validator-environment type, or if the network is under attack by a specific validator-environment type.

See https://youtu.be/iaAEGs1DMgQ?t=574 for additional context. 

### Validator Environment Equal-uptime Assumption

Whereas we arguably expect better uptime for some validator environments than others (e.g. better for cloud environments than local hardware environments), we make the simplifying assumption that the same validator uptime is applied to all validator environments. Once respective data becomes available over time, this assumption could be dropped in future model iterations.

## Validator Performance Assumptions

### Average Uptime

By default, the model assumes an average of 98% uptime.

In reality, this value has varied between lows of 95% and highs of 99.7% with an average of approximately 98%.

We capture the average uptime using the `validator_uptime_process` System Parameter – a function that returns the average uptime and allows us to create stochastic or time-dependent uptime processes.

### Frequency of Slashing Events

By default, the model assumes 1 slashing event every 1000 epochs (~= 3 hours).

As more statistical data is collected about slashing in different validator environments, this assumption could be updated.

### Participation Rate

The model assumes that validators are either online and operating perfectly, or offline and not fulfilling their duties. Offline validators are penalized for not attesting to the source, target, and head. We do not model validators that fulfil some of their duties, and not other duties. We capture this participation rate (percentage of online validators) using the `validator_uptime_process` System Parameter.

In its initial version, the model does not model Ethereum's inactivity mechanism. We assume a participation of more than 2/3 at all times. We assert this requirement in the `policy_validators(...)` Policy Function.
