# Model Assumptions

While the model implements the official Ethereum Specification wherever possible – see [README](README.md) for latest implemented release version – and allows for the computational simulation of many different assumption scenarios, the model does rest on a few validator-level assumptions by default, described in this document and to a large degree sourced from the extensive research done in the context of the well-known [Hoban/Borgers Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). We adapted some of these assumptions to reflect the evolution of the Ethereum protocol (e.g., Altair updates) and added new ones due to the nature of our dynamical-systems-modelling paradigm (e.g. time-dependent, dynamic variables). The [Experiment Notebook: Model Validation](experiments\notebooks\1_model_validation.ipynb) validates selected outputs of the CADLabs model against the Hoban/Borgers model to allow for efficient sanity checks. 
  
* [Network-level Assumptions](#network-level-assumptions)
  * [ETH Price](#ETH-Price)
  * [Proof-of-Work ETH Issuance](#proof-of-work-eth-issuance)
  * [Upgrade Stage Dates](#Upgrade-Stage-Dates)
    * [Simulation Start Date](#Simulation-Start-Date)
    * [EIP-1559 Activation Date](#eip-1559-activation-date)
    * [Proof-of-Stake Activation Date](#proof-of-stake-activation-date)
  * [Average Block Size](#Average-Block-Size)
  * [Average Base Fee](#Average-Base-Fee)
  * [Average Priority Fee](#Average-Priority-Fee)
  * [Maximum Extractable Value (MEV)](#maximum-extractable-value-mev)
* [Validator-level Assumptions](#validator-level-assumptions)
  * [Validator Adoption](#validator-adoption)
  * [Max Validator Cap](#maximum-validator-cap)
  * [Validator Environments](#validator-environments)
    * [Validator Environment Categories and Cost Structures](#Validator-Environment-Categories-and-Cost-Structures)
    * [Validator Environment Relative Weights](#Validator-Environment-Relative-Weights)
    * [Validator Environment Equal-slashing](#validator-environment-equal-slashing)
    * [Validator Environment Equal-uptime](#validator-environment-equal-uptime)
  * [Validator Performance](#Validator-Performance)
    * [Average Uptime](#Average-Uptime)
    * [Frequency of Slashing Events](#Frequency-of-Slashing-Events)
    * [Participation Rate](#Participation-Rate)

## Network-level Assumptions

### ETH Price 

In all state-space (i.e. time-domain) analyses of this repo, the ETH price is set to the daily mean over the last 12 months (source: Etherscan). This value is constant and calculated from a CSV file in the [data/](data/) directory, in the [data.historical_values](data/historical_values.py) module. 

To change this value, update the `eth_price_process` [System Parameter](./model/system_parameters.py). 

Note: In future releases of this model, we may periodically update this value automatically.  

### Proof-of-Work ETH Issuance

The Proof-of-Work ETH issuance (block rewards) in all time-domain analyses before the model's PoS Activation Date is set to the mean daily issuance over the last 12 months from Etherscan. This value is constant and calculated from a CSV file in the [data/](data/) directory, in the [data.historical_values](data/historical_values.py) module.  

To change this value, update the `daily_pow_issuance` [System Parameter](./model/system_parameters.py).

Note: In future releases of this model, we may periodically update this value automatically until the merge. 

### Upgrade Stage Dates

The model is configurable to reflect protocol behaviour at different points in time along the Ethereum development roadmap (referred to as "upgrade stages" in this repo).

#### Simulation Start Date

In all state-space (i.e. time-domain) analyses of this repo, the default start date is set to the current date, i.e. all analyses start "today". That being said, there are certain Initial States and System Parameter default values that are static, and don't update dynamically from an API. In these cases we generally use an average value over a time period, for example for the validator adoption System Parameter.

The simulation start date can be set using the `date_start` [System Parameter](./model/system_parameters.py). 

#### EIP-1559 Activation Date

The model by default assumes 4 August 2021 [London mainnet upgrade](https://blog.ethereum.org/2021/07/15/london-mainnet-announcement/) as the launch date for EIP1559. State-space (i.e. time-domain) analyses with starting date after 4 August 2021 therefore have the EIP-1559 mechanism fully activated. 

To change the EIP-1559 Activation Date, update the `date_eip1559` [System Parameter](./model/system_parameters.py).

#### Proof-of-Stake Activation Date

The model by default assumes 1 March 2022 for the Proof-of-Stake activation date ("The Merge"), since this seemed to be the Ethereum Community's consensus expectation at the time the model's default assumptions were defined. Launch dates are hard to predict, hence we recommend to play with alternative dates.

To change the Proof-of-Stake activation date, update the `date_pos` [System Parameter](./model/system_parameters.py).

## Average Block Size

With the introduction of [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) the pre-EIP1559 block size (gas limit) has been replaced by two values: a “long-term average target” (equal to the pre-EIP1559 gas limit, i.e. 15m gas), and a “hard per-block cap” (set to twice the pre-EIP1559 gas limit, i.e. 30m gas). 

By default, the model assumes that the block size (gas used per block) will on average be equal to the gas target, i.e. 15m gas. To change this value, update the `gas_target_process` [System Parameter](./model/system_parameters.py).

Note for cadCAD engineers: It is quite straight forward to extend the model for dynamic block size and base fee (see [roadmap document](ROADMAP.md)), and we encourage you to give this a try. This would also open the model up automatic updates via live adoption data.

## Average Base Fee

[EIP-1559](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md) defines a variable `max_fee_per_gas` to set a fee cap per transaction. This fee cap is the maximum fee in Gwei per gas a user will pay per transaction. This fee is made up of the base fee and a priority fee, where the base fee is burned and the priority fee is paid to miners/validators.

The pre-EIP1559 blockspace market followed a demand curve - transactions with a higher value (gas used x gas price) are prioritized by miners over transactions with a lower value, and the total gas used in a block is limited to 15m.
Effectively this meant that some transactions would be priced out and not included in the block. In practise, 10-15% of the gas used in a block is by zero-fee transactions, due to for example MEV clients including Flashbots bundles.

For the above reason (and until actual base fee data becomes available), instead of taking a historical minimum gas price per block to extrapolate to a reasonable future base fee at equilibrium, we take a 3 month median (4 May 2021 - 4 August 2021) to remove zero-fee outliers (e.g. Flashbot bundles) for pre-EIP-1559 date ranges (zero fee transactions are no longer possible with EIP-1559).

Using a [Dune Analytics query](https://duneanalytics.com/queries/91241) we calculate the 90-day median gas price by transaction:
* 90-Day 50th Percentile ("Median"): 30 Gwei per gas

To change the default average base fee, update the `base_fee_process` [System Parameter](./model/system_parameters.py).

Note: In future releases of this model, we may periodically update this value automatically using on-chain data.

### Average Priority Fee

We used a staged approach for the estimation of the average priority fee:
* Pre Proof-of-Stake: Priority Fee = 2 Gwei per gas (to compensate for uncle risk and account for effect of possible sporadic transaction inclusion auctions)
* Post Proof-of-Stake: Priority Fee = 1 Gwei per gas (no uncle risk to compensate for, i.e. only accounting for effect of possible sporadic transaction inclusion auctions)

Sources:
* [Uncle risk/MEV miner fee calculation](https://notes.ethereum.org/@barnabe/rk5ue1WF_)
* [Why would miners include transactions at all](https://notes.ethereum.org/@vbuterin/BkSQmQTS8#Why-would-miners-include-transactions-at-all)

To change the default average priority fee, update the `priority_fee_process` [System Parameter](./model/system_parameters.py).

### Maximum Extractable Value (MEV)

The consensus among researchers is that MEV is hard to quantify, and the future interaction between EIP-1559 and MEV is at this stage uncertain and complex. For this reason we adopt the assumption that in normal conditions MEV will be extracted via off-chain mechanisms, and so will be treated as a seperate process to EIP-1559 - we suggest to refine the model assumptions once more data and research about the interaction between EIP-1559 and MEV is available.

The `mev_per_block` [System Parameter](./model/system_parameters.py) can be used to set the realized MEV in ETH per block. By default, we set the `mev_per_block` to zero ETH to better analyse PoS incentives in isolation, and leave it up to the reader to set their own assumptions. In some analyses we set the `mev_per_block` to the 3 month median value calculated using [Flashbots MEV-Explore analytics](https://explore.flashbots.net/).

Note: In future releases of this model, we may periodically update this value automatically using API data.

**Further reading:**

Maximum Extractable Value (MEV), previously referred to as "Miner Extractable Value", is a measure of the profit a miner/validator can make by arbitrarily including, excluding, or re-ordering transactions within the blocks they produce.

The most prominent form of MEV has been that introduced by Flashbots' MEV-geth client, making up 85% of Ethereum's hashrate at the time of writing, and we include an extract from the research article by Flashbots ["MEV and EIP-1559"](https://hackmd.io/@flashbots/MEV-1559) for context:

> Flashbots has introduced a way for searchers to express their transaction ordering preferences to miners, leading to a more efficient market all Ethereum users should ideally benefit from. In order to achieve this, Flashbots provides custom mining software (MEV-geth) to a number of miners jointly controlling the vast majority of Ethereum’s hashrate (85% at the time of writing).

There are several auction mechanisms coexisting in Ethereum, identified by Flashbots in their research article ["MEV and EIP-1559"](https://hackmd.io/@flashbots/MEV-1559). Of these MEV related auction mechanisms only one, transaction inclusion, directly affects EIP-1559 priority fees:
* Transaction inclusion via EIP-1559 priority fees
* Transaction privacy via Flashbots/Darkpools
* Transaction ordering via Flashbots/Other relays

Prior to the adoption of the Flashbots MEV-geth client, gas prices were artificially high due to MEV bots spamming blocks with higher gas bids to ensure their transaction would occur before the transaction that they were attacking. Since then, the majority of MEV bots have moved to the Flashbots network, relieving the network of this spam that drove gas prices up. Now that MEV is extracted on an independent channel (Flashbots) and from a different mechanism (shared profit vs. high gas fees), gas prices have decreased.

## Validator-level Assumptions

### Validator Adoption

Validator adoption is the assumed rate of new validators entering the activation queue per epoch, that results in an implied ETH staked value over time.

The "Validator Revenue and Profit Yields" experiment notebook introduces three linear adoption scenarios (historical adoption has been approximately linear):
* Normal adoption: assumes an average of 3 new validators per epoch. These rates correspond to the historical average newly **activated** validators per epoch between 15 January 2021 and 15 July 2021 as per [Beaconscan](https://beaconscan.com/stat/validator).
* Low adoption: assumes an average of 1.5 new validators per epoch, i.e. a 50% lower rate compared to the base scenario
* High adoption: assumes an average of 4.5 new validators per epoch, i.e. a 50% higher rate compared to the base scenario

The activation queue is modelled as follows: Validators that deposit 32 ETH are only activated and allowed to validate once they pass through the queue, and the queue has a maximum rate at which it can process and activate new validators. This activation rate is what changes the effective validator adoption rate in some analyses where there are more validators wanting to enter the system than being activated per epoch.

The normal adoption scenario is used as the default validator adoption rate for all experiments - to change this value, update the `validator_process` [System Parameter](./model/system_parameters.py).

### Maximum Validator Cap

The model adds a feature of a maximum validator cap to limit the number of validators that are validating ("awake") at any given time.

This feature is based on Vitalik's proposal where validators are not stopped from depositing and becoming active validators, but rather introduces a rotating validator set.

"Awake" validators are a subset of "active" validators that are "validating" and receiving rewards, while "active" validators are all the validators with ETH staked.

The maximum validator cap is disabled by default (by setting the value to `None`), it's value is defined by the `MAX_VALIDATOR_COUNT` system parameter.

See https://ethresear.ch/t/simplified-active-validator-cap-and-rotation-proposal for additional context.

### Validator Environments

The model supports the simulation of validator economics across different "validator environments" to account for the different deployment setups validators are using to access the network, each with slightly different economics. 

#### Validator Environment Categories and Cost Structures

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

#### Validator Environment Relative Weights

By default, the model assumes the following relative weights for the calculation of average validator revenue and profit yields, as defined by 
[Hoban/Borgers' Ethereum 2.0 Economic Model](https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE). These values could change substantially and the user is encouraged to experiment with other assumptions. 

1. Run own hardware validator ("DIY-Hardware"): **37%**
2. Run own cloud validator ("DIY-Cloud"): **13%**
3. Validate via a pool Staking-as-a-Service provider ("Pool-Staas"): **27%**
4. Validate via a pool hardware service provider ("Pool-Hardware"): **5%**
5. Validate via a pool Cloud provider ("Pool-Cloud"): **2%**
6. Validate via a custodial Staking-as-a-Service provider ("StaaS-Full"): **8%**
7. Validate via a non-custodial Staking-as-a-Service provider ("StaaS-Self-custodied"): **8%**

#### Validator Environment Equal-slashing

Whereas in reality slashing events have occurred more often in some validator environments (e.g. institutional players getting their setup wrong and double-signing), we make the simplifying assumption that slashing events are applied equally across all validator-environment types.

This assumption is adequate for calculations of validator economics under steady-state conditions but might fail if slashing events increase significantly for a specific validator-environment type, or if the network is under attack by a specific validator-environment type.

See https://youtu.be/iaAEGs1DMgQ?t=574 for additional context. 

#### Validator Environment Equal-uptime

Whereas we arguably expect better uptime for some validator environments than others (e.g. better for cloud environments than local hardware environments), we make the simplifying assumption that the same validator uptime is applied to all validator environments. Once respective data becomes available over time, this assumption could be dropped in future model iterations.

### Validator Performance

#### Average Uptime

By default, the model assumes an average of 98% uptime.

In reality, this value has varied between lows of 95% and highs of 99.7% with an average of approximately 98%.

We capture the average uptime using the `validator_uptime_process` System Parameter – a function that returns the average uptime and allows us to create stochastic or time-dependent uptime processes.

#### Frequency of Slashing Events

By default, the model assumes 1 slashing event every 1000 epochs.

As more statistical data is collected about slashing in different validator environments, this assumption could be updated.

#### Participation Rate

The model assumes that validators are either online and operating perfectly, or offline and not fulfilling their duties. Offline validators are penalized for not attesting to the source, target, and head. We do not model validators that fulfil some of their duties, and not other duties. We capture this participation rate (percentage of online validators) using the `validator_uptime_process` System Parameter.

In its initial version, the model does not model Ethereum's inactivity leak mechanism. We assume a **participation of more than 2/3 at all times**. We assert this requirement in the `policy_validators(...)` Policy Function.
