# Model Assumptions

While the model implements the official Ethereum Specification wherever possible - see [README](README.md) for latest implemented release version - and allows for the computational simulation of many different assumption scenarios, the model does rest on a few validator-level assumptions by default, described in this document and to a large degree sourced from the extensive research done in the context of the well-known [Hoban/Borgers Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). We adapted some of these assumptions to reflect the evolution of the Ethereum protocol (e.g., Altair updates), and added new ones due to the nature of our dynamcial systems modeling paradigm (e.g., time-dependent, dynamic variables). The [Experiment Notebook: Model Validation](experiments\notebooks\1_model_validation.ipynb) validates selected outputs of the CADLabs model against the Hoban/Borgers model to allow for efficient sanity checks. 

* [Validator environment assumptions](#validator-environment-assumptions)
    * [Validator environment categories and cost structures](#validator-environment-categories-and-cost-structures)
    * [Validator environment relative weights](#validator-environment-relative-weights)
    * [Validator environment equal slashing assumption](#validator-environment-equal-slashing-assumption)
    * [Validator environment equal uptime assumption](#validator-environment-equal-uptime-assumption)
* [Validator performance assumptions](#validator-performance-assumptions)
    * [Average uptime](#average-uptime)
    * [Frequency of slashing events](#frequency-of-slashing-events)
    * [Participation rate](#participation-rate)

## Validator environment assumptions

The model supports the simulation of validator economics across different "validator environments" to account for the different deployment setups validators are using to access the network, each with slightly different economics. 

### Validator environment categories and cost structures

By default, the model implements the 7 validators environment categories as suggested by 
[Hoban/Borgers Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). Below is a short characterization of each category. For the respective cost assumption details, please refer to ["Cost of Validating"](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE/edit#gid=1220504079).

Across both hardware and cloud setups, the following requirements are assumed:
- Processor: Intel Core i7–4770 or AMD FX-8310 or better
- Memory: 8GB RAM
- Storage: 100GB available space SSD
- Internet: Broadband connection

1. **Run own hardware validator ("DIY-Hardware")**
- Setup: Validator running their own hardware
- Economics: Validator receives full revenue yield and carries full hardware, electricity, and bandwidth cost
- Example: Self-managed hardware (see hardware/cloud specifications above)

2. **Run own cloud validator ("DIY-Cloud")**
- Setup: Validator running their node on a cloud service
- Economics: Validator receives full revenue yield and carries cost of cloud service
- Example: AWS (see hardware/cloud specifications above)

3. **Validate via a pool Staking-as-a-Service provider ("Pool-StaaS")**
- Setup: Validator staking indirectly in a pool of validators via a Staking-as-a-service provider with infrastructure and keys managed by provider
- Economics: Costs (hardware, electricity, and bandwidth) carried by StaaS provider who charge a fee (percentage of revenue) to the validators
- Example: Rocket Pool (Pool) - https://www.rocketpool.net/

4. **Validate via a pool hardware service provider ("Pool-Hardware")**
- Setup: Validators pool ETH together on a node on own hardware and manage infrastructure and keys themselves
- Economics: Costs (hardware, electricity, and bandwidth) and revenue yield shared amongst validators in pool
- Example: Self-managed hardware (see hardware/cloud specifications above)

5. **Validate via a pool cloud provider ("Pool-Cloud")**
- Setup: Validators pool ETH together on a node on a cloud service and manage infrastructure and keys themselves 
- Economics: Costs (hardware, electricity, and bandwidth) and revenue yield shared amongst validators in pool
- Example: AWS (see hardware/cloud specifications above)

6. **Validate via a custodial Staking-as-a-Service provider ("StaaS-Full")**
- Setup: Validator stakes full amount (32 ETH) on own node via a custodial Staking-as-a-Service provider with infrastructure and keys managed by provider
- Economics: Costs (hardware, electricity, and bandwidth) carried by StaaS provider who charge a fee (percentage of revenue) to the validators
- Example: N/A

7. **Validate via a non-custodial Staking-as-a-Service provider ("StaaS-Self-custodied")**
- Setup: Validator stakes full amount (32 ETH) on own node via a non-custodial Staking-as-a-Service provider with infrastructure managed by provider
- Economics: Costs carried by StaaS provider who charge a fee (percentage of revenue) to the validators (assumed lower cost than Staas-Full environment)
- Example: Attestant "Managed Staking Service" - https://www.attestant.io/service/

The model allows for the creation of **custom validator environments and cost-structures**. These can be configured in the model's [System Parameters](model/system_parameters.py) as part of the `validator_environments` variable.

For more information about active validator staking services, see https://beaconcha.in/stakingServices.

### Validator environment relative weights

By default, the model assumes the following relative weights for the calculation of average validator revenue and profit yields, as defined by 
[Hoban/Borgers' Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). These values could change substantially and the user is encouraged to experiment with other assumptions. 

1. **Run own hardware validator ("DIY-Hardware")**: 37%
2. **Run own cloud validator ("DIY-Cloud")**: 13%
3. **Validate via a pool Staking-as-a-Service provider ("Pool-Staas")**: 27%
4. **Validate via a pool hardware service provider ("Pool-Hardware")**: 5%
5. **Validate via a pool Cloud providers ("Pool-Cloud")**: 2%
6. **Validate via a custodial Staking-as-a-Service provider ("StaaS-Full")**: 8%
7. **Validate via a non-custodial Staking-as-a-Service provider ("StaaS-Self-custodied")**: 8%

### Validator Environment Equal Slashing Assumption

Whereas in reality slashing events have occurred more often in some validator environments (e.g. institutional players getting their setup wrong and double-signing), we make the simplifying assumption that slashing events are applied equally across all validator environment types.

This assumption is adequate for calculations of validator economics under steady-state conditions, but might fail if slashing events increase significantly for a specific validator environment type, or if the network is under attack by a specific validator environment type.

See https://youtu.be/iaAEGs1DMgQ?t=574 for additional contexts. 

### Validator Environment Equal Uptime Assumption

Whereas we arguably expect better uptime for some validator environments than others (e.g. better for cloud environments than local hardware environments), we make the simplifying assumption that the same validator uptime is applied to all validator environments. Once respective data becomes available over time, this assumption could be dropped in future model iterations.

## Validator performance assumptions

### Average Uptime

By default, the model assumes an average of 98% uptime.

In reality this value has varied between lows of 95% and highs of 99.7% with an average of approximately 98%.

We capture the average uptime using the `validator_uptime_process` System Parameter - a function that returns the average uptime, which allows us to create stochastic or time-dependent uptime processes.

### Frequency of Slashing Events

By default, the model assumes 1 slashing event every 1000 epochs (~= 3 hours).

As more statistical data is collected about slashing in different validator environments, this assumption could be updated.

### Participation rate

The model assumes that validators are either online and operating perfectly, or offline and not fulfilling their duties. Offline validators are penalized for not attesting to the source, target, and head. We do not model validators that fullfil some of their duties, and not other duties. We capture this participation rate (percentage of online validators) using the `validator_uptime_process` System Parameter.

In its initial version, the model does not model Ethereum's inactivity leak mechanism. We assume a participation of more than 2/3 at all times. We assert this requirement in the `policy_validators(...)` Policy Function.
