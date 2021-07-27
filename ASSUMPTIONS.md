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
* [Validator Adoption Assumptions](#validator-adoption-assumptions)
* [Ethereum Network Assumptions](#ethereum-network-assumptions)
* [Ethereum Transaction & EIP-1559 Assumptions](#ethereum-transaction--eip-1559-assumptions)

## Validator Environment Assumptions

The model supports the simulation of validator economics across different "validator environments" to account for the different deployment setups validators are using to access the network, each with slightly different economics. 

### Validator Environment Categories and Cost Structures

By default, the model implements the 7 validator environment categories as suggested by 
[Hoban/Borgers Ethereum 2.0 Economic Model](https://thomasborgers.medium.com/ethereum-2-0-economic-review-1fc4a9b8c2d9). Below is a short characterization of each category. For the respective hardware-setup and cost-assumption details, please refer to ["Cost of Validating"](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE).

1. **Run own hardware validator ("DIY-Hardware")**
- Setup: Individual running a Beacon Node and Validator Client with one or more Validators on their own hardware
- Economics: Individual receives full revenue yields and carries full hardware, electricity, and bandwidth cost

2. **Run own cloud validator ("DIY-Cloud")**
- Setup: Individual running a Beacon Node and Validator Client with one or more Validators on a cloud service
- Economics: Individual receives full revenue yields and carries cost of cloud service, with costs shared amongst multiple Validators for a lower cost per Validator compared to DIY hardware

3. **Validate via a pool Staking-as-a-Service provider ("Pool-StaaS")**
- Setup: Individual staking indirectly in a pool of Validators via a Staking-as-a-Service provider with infrastructure (Beacon Node and Validator Client) and keys managed by provider
- Economics: Costs (hardware, electricity, and bandwidth) carried by StaaS provider who charges a fee (percentage of revenue) to the Validators in pool

4. **Validate via a pool hardware service provider ("Pool-Hardware")**
- Setup: A node operator hosts both a Beacon Node and Validator Client on their own hardware infrastructure, and pools ETH together from Stakers to create multiple Validators
- Economics: Costs (hardware, electricity, and bandwidth) and revenue yields shared amongst Validators in pool

5. **Validate via a pool cloud provider ("Pool-Cloud")**
- Setup: A node operator hosts both a Beacon Node and Validator Client on their own cloud infrastructure, and pools ETH together from Stakers to create multiple Validators
- Economics: Costs (hardware, electricity, and bandwidth) and revenue yields shared amongst Validators in pool

6. **Validate via a custodial Staking-as-a-Service provider ("StaaS-Full")**
- Setup: Validator stakes via a custodial Staking-as-a-Service provider, that manages both the Validator Client and Beacon Node
- Economics: Operational costs (hardware, electricity, and bandwidth) carried by StaaS provider who charges a fee (percentage of revenue) to the Validators

7. **Validate via a non-custodial Staking-as-a-Service provider ("StaaS-Self-custodied")**
- Setup: Validator stakes using own Validator Client, but instead of running a Beacon Node themselves they opt to use a StaaS Beacon Node provider via an API
- Economics: Beacon Node operational costs (hardware, electricity, and bandwidth) carried by StaaS provider who charges a fee (percentage of revenue) to the Validators (assumes lower cost than Staas-Full environment)

This model allows for the creation of **custom validator environments and cost-structures**. These can be configured in the model's [System Parameters](model/system_parameters.py) as part of the `validator_environments` variable.

For more information about currently active validator staking services, see https://beaconcha.in/stakingServices.

### Validator Environment Relative Weights

By default, the model assumes the following relative weights for the calculation of average validator revenue and profit yields, as defined by 
[Hoban/Borgers' Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). These values could change substantially and the user is encouraged to experiment with other assumptions. 

1. Run own hardware validator ("DIY-Hardware"): **37%**
2. Run own cloud validator ("DIY-Cloud"): **13%**
3. Validate via a pool Staking-as-a-Service provider ("Pool-Staas"): **27%**
4. Validate via a pool hardware service provider ("Pool-Hardware"): **5%**
5. Validate via a pool Cloud provider ("Pool-Cloud"): **2%**
6. Validate via a custodial Staking-as-a-Service provider ("StaaS-Full"): **8%**
7. Validate via a non-custodial Staking-as-a-Service provider ("StaaS-Self-custodied"): **8%**

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

By default, the model assumes 1 slashing event every 1000 epochs.

As more statistical data is collected about slashing in different validator environments, this assumption could be updated.

### Participation Rate

The model assumes that validators are either online and operating perfectly, or offline and not fulfilling their duties. Offline validators are penalized for not attesting to the source, target, and head. We do not model validators that fulfil some of their duties, and not other duties. We capture this participation rate (percentage of online validators) using the `validator_uptime_process` System Parameter.

In its initial version, the model does not model Ethereum's inactivity leak mechanism. We assume a **participation of more than 2/3 at all times**. We assert this requirement in the `policy_validators(...)` Policy Function.

## Validator Adoption Assumptions

Validator adoption is the assumed rate of new validators entering the activation queue per epoch, that results in an implied ETH staked value over time.

The "Validator Revenue and Profit Yields" experiment notebook introduces three linear adoption scenarios (historical adoption has been approximately linear):
* Normal adoption: assumes an average of 3 new validators per epoch. These rates correspond to the historical average newly **activated** validators per epoch between 15 January 2021 and 15 July 2021 as per [Beaconscan](https://beaconscan.com/stat/validator).
* Low adoption: assumes an average of 1.5 new validators per epoch, i.e. a 50% lower rate compared to the base scenario
* High adoption: assumes an average of 4.5 new validators per epoch, i.e. a 50% higher rate compared to the base scenario

The normal adoption scenario is used as the default validator adoption rate for all experiments - to change this value, update the `validator_process` [System Parameter](./model/system_parameters.py).

## Ethereum Network Assumptions

### Ethereum Price

The ETH price is set to the mean daily price over the last 12 months from Etherscan.

This value is constant and calculated from a CSV file in the [data/](data/) directory, in the [data.historical_values](data/historical_values.py) module.

To change this value, update the `eth_price_process` [System Parameter](./model/system_parameters.py).

### Ethereum Issuance

The Ethereum issuance due to Proof-of-Work block rewards is set to the mean daily issuance over the last 12 months from Etherscan.

This value is constant and calculated from a CSV file in the [data/](data/) directory, in the [data.historical_values](data/historical_values.py) module.

To change this value, update the `daily_pow_issuance` [System Parameter](./model/system_parameters.py).

### Ethereum Network Upgrade Stage Assumptions

#### Simulation Start Date

The simulation start date can be set using the `date_start` [System Parameter](./model/system_parameters.py). By default, for time-domain analyses, the start date is set to the current date.

#### EIP-1559 Activation Date

EIP-1559 transaction pricing will be included as part of the [London mainnet upgrade](https://blog.ethereum.org/2021/07/15/london-mainnet-announcement/) on 4 August 2021. After this date, the simulation will activate the necessary EIP-1559 mechanisms.

To change this value, update the `date_eip1559` [System Parameter](./model/system_parameters.py).

#### Proof-of-Stake Activation Date ("The Merge")

The Ethereum researcher Justin Drake estimates a "best guess" of 1 December 2021 for the Proof-of-Stake activation date in his [ETH supply analysis](https://docs.google.com/spreadsheets/d/1ZN444__qkPWPjMJQ_t6FfqbhllkWNhHF-06ivRF73nQ). Launch dates are hard to predict, and for more rigorous analysis a range of values should be tested.

To change this value, update the `date_pos` [System Parameter](./model/system_parameters.py).

## Ethereum Transaction & EIP-1559 Assumptions

### Average Gas Used

With the introduction of [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) the current gas limit is replaced by two values:
* a “long-term average target” equal to the current gas limit
* a “hard per-block cap” which is twice the current gas limit

The long-term average gas target per block is set to 15m gas; by default we assume the gas used per block will on average be equal to the gas target. To change this value, update the `gas_target_process` [System Parameter](./model/system_parameters.py).

### Average Base Fee

The [EIP-1559 proposal](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md) defines a variable `max_fee_per_gas` to set a fee cap per transaction. This fee cap is the maximum fee in Gwei per gas a user will pay per transaction. This fee is made up of the base fee and a priority fee, where the base fee is burned and the priority fee is paid to miners/validators.

The blockspace market currently follows a demand curve - transactions with a higher value (gas used x gas price) are prioritized by miners over transactions with a lower value, and the total gas used in a block is limited to 15m.
Effectively what this means is that some transactions will be priced out and not included in the block. In practise, 10-15% of the gas used in a block is by zero-fee transactions, due to for example MEV clients including Flashbots bundles - for this reason, instead of taking the minimum gas price in the block to calculate a reasonable value for the future base fee at equilibrium, we take the 25th percentile to remove zero-fee outliers (which are no longer possible after EIP-1559). This is a reasonable assumption because at equilibrium the base fee is meant to target the user in the upper percentiles of the current demand curve at 15m gas.

Using a [Dune Analytics query](https://duneanalytics.com/queries/91241) we calculate the 90-day 25th and 50th percentile gas price by transaction:
* 90-Day 50th Percentile ("Median"): 33 Gwei per gas
* 90-Day 25th Percentile: 18 Gwei per gas

We expect the steady state average base fee to be in the range of 20-30 Gwei per gas, and by default set the `base_fee_process` [System Parameter](./model/system_parameters.py) halfway to a constant 25 Gwei per gas. 

The following scenarios may exist, outside of the steady state:
* An increased base fee when rollups start paying for publishing on L1
* Increased priority fees during periods of high network load

### Average Priority Fee

In steady state and pre Proof-of-Stake the priority fee level compensates for uncle risk, see:
* [Uncle risk/MEV miner fee calculation](https://notes.ethereum.org/@barnabe/rk5ue1WF_)
* [Why would miners include transactions at all](https://notes.ethereum.org/@vbuterin/BkSQmQTS8#Why-would-miners-include-transactions-at-all)

We adopt the following assumption in steady state, based on the research above:
* Pre Proof-of-Stake: Priority Fee = 2 Gwei per gas (to compensate for uncle risk and account for effect of possible sporadic transaction inclusion auctions)
* Post Proof-of-Stake: Priority Fee = 1 Gwei per gas (to account for effect of possible sporadic transaction inclusion auctions)

To change this value, update the `priority_fee_process` [System Parameter](./model/system_parameters.py).

### Maximum Extractable Value (MEV)

Maximum Extractable Value (MEV), previously referred to as "Miner Extractable Value", is a measure of the profit a miner/validator can make by arbitrarily including, excluding, or re-ordering transactions within the blocks they produce.

The most prominent form of MEV has been that introduced by Flashbots' MEV-geth client, making up 85% of Ethereum's hashrate at the time of writing, and we include an extract from the research article by Flashbots ["MEV and EIP-1559"](https://hackmd.io/@flashbots/MEV-1559) for context:

> Flashbots has introduced a way for searchers to express their transaction ordering preferences to miners, leading to a more efficient market all Ethereum users should ideally benefit from. In order to achieve this, Flashbots provides custom mining software (MEV-geth) to a number of miners jointly controlling the vast majority of Ethereum’s hashrate (85% at the time of writing).

There are several auction mechanisms coexisting in Ethereum, identified by Flashbots in their research article ["MEV and EIP-1559"](https://hackmd.io/@flashbots/MEV-1559). Of these MEV related auction mechanisms only one, transaction inclusion, directly affects EIP-1559 priority fees:
* Transaction inclusion via EIP-1559 priority fees
* Transaction privacy via Flashbots/Darkpools
* Transaction ordering via Flashbots/Other relays

Prior to the adoption of the Flashbots MEV-geth client, gas prices were artificially high due to MEV bots spamming blocks with higher gas bids to ensure their transaction would occur before the transaction that they were attacking. Since then, the majority of MEV bots have moved to the Flashbots network, relieving the network of this spam that drove gas prices up. Now that MEV is extracted on an independent channel (Flashbots) and from a different mechanism (shared profit vs. high gas fees), gas prices have decreased.

The consensus among researchers is that MEV is hard to quantify, and the future interaction between EIP-1559 and MEV is at this stage uncertain and complex. For this reason we adopt the assumption that in normal conditions MEV will be extracted via off-chain mechanisms, and so will be treated as a seperate process to EIP-1559 - we suggest to refine the model assumptions once more data and research about the interaction between EIP-1559 and MEV is available.

The `realized_mev_per_block` [System Parameter](./model/system_parameters.py) can be used to set the realized MEV in ETH per block. By default, we set the `realized_mev_per_block` to zero ETH, and leave it up to the reader to set their own assumptions.
