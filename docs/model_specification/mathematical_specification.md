# Mathematical Specification

:warning: The Mathematical Specification needs to be updated to cover the latest Ethereum Altair updates

## Overview

This Mathematical Specification articulates the relevant Eth2 validator economics system dynamics as a [state-space representation](https://en.wikipedia.org/wiki/State-space_representation). Given the iterative nature of dynamical systems modeling work, we expect to make adjustments to this Mathematical Specification as we build and validate the cadCAD model.

### Level of Aggregation

Although cadCAD technically supports several computational modeling paradigms (e.g. agent-based modeling, population-level modeling, system dynamics modeling, hybrid modeling, etc.) we adopt an aggregate system dynamics lense in our MVP educational model. Rather than modelling the behaviour of individual agents, we consider what is often called a "representative agent" in economics literature. This allows us to apply aggregation and approximation for groups of agents or in our case, validator environments.

### Statistical Approximations

The aggregate system dynamics point of view led us to make several statistical approximations, e.g.:

* Expected uptime metrics: We use aggregate expected uptime metric assumptions as per survey data by [Hoban/Borgers' Economic Model](https://drive.google.com/file/d/1pwt-EdnjhDLc_Mi2ydHus0_Cm14rs1Aq/view).
* Per-epoch inclusion distance: We approximate per-epoch inclusion distance as per [Hoban/Borgers' Economic Model](https://drive.google.com/file/d/1pwt-EdnjhDLc_Mi2ydHus0_Cm14rs1Aq/view), using a formula derived by [@hermanjunge](https://github.com/hermanjunge/eth2-reward-simulation/blob/master/assumptions.md#attester-incentives).

### Epoch-level Granularity

Unless specified otherwise, all State Variables, System Metrics, and System Parameters are time-dependent and calculated at per-epoch granularity. For ease of notation, units of time will be assumed implicitly. In the model implementation, calculations can be aggregated across epochs where necessary - for example for performance reasons.

## Notation

The Mathematical Specification uses the following notation:
* A list / vector of units or in calculations is represented using the matrix symbol: $\begin{bmatrix} x \end{bmatrix}$
* A list or vector variable is represented using the vector symbol: $\vec{x}$
* A $\Rightarrow$ symbol represents a function that returns a value, ignoring the arguments. For example a Python lambda function `lambda x: 1` would be represented as: $\Rightarrow 1$
* The superscript $S^+$ is used to define a state transition from state $S$ at the current epoch $e$, to the state at the next epoch $e + 1$

The following domain notation is used in the Mathematical Specification:
* $\mathbb{Z}$ - positive and negative integers
* $\mathbb{R}$ - positive and negative real numbers 
* $\mathbb{Z}^+$ - positive integers
* $\mathbb{R}^-$ - negative real numbers
* etc.

## System States

To create a state-space representation, we first describe the system's [state space](https://www.google.com/search?q=state+space+state+variables&oq=state+space+state+variables&aqs=chrome..69i57.4591j0j1&sourceid=chrome&ie=UTF-8) in the form of a set of State Variables. A state space is a data structure that consists of all possible values of State Variables. The state of the system can be represented as a state vector within the state space.

For reasons of clarity and comprehensibility we categorize State Variables as follows: Constants State Variables, ETH State Variables, Validator State Variables, Reward and Penalty State Variables, EIP1559 State Variables, and System Metric State Variables.  

We define the State Variables' domain, range, and units. The "variable" column values are direct referrences to the to-be-built cadCAD model code.

### ETH State Variables

| Name | Symbol | Domain | Unit | Variable | Description |
| -------- | -------- | -------- | -------- | -------- | --------|
| ETH Price | $P$ | $\mathbb{R}^+$ | $$/\text{ETH}$ | `eth_price` | ETH spot price sample (from exogenous process) |
| ETH Supply | $S$ | $\mathbb{R}^+$ | $\text{ETH}$ | `eth_supply` | ETH supply with inflation/deflation |
| ETH Staked | $X$ | $\mathbb{R}^+$ | $\text{ETH}$ |`eth_staked` | Total ETH staked by all validators |

### Validator State Variables

| Name | Symbol | Domain | Unit | Variable |
| -------- | -------- | -------- | -------- | --------|
| # Validators | $V$ | $\mathbb{R}^+$ | None | `number_of_validators` |
| # Validators Online | $V_{online}$ | $\mathbb{R}^+$ | None | `number_of_validators_online` |
| # Validators Offline | $V_{offline}$ | $\mathbb{R}^+$ | None | `number_of_validators_offline` |
| Average Effective Balance | $\bar{B}$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `average_effective_balance` |
| Validator ETH Staked | $\vec{\sigma}$ | $\mathbb{R}^+$ | $[\text{ETH}]$ | `validator_eth_staked` |

### Reward and Penalty State Variables

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

### EIP1559 State Variables

| Name | Symbol | Domain | Unit | Variable |
| -------- | -------- | -------- | -------- | --------|
| Total Basefee | $F$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `total_basefee` |
| Total Tips to Validators | $T$ | $\mathbb{R}^+$ | $\text{Gwei}$ | `total_tips_to_validators` |

### System Metric State Variables

We first define System Metrics on the level of the following 7 validator environments, using Numpy array matrix alegbra:

1. DIY Hardware
2. DIY Cloud
3. Pool StaaS
4. Pool Hardware
5. Pool Cloud
6. StaaS Full
7. StaaS Self-Custodied

We then define network level System Metrics through aggregation.

#### Validator Environment Level

The State Variables in this category have the following vector form:

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

#### Aggregate Network Level

The above validator environment level System Metrics are then aggregated into scalar values to define aggregate network level system metrics. For example, the validator costs $\vec{C}$ becomes the total network costs $C$ when summed over all 7 validator types.

| Name | Symbol | Domain | Unit | Variable |
| -------- | -------- | -------- | -------- | --------|
| ETH Supply Inflation | $I$ | $\mathbb{R}$  | $\%$ | `supply_inflation` |
| Total Revenue | $K_r$ | $\mathbb{R}$ | $  | `total_revenue` |
| Total Profit | $K_p$ | $\mathbb{R}$ | $ | `total_profit` |
| Total Network Costs | $C$ | $\mathbb{R}^+$ | $ | `total_network_costs` |
| Total Revenue Yields | $Y_r$ | $\mathbb{R}$ | $\%$ | `total_revenue_yields` |
| Total Profit Yields | $Y_p$ | $\mathbb{R}$ | $\%$ | `total_profit_yields` |

## System Inputs

By defining State Variables we have defined the system's state space and with it, system boundaries. System inputs are not dependent on the system's State Variables. Their logic is defined by Policy Functions in our cadCAD model, and they update the model's State Variables via State Update Functions.

We describe two environmental processes as System Inputs, updating the ETH Price and ETH Staked State Variables.

### ETH Price

For the MVP implementation of our model we use tiered ETH price levels to represent the relevant spectrum of market conditions, similar to [Hoban/Borgers' Economic Model](https://drive.google.com/file/d/1pwt-EdnjhDLc_Mi2ydHus0_Cm14rs1Aq/view). We also plan the option for the user to manually select ETH price ranges to emulate custom scenarios.

This environmental process, represented in the model as a Python lambda function, is called at each epoch with the current run and timestep, and returns an ETH price sample to update the ETH Price state variable during runtime.

### ETH Staked

For the MVP implementation of our model we assume a representative agent that remains within the system once entered, and we use a monotonically increasing function as a standard adoption model.  We also plan the option for the user to manually select define ETH staked levels to emulate custom scenarios. 

This environmental process, represented in the model as a Python lambda function, is called at each epoch with the current run and timestep, and returns the change in ETH staked to update the ETH Staked state variable during runtime.

In future model implementations, we could imagine adding feedback loops from State Variables. For instance, capital efficient validators will likely stake and unstake ETH based on the development of validator returns.

## System Parameters

System Parameters are used as configurable variables as part of the model's System Input (Policy Function) and State Update (State Update Function) logic. An example of a parameter would be the `BASE_REWARD_FACTOR`, used to calculate and update the base reward state variable. 

In a cadCAD model, parameters are lists of Python types that can be swept, or in the case of a stochastic process used to perform a Monte Carlo simulation. For the purpose of experimentation we've set defaults, and will sweep parameters within reasonable ranges around these defaults.

For reasons of clarity and comprehensibility we categorize parameters as: Eth2 Official Specification Parameters,

### Eth2 Official Specification System Parameters

All System Parameters in this category use uppercase snake-case variable naming for easy recognition, such as `BASE_REWARD_FACTOR`.

| Variable | Default Value | Unit |
| -------- | -------- | -------- |
| `BASE_REWARD_FACTOR` | `64` | None |
| `BASE_REWARDS_PER_EPOCH` | `4` | None |
| `MAX_EFFECTIVE_BALANCE` | `32e9` | $\text{Gwei}$ |
| `EFFECTIVE_BALANCE_INCREMENT` | `1e9` | $\text{Gwei}$ |
| `PROPOSER_REWARD_QUOTIENT` | `8` | None |
| `WHISTLEBLOWER_REWARD_QUOTIENT` | `512` | None |
| `MIN_SLASHING_PENALTY_QUOTIENT` | `32` | None |

### Validator Environment System Parameters

| Variable | Unit | Description |
| -------- | -------- | -------- |
| `validator_percentage_distribution` | $\begin{bmatrix} \% \end{bmatrix}$ | The distribution of the total number of validators per validator type |
| `validator_hardware_costs_per_epoch` | $$\begin{bmatrix} \$ \end{bmatrix}$$ | The per-epoch costs for DIY hardware infrastructure per validator type |
| `validator_cloud_costs_per_epoch` | $$\begin{bmatrix} \$ \end{bmatrix}$$ | The per-epoch costs for cloud computing resources per validator type |
| `validator_third_party_costs_per_epoch` | $\begin{bmatrix} \% \end{bmatrix}$ | A percentage value of the total validator rewards that goes to third-party service providers as a fee per validator type |

### Validator Performance System Parameters

| Variable | Default Value | Unit | Description |
| -------- | -------- | -------- | -------- |
| `validator_internet_uptime` |99.9| $\%$ | The expected average uptime due to internet issues |
| `validator_power_uptime` |99.9| $\%$ | The expected average uptime due to power issues |
| `validator_technical_uptime` |98.2| $\%$ | The expected average uptime due to technical constraints |
| `slashing_events_per_1000_epochs` | `1` | $\frac{1}{1000}\text{epochs}$ | The expected number of validator actions that result in slashing per 1000 epochs |
| `number_of_validating_penalties` | `3` | None | The total number of validation penalty types |

### EIP1559 System Parameters

| Variable | Default Value | Unit | Description |
| -------- | -------- | -------- | -------- |
| `eip1559_basefee` | `1` | $\text{Gwei}$ | Assuming a fixed 1 Gwei basefee, for the purpose of the MVP model. To be validated during model implementation. |
| `eip1559_avg_tip_amount` | `0.01` | $\%$ | Assuming a fixed 1% tip amount, for the purpose of the MPV model. To be validated during model implementation. |
| `eip1559_avg_transactions_per_day` | `688078` | None | Average transactions per day over past 6 months. To be validated during model implementation. |
| `eip1559_avg_gas_per_transaction` | `73123` | $\text{Gas}$ | Average transaction gas over past 6 months. To be validated during model implementation. |

## State Update Logic

After defining the model's state space in the form of System States, we describe their state update logic, represented as cadCAD policy and State Update Functions (also called "mechanisms" sometimes)

To visualize the state update logic, we use a differential specification diagram (also known as a "cadCAD Canvas" at cadCAD Edu). This diagram will accompany the derivation of the Mathematical Specification of the model mechanisms.

The [model's cadCAD Canvas / Differential Specification](https://lucid.app/lucidchart/invitations/accept/07b715e4-80c9-4901-8ba7-f3309e52a38d?viewport_loc=41%2C-239%2C5380%2C3206%2CQe-m-rCpJ8RS) is accessible via LucidChart. Below is an illustrative screenshot. 

![](https://i.imgur.com/vGaNGf3.png)

We describe the state update logic along the columns of the model's cadCAD Canvas' columns, also known as "Partial State Update Blocks" (PSUB). One round of execution of these Partial State Update Blocks would represent the state transition from one epoch to the next.

#### Constants

The following constants are used in the derivation of the State Update Logic.

| Name | Symbol | Domain | Unit | Variable | Value |
| -------- | -------- | -------- | -------- | --------| --------|
| Epochs per year | $E_{year}$ | $\mathbb{Z}^+$ | $\text{epochs}$ | `epochs_per_year` | 82180 |
| Epochs per day | $E_{day}$ | $\mathbb{Z}^+$ | $\text{epochs}$ | `epochs_per_day` | 225 |

### PSUB 1: Environmental Processes

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

### PSUB 2: Validators

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

### PSUB 3: Base Reward

:::info
The base reward is updated at each timestep according to the average effective balance and the amount of ETH staked in the system.
:::

The base reward is calculated as the average effective balance multiplied by the ratio of the base reward factor, to the square-root of the total ETH staked multiplied by the base rewards per epoch:

$$
\beta = \text{min}(\bar{B}, \text{MAX_EFFECTIVE_BALANCE}) \times \frac{\text{BASE_REWARD_FACTOR}}{\sqrt{X \times 10^9} \times \text{BASE_REWARDS_PER_EPOCH}}
$$

### PSUB 4: Block Proposal and Attestation

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

### PSUB 5: Slashing

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

### PSUB 6: EIP1559 Sub-system

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




The following state-update logic for system metric State Variables can also be performend in post-processing, to improve run-time performance.

## System Metrics

System Metrics are computed from State Variables in order to assess the performance of the system. The calculation of our System Metrics is also represented in the [model's cadCAD Canvas / Differential Specification](https://lucid.app/lucidchart/invitations/accept/07b715e4-80c9-4901-8ba7-f3309e52a38d?viewport_loc=41%2C-239%2C5380%2C3206%2CQe-m-rCpJ8RS) and accessible via LucidChart. Below is an illustrative screenshot. 

![](https://i.imgur.com/VTiLNne.png)

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
