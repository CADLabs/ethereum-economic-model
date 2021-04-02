# EDP Phase 2: System Design

## Table of Contents

* [Mathematical Specification](#Model-Specification)
    * [Overview](#Overview)
    * [State Variables](#State-Variables)
    * [Exogenous Processes](#Exogenous-Processes)
    * [System Parameters](#System-Parameters)
    * [Mechanisms](#Mechanisms)
    * [System Metrics](#System-Metrics)
* [cadCAD Systems Model](#cadCAD-Systems-Model) (project phase 2)

# Mathematical Specification

## Overview

The **Mathematical Specification** defines the model as follows:
1. [State Variables](#State-Variables): the definition of State Variables as part of the [state-space representation](#State-space-Representation) of the system
2. [Exogenous Processes](#Exogenous-Processes): the inputs of the system that don't depend on internal system states
3. [System Parameters](#System-Parameters): the parameters that define the configuration of the system, referred to in the derivation of **Mechanisms** and **System Metrics**
4. [Mechanisms](#Mechanisms): the mathematical definition of system state transitions that update the State Variables, later integrated into cadCAD Policies and State Update Functions
5. [System Metrics](#System-Metrics): the outputs of the system that depend on the system **State Variables**, and measure the performance and KPIs of the system

### State-space Representation

A **state-space representation** is a formal mathematical model of a system as a set of input, output, and state variables related by first-order differential equations. These variables evolve over time in a way that depends on the current value of the state variables, as well as any inputs to the system. At each timestep there is a state transition, otherwise known as a State Update Function in the cadCAD generalized dynamical systems paradigm. [[1]](https://en.wikipedia.org/wiki/State-space_representation)

### Aggregation and Approximation

We refer to the model as an aggregate system dynamics model, because rather than modelling behaviour of individual agents, we consider what is often called a "representative agent" in economics literature. This allows us to apply aggregation and approximation for groups of agents, or in this case validator types (e.g. cloud, DIY, StaaS). 

For the purpose of the model a number of statistical approximations will be made, for example:
* Calculating an "average effective balance" instead of using an agent level per validator effective balance
* Determining the number of validators offline using expected uptime metrics
* Approximating a per-epoch inclusion distance using a formula derived by GitHub user @hermanjunge and used in the Hoban/Borgers model that depends on the number of offline validators

### Granularity

Unless specified otherwise all state variables, metrics, and parameters are time-dependent and calculated at per-epoch granularity. For ease of notation, units of time will be assumed implicitly. An exception to the per-epoch granularity is certain metrics that are annualized, such as the ETH supply inflation rate.

In the model implementation, the calculations could be aggregated across epochs where necessary - for example for performance reasons.

### Notation

The following notation is used in the mathematical specification:
* A list / vector of units or in calculations is represented using the matrix symbol: $\begin{bmatrix} x \end{bmatrix}$
* A list or vector variable is represented using the vector symbol: $\vec{x}$
* A $\Rightarrow$ symbol represents a function that returns a value, ignoring the arguments. For example a Python lambda function `lambda x: 1` would be represented as: $\Rightarrow 1$
* The superscript $S^+$ is used to define a state transition from state $S$ at the current epoch $e$, to the state at the next epoch $e + 1$

The following domain notation is used in the mathematical specification:
* $\mathbb{Z}$ - positive and negative integers
* $\mathbb{R}$ - positive and negative real numbers 
* $\mathbb{Z}^+$ - positive integers
* $\mathbb{R}^-$ - negative real numbers
* etc.

## State Variables

To create a state-space representation of the system, we first define the state variables. The state-space is a data structure that consists of all possible values of states (i.e the state variables). A state is the point in the state-space that represents a particular configuration of the system.

To properly mathematically define the state variables, parameters, and metrics, the domain and range, as well as units have been included. In the case of the system parameters, the expected default values have been included too. The variable column values are direct referrences to the to-be-built cadCAD model code.

The following constants are referred to in the specification:

| Name | Symbol | Domain | Unit | Variable | Value |
| -------- | -------- | -------- | -------- | --------| --------|
| Epochs per year | $E_{year}$ | $\mathbb{Z}^+$ | $\text{epochs}$ | `epochs_per_year` | 82180 |
| Epochs per day | $E_{day}$ | $\mathbb{Z}^+$ | $\text{epochs}$ | `epochs_per_day` | 225 |

### Ethereum States

To represent the Ethereum ETH token state, we define three state variables - the current spot price, total token supply, and the total ETH staked in the PoS system:

| Name | Symbol | Domain | Unit | Variable | Description |
| -------- | -------- | -------- | -------- | -------- | --------|
| ETH Price | $P$ | $\mathbb{R}^+$ | $$/\text{ETH}$ | `eth_price` | The current ETH price sample from an exogenous process (an external data feed) |
| ETH Supply | $S$ | $\mathbb{R}^+$ | $\text{ETH}$ | `eth_supply` | Ethereum supply with inflation/deflation |
| ETH Staked | $X$ | $\mathbb{R}^+$ | $\text{ETH}$ |`eth_staked` | Total ETH staked by all validators |

### Validator States

To represent validators entering the system through a process of staking, and keep track of their holdings in the PoS system, we define the following state variables:

| Name | Symbol | Domain | Unit | Variable |
| -------- | -------- | -------- | -------- | --------|
| Number of validators | $V$ | $\mathbb{R}^+$ | None | `number_of_validators` |
| Number of validators online | $V_{online}$ | $\mathbb{R}^+$ | None | `number_of_validators_online` |
| Number of validators offline | $V_{offline}$ | $\mathbb{R}^+$ | None | `number_of_validators_offline` |
| Average effective balance | $\bar{B}$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `average_effective_balance` |
| Validator ETH Staked | $\vec{\sigma}$ | $\mathbb{R}^+$ | $[\text{ETH}]$ | `validator_eth_staked` |

### PoS Rewards and Penalties States

To allocate and account for PoS system rewards and penalties, there are a number of state variables to consider. In general, there are two types of state variables defined - individual state variables such as the target reward `r_t` that represent the total per-epoch value for a specific reward type, and aggregate state variables such as validating rewards `R_v` that account for the value of all rewards of a specific type per-epoch.

Within the system, all rewards and penalties are stored in $\text{Gwei}$, before being converted to ETH and $ when calculating metrics.

| Name | Symbol | Domain | Unit | Variable |
| -------- | -------- | -------- | -------- | --------|
| Base Reward | $\beta$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `base_reward` |
| Source Reward | $r_s$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `source_reward` |
| Target Reward | $r_t$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `target_reward` |
| Head Reward | $r_h$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `head_reward` |
| Block Attester Reward | $r_a$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `block_attester_reward` |
| Block Proposer Reward | $r_p$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `block_proposer_reward` |
| Amount Slashed | $\psi$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `amount_slashed` |
| Validating Rewards | $R_v$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `validating_rewards` |
| Whistleblower Rewards | $R_w$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `whistleblower_rewards` |
| Validating Penalties | $Z_v$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `validating_penalties` |
| Total Online Validator Rewards | $R_o$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `total_online_validator_rewards` |

### EIP1559 States

| Name | Symbol | Domain | Unit | Variable |
| -------- | -------- | -------- | -------- | --------|
| Total Basefee | $F$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `total_basefee` |
| Total Tips to Validators | $T$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `total_tips_to_validators` |

### Metric States

Metrics are key performance indicators (KPIs) of the system - in this case of the total network performance as well as the distribution across different validator types.

The following metrics are calculated per validator type using Numpy array matrix algebra, before being aggregated.

There are 7 different validator types:
1. DIY Hardware
2. DIY Cloud
3. Pool StaaS
4. Pool Hardware
5. Pool Cloud
6. StaaS Full
7. StaaS Self-Custodied

The validator metrics have the following form:

\begin{bmatrix}
\text{DIY Hardware}\\
...\\
\text{StaaS Self-Custodied}
\end{bmatrix}

| Name | Symbol | Domain | Unit | Variable |
| -------- | -------- | -------- | -------- | --------|
| Validator Revenue | $\vec{K_r}$ | $\mathbb{R}$ | [$] | `validator_revenue` |
| Validator Profit  | $\vec{K_p}$ | $\mathbb{R}$ | [$] | `validator_profit` |
| Validator Revenue Yields | $\vec{Y_r}$ | $\mathbb{R}$ | $[\%]$ | `validator_revenue_yields` |
| Validator Profit Yields | $\vec{Y_p}$ | $\mathbb{R}$ | $[\%]$ | `validator_profit_yields` |
| Validator Count Distribution | $\vec{V}$ | $\mathbb{R}^+$ | $[\%]$ | `validator_count_distribution` |
| Validator Hardware Costs | $\vec{C}_{hardware}$ | $\mathbb{R}^+$ | [$] | `validator_hardware_costs` |
| Validator Cloud Costs | $\vec{C}_{cloud}$ | $\mathbb{R}^+$ | [$] | `validator_cloud_costs` |
| Validator Third-Party Costs | $\vec{C}_{third-party}$ | $\mathbb{R}^+$ | $[\%]$ | `validator_third_party_costs` |
| Validator Costs | $\vec{C}$ | $\mathbb{R}^+$ | [$] | `validator_costs` |

### Aggregate Metric States

The vector form of the metrics per validator type are then aggregated into scalar values for a system metric. For example, the validator costs $\vec{C}$ becomes the total network costs $C$ when summed over all 7 validator types.

| Name | Symbol | Domain | Unit | Variable |
| -------- | -------- | -------- | -------- | --------|
| ETH Supply Inflation | $I$ | $\mathbb{R}$  | $\%$ | `supply_inflation` |
| Total Revenue | $K_r$ | $\mathbb{R}$ | $  | `total_revenue` |
| Total Profit | $K_p$ | $\mathbb{R}$ | $ | `total_profit` |
| Total Network Costs | $C$ | $\mathbb{R}^+$ | $ | `total_network_costs` |
| Total Revenue Yields | $Y_r$ | $\mathbb{R}$ | $\%$ | `total_revenue_yields` |
| Total Profit Yields | $Y_p$ | $\mathbb{R}$ | $\%$ | `total_profit_yields` |

## Exogenous Processes

By selecting state variables as part of a state space representation, we have defined a system boundary. Exogenous processes produce inputs to our model that exist outside this boundary, and are not dependent on the system states.

We have three possible exogenous processes:

1. ETH price process that updates $P$
2. ETH supply process that updates $S$
3. ETH staked process that updates $X$

### ETH Price

Eventually, when the adoption of Eth2 is significant, we could expect validator staking to influence the velocity of money in the Ethereum ecosystem. For the purpose of this model, we've asumed this isn't the case, and that the ETH price can be modelled as an exogenous process.

:::warning
**Assumption**: Staking has no significant influence on the ETH price while ETH staked forms an insignificant portion of the total ETH supply.
:::

### ETH Supply

The ETH supply inflation is currently based on miner block rewards. When EIP1559 is introduced this will introduce an additional deflationary monetary policy. The Eth2 system PoS rewards and penalties will introduce a nominal inflation rate expected to be lower than the current Eth1 system, the price to maintain security of the system being much lower.

For the purpose of this model, we've assumed the system is operating post-merge, and that EIP1559 has been implemented. Because of this, there is no exogenous process of inflation from miner block rewards.

:::warning
**Assumption**: The system is operating post-merge, and EIP1559 has been implemented. Thus there is no inflation due to miner block rewards.
:::

We list ETH supply here to validate our decision to not introduce an exogenous process for ETH supply, but in future versions this could be reconsidered. The impact of ETH supply volatility, network congestion via EIP1559 and a changing basefee, could also be investigated. 

### ETH Staked

For the purpose of the model, we assume the amount of ETH staked in the system is not dependent on the current model state.

:::warning
**Assumption**: ETH staked is not dependent on the current model state.
:::

In reality, the staking of ETH into the system, and eventually out of the system when Eth2 if fully operational, is likely to be dependent on a number of feedback loops within the system - actors will make informed decisions based on both internal system states and exogenous states. Capital efficient investors will likely act to optimize their investment yields, and a minority will act to secure the system. Time and data will tell how best to model these dynamics and extend the current model.

Initially we'll assume a representative agent that remains within the system once staked, and an ETH staking process that follows an adoption model.

## System Parameters

Parameters are used as configurable variables in the logic of policies and mechanisms, often when performing calculations. An example of a parameter would be the `BASE_REWARD_FACTOR`, used to calculate and update the base reward state. In a cadCAD model, parameters are lists of Python types that can be swept, or in the case of a stochastic process used to perform a Monte Carlo simulation.

All parameters in this model can be tweaked by users of the model, but for the purpose of experimentation we've set defaults, and will likely sweep parameters within reasonable ranges around these defaults.

### Exogenous Processes

The following exogenous processes are configured using parameters, and update the corresponding state variables during runtime.

For example: at each epoch, the `eth_price_process` parameter, which is a Python lambda function, is called with the current run and timestep, and returns an ETH price sample, which would be used to update the state variable `eth_price`.

| Variable | Unit | Description |
| -------- | -------- | -------- |
| `eth_price_process` | $\Rightarrow \text{ETH}$ | A process in the form of a lambda function that takes the current run, timestep and returns an ETH price sample |
| `eth_staked_process` | $\Rightarrow \Delta \text{ETH}$ | A process that returns the change in total ETH staked |

### Eth2 Specification Parameters

The following parameters are the relevant parameters from the Eth2 specification.

All parameters from the Eth2 specification use uppercase snake-case variable naming, such as `BASE_REWARD_FACTOR`.

| Variable | Default Value | Unit |
| -------- | -------- | -------- |
| `BASE_REWARD_FACTOR` | `64` | None |
| `BASE_REWARDS_PER_EPOCH` | `4` | None |
| `MAX_EFFECTIVE_BALANCE` | `32e9` | $\text{Gwei}$ |
| `EFFECTIVE_BALANCE_INCREMENT` | `1e9` | $\text{Gwei}$ |
| `PROPOSER_REWARD_QUOTIENT` | `8` | None |
| `WHISTLEBLOWER_REWARD_QUOTIENT` | `512` | None |
| `MIN_SLASHING_PENALTY_QUOTIENT` | `32` | None |

### Validator Configuration Parameters

The following parameters are used in the configuration of validator types and operation.

| Variable | Unit | Description |
| -------- | -------- | -------- |
| `validator_internet_uptime` | $\%$ | The expected average uptime due to internet issues |
| `validator_power_uptime` | $\%$ | The expected average uptime due to power issues |
| `validator_technical_uptime` | $\%$ | The expected average uptime due to technical constraints |
| `validator_percentage_distribution` | $\begin{bmatrix} \% \end{bmatrix}$ | The distribution of the total number of validators per validator type |
| `validator_hardware_costs_per_epoch` | $$\begin{bmatrix} \$ \end{bmatrix}$$ | The per-epoch costs for DIY hardware infrastructure per validator type |
| `validator_cloud_costs_per_epoch` | $$\begin{bmatrix} \$ \end{bmatrix}$$ | The per-epoch costs for cloud computing resources per validator type |
| `validator_third_party_costs_per_epoch` | $\begin{bmatrix} \% \end{bmatrix}$ | A percentage value of the total validator rewards that goes to third-party service providers as a fee per validator type |

### Validation Parameters

The following parameters are used by the Eth2 PoS policies and mechanisms.

| Variable | Default Value | Unit | Description |
| -------- | -------- | -------- | -------- |
| `slashing_events_per_1000_epochs` | `1` | $\frac{1}{1000}\text{epochs}$ | The expected number of validator actions that result in slashing per 1000 epochs |
| `number_of_validating_penalties` | `3` | None | The total number of validation penalty types |

### EIP1559 Parameters

The following parameters are used by the Ethereum EIP1559 transaction pricing subsystem to approximate basefees and tips.

| Variable | Default Value | Unit | Description |
| -------- | -------- | -------- | -------- |
| `eip1559_basefee` | `1` | $\text{Gwei}$ | Assuming a fixed 1 Gwei basefee, for the purpose of the MVP model. To be validated during model implementation. |
| `eip1559_avg_tip_amount` | `0.01` | $\%$ | Assuming a fixed 1% tip amount, for the purpose of the MPV model. To be validated during model implementation. |
| `eip1559_avg_transactions_per_day` | `688078` | None | Average transactions per day over past 6 months. To be validated during model implementation. |
| `eip1559_avg_gas_per_transaction` | `73123` | $\text{Gas}$ | Average transaction gas over past 6 months. To be validated during model implementation. |

## Mechanisms

Once we have a data structure for our model, in the form of a state-space representation and the associated state variables, we can define the mechanisms that update that state over time.

To visualize the architecture of these mechanisms, we use a differential specification diagram, otherwise known as a "cadCAD Canvas" at cadCAD Edu. This diagram will accompany the derivation of the mathematical specification of the model mechanisms.

A differential specification diagram has a number of components, to summarize:
* A set of columns called Partial State Update Blocks, that represent the sequence of state transitions within a single timestep (epoch in our model)
* Within each Partial State Update Block multiple state updates can occur in parallel, but each State Update Function is responsible for updating the value of a single State Variable
* Policies define decisions and processes within the model output signals as inputs to State Update Functions that update the specific State Variable
* The first row contains the input states to the model Policies and State Update Functions
* The second row contains the Policies of the model
* The third row contains the State Update Functions
* The fourth and fifth rows contain the State Variables and Metrics that the State Update Functions update

![](https://i.imgur.com/FNPkqIz.png =300x)

![](https://i.imgur.com/vGaNGf3.png)

The following mechanisms are categorized according to the differential specification, in the same order of operations. The execution of these mechanisms in order would represent the state transition from one epoch to the next.

### Exogenous Processes

:::info
These are the ETH price and ETH staked processes, defined in the model specification, that update the ETH price and ETH staked at each timestep.
:::

The ETH supply at the next epoch is equal to ETH supply at the current epoch plus the total network issuance:
$$
S^+ = S + (R_v + R_w - Z_v - \psi - F)
$$

The total ETH staked is the sum ETH staked for all validator types:
$$
X = \sum_{i=1}^{V}{\sigma_{ij}}
$$

### Validators

:::info
Validators entering the system are driven by the total ETH staked in the system, and online and offline validators are approximated statistically.
:::

The total validators is equal to the number of online and offline validators:

$$V = V_{online} + V_{offline}$$

The following mathematical pseudo-code is used to calculate the aggregate average effective balance of the system:

\begin{equation}
\begin{aligned}
\bar{B} &= \frac{min(\text{total_effective_balance}, \text{max_total_effective_balance})}{V} \\
\text{where}: \\
\text{gwei} &= 10^9 \\
\text{effective_balance_increment} &= 10^9 \\
\text{total_effective_balance} &= X \times 10^9 - X \times 10^9 \quad mod \quad \text{effective_balance_increment} \\
\text{max_total_effective_balance} &= 32 \times V \\
\end{aligned}
\end{equation}

### Base Reward

:::info
The base reward is updated at each timestep according to the average effective balance and the amount of ETH staked in the system.
:::

The base reward is calculated as the average effective balance multiplied by the ratio of the base reward factor, to the square-root of the total ETH staked multiplied by the base rewards per epoch:

$$
\beta = \text{min}(\bar{B}, \text{MAX_EFFECTIVE_BALANCE}) \times \frac{\text{BASE_REWARD_FACTOR}}{\sqrt{X \times 10^9} \times \text{BASE_REWARDS_PER_EPOCH}}
$$

### Block Proposal and Attestation

:::info
The rewards and penalties from PoS block proposal and attestation are approximated and aggregated across all validators at each epoch.
:::

#### Source, Target, and Head Rewards

To approximate the source, target, and head vote rewards, it is assumed that all active (online) validators get a correct source, target, and head vote once per epoch:

$$
r_s = r_t = r_h = (1 - \frac{V_{offline}}{V}) * \beta * V
$$

#### Block Proposal and Attestation Rewards

To calculate the block proposer and attester rewards, the inclusion distance is approximated using the number of offline validators, derived here https://github.com/hermanjunge/eth2-reward-simulation/blob/master/assumptions.md#attester-incentives:

$$
r_a = (1 - \frac{1}{\text{PROPOSER_REWARD_QUOTIENT}}) \times \beta \times \frac{1}{\text{inclusion_distance}}
$$

$$
r_p = (\frac{1}{\text{PROPOSER_REWARD_QUOTIENT}}) \times \beta \times \frac{1}{\text{inclusion_distance}}
$$

#### Validating Rewards

The validating rewards is calculated as the sum of all validator reward states:

$$
R_v = r_s + r_t + r_h + r_a + r_p
$$

#### Validating Penalties

The validating penalties are aproximated using the total number of validator penalties multiplied by the base reward and the number of validators offline:
$$
Z_v = \beta \times V_{offline} \times \text{number_of_validating_penalties}
$$

#### Total Online Validator Rewards

The total online validator rewards are the net rewards awarded to online validators account for validating rewards, validating penalties, whistleblower rewards, and tips to validators:

$$
R_o = R_v + R_w + T - Z_v
$$

### Slashing

:::info
Slashing is performed and whistleblower rewards distributed, approximated using the total number of offline validators.
:::

The whistleblower reward is calculated as the current average effective balance divided by the whistleblower reward quotient, multiplied by the number of slashing events in the current epoch:

$$
R_w = \frac{\bar{B}}{\text{WHISTLEBLOWER_REWARD_QUOTIENT}} \times \frac{\text{slashing_events_per_1000_epochs}}{1000}
$$

The amount slashed is calculated as the current average effective balance divided by the minimum slashing penalty quotient, multiplied by the number of slashing events in the current epoch:

$$
\psi = \frac{\bar{B}}{\text{MIN_SLASHING_PENALTY_QUOTIENT}} \times \frac{\text{slashing_events_per_1000_epochs}}{1000}
$$

### EIP1559 Sub-system

:::info
The total basefee and tips to validators are calculated at each timestep, according to average expected transaction rates.
:::

EIP1559 introduces a basefee that is burned, and tips to validators, the total basefee and tips per epoch being calculated as:

$$
F = \frac{\text{eip1559_avg_transactions_per_day}}{E_{day}} \times \text{eip1559_avg_gas_per_transaction} \\ \times \text{eip1559_basefee} 
$$

$$
T = \frac{\text{eip1559_avg_transactions_per_day}}{E_{day}} \times \text{eip1559_avg_gas_per_transaction} \\ \times \text{eip1559_avg_tip_amount} 
$$

## System Metrics

![](https://i.imgur.com/VTiLNne.png)

The system metrics are calculated in three stages, in three partial state update blocks:

* Reward Aggregation
* Validator Cost Aggregation
* Accounting and Metrics

The metrics of the system can also be calculated in post-processing, to improve run-time performance.

#### Network Costs

The validator costs is the sum of hardware, cloud, and third-party costs per validator type:
$$
\vec{C} = \vec{C}_{hardware} + \vec{C}_{cloud} + \vec{C}_{third-party} \qquad ([$])
$$

The total network costs is the sum of validator costs over all validator types (row index $i$):
$$
C = \sum_{i}{\vec{C}_{ij}} \qquad ($)
$$

#### Revenue and Profit

The validator revenue is the rewards for online validators in ETH, $R_o / 10^9$, distributed according to the validator percentage distribution multiplied by the current ETH price $P$:
$$
\vec{K}_r = \text{validator_percentage_distribution} \times R_o / 10^9 \times P \qquad ([$])
$$

The validator profit is the validator revenue less the validator costs:
$$
\vec{K}_p = \vec{K}_r - \vec{C} \qquad ([$])
$$

The total revenue is the sum of validator revenue over all validator types:
$$
K_r = \sum_{i}{\vec{K}_{r,ij}} \qquad ($)
$$

The total profit is the total revenue less the total network costs:
$$
K_p = K_r - C \qquad ($)
$$

#### Revenue and Profit Yields

The per-validator revenue and profit yields are calculated and annualized as the validator profit and revenue multiplied by the number of epochs in a year divided by the validator ETH staked, $\sigma$, in dollars:
$$\vec{Y}_r = \frac{\vec{K}_r \times E_{year}}{\sigma \times P} \qquad ([\%])$$
$$\vec{Y}_p = \frac{\vec{K}_p \times E_{year}}{\sigma \times P} \qquad ([\%])$$

The total revenue and profit yields are calculated and annualized as the total profit and revenu multiplied by the number of epochs in a year divided by the total ETH staked, $X$, in dollars:
$$Y_r = \frac{K_r \times E_{year}}{X \times P} \qquad (\%)$$
$$Y_p = \frac{K_p \times E_{year}}{X \times P} \qquad (\%)$$

# cadCAD Systems Model

Completed in project phase 2.
