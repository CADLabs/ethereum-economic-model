# Model Assumptions

While the model implements the official Ethereum Specification wherever possible - see the [README](README.md) for release version - and allows for the computational simulation of many different assumption scenarios, the model does rest on several validator-level assumptions by default. These validator-level assumptions are mostly taken from the well-known [Hoban/Borgers Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). The underlying desk and survey research is very extensive. We adapted some of these assumptions to reflect the evolution of the Ethereum protocol (e.g., Altair updates), and added new ones due to the nature of our dynamcial systems modeling paradigm (e.g., time-dependent, dynamic variables). The [Experiment Notebook: Model Validation](experiments\notebooks\1_model_validation.ipynb) validates selected _outputs_ of the CADLabs model against the Hoban/Borgers model to allow for efficient sanity checks. 

* [Validator environment assumptions](#validator-environment-assumptions)
    * [Validator environment categories and cost structures](#validator-environment-categories-and-cost-structures)
    * [Validator environment relative weights](#validator-environment-relative-weights)
    * [Validator environment equal slashing assumption](#validator-environment-equal-slashing-assumption)
    * [Validator environment equal uptime assumption](#validator-environment-equal-uptime-assumption)
* [Validator performance assumptions](#validator-performance-assumptions)
    * [Average uptime](#average-uptime)
    * [Frequency of slashing events](#frequency-of-slashing-events)
    * [Participation rate](#participation-rate)
* [Epoch level granularity](#epoch-level-granularity)

## Validator environment assumptions

The model supports the simulation of validator economics across different "validator environments" to account for the different deployment setups validators are using to access the network, each with slightly different economics. 

### Validator environment categories and cost structures

By default, the model implements the 7 validators environment categories and associated cost structures as defined by 
[Hoban/Borgers Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). Below is a short charaterization of each environment. For the associated cost assumptions please refer to the tab "Cost of Validating" in [Hoban/Borgers model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE/edit#gid=1220504079).

1. **Run own hardware validator ("DIY-Hardware")**
- Setup: Validator running their own hardware
- Economics: Validator receives full revenue yield and carries full hardware, electricity, and bandwidth cost
- Example: Raspberry Pi

2. **Run own cloud validator ("DIY-Cloud")**
- Setup: Validator running their node on a cloud service
- Economics: Validator receives full revenue yield and carries cost of cloud service
- Example: AWS

3. **Validate via a pool Staking-as-a-Service provider ("Pool-StaaS")** - TODO: Clearly describe 3 vs 4 vs. 5
- Setup: Validator staking indirectly in a Pool of validators
- Economics: Costs carried by StaaS provider who charge a fee (percentage of revenue) to the validators
- Example: Rocket Pool - https://www.rocketpool.net/

4. **Validate via a pool hardware service provider ("Pool-Hardware")** - TODO: Clearly describe 3 vs 4 vs. 5
- Setup: Validator staking directly 
- Economics: TODO
- Example: TODO

5. **Validate via a pool cloud provider ("Pool-Cloud")**- TODO: Clearly describe 3 vs 4
- Setup: TODO 
- Economics: TODO
- Example: TODO

6. **Validate via a custodial Staking-as-a-Service provider ("StaaS-Full")**
- Setup: Validator stakes full amount (32 ETH) on own node via a Staking-as-a-Service provider with infrastructure and keys managed by provider
- Economics: Costs carried by StaaS provider who charge a fee (percentage of revenue) to the validators
- Example: TODO

7. **Validate via a non-custodial Staking-as-a-Service provider ("StaaS-Self-custodied")**
- Setup: Validator stakes full amount (32 ETH) on own node via a Staking-as-a-Service provider with infrastructure managed by provider
- Economics: Costs carried by StaaS provider who charge a fee (percentage of revenue) to the validators (assumed lower cost than Staas-Full environment)
- Example: Attestant "Managed Staking Service" - https://www.attestant.io/service/

The model allows for the creation of a custom validator environment and/or cost-structures. (TODO: Validate how? Describe more?)

### Validator environment relative weights

By default, the model assumes the following relative weights for the calculation of average validator revenue and profit yields, as defined by 
[Hoban/Borgers' Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). These values could change substantially and the user is encouraged to experiment with other assumptions. 

1. **Run own hardware validator ("DIY-Hardware")**: 37%
2. **Run own cloud validator ("DIY-Cloud")**: 13%
3. **Validate via a pool Staking-as-a-Service provider ("Pool-Staas")**: 27% - TODO: Clearly describe 3 vs 4 vs. 5
4. **Validate via a pool hardware service provider ("Pool-Hardware")**: 5% - TODO: Clearly describe 3 vs 4 vs. 5
5. **Validate via a pool Cloud providers ("Pool-Cloud")**: 2% TODO: Clearly describe 3 vs 4
6. **Validate via a custodial Staking-as-a-Service provider**: 8% ("StaaS-Full")
7. **Validate via a non-custodial Staking-as-a-Service provider**: 8% ("StaaS-Self-custoried")

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

## Epoch-level granularity

Unless specified otherwise, all State Variables, System Metrics, and System Parameters are time-dependent and calculated at epoch level granularity. For ease of notation, units of time will be assumed implicitly. In the model implementation, calculations can be aggregated across epochs where necessary - for example for performance reasons.

By default calculations will be aggregated across 1 day in epochs (~= 225 epochs), using the delta-time or `dt` parameter - the simulation results will have the same aggregation i.e. State Variables will be per-day, assuming `dt = 225`.
