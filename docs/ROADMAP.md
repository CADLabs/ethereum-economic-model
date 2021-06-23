# Research Roadmap

## Model Extensions

Assorted technical extensions ("future features") and advanced scenario analyses of the model:

* Implement the ability to simulate an inactivity leak scenario
* Extend the model to cover future Ethereum upgrade stages after merge, such as sharding
* Implement caching of results for improved simulation performance
* Backtest the model against historical data such as the ETH price, ETH staked to determine expected historical yields
* Apply Hoban/Borgers security (cost of attack) and required rate of return (RSAVY) analysis to simulation results

### 1. Simplified POW-only Model to study the behaviour of EIP-1559 under various network conditions

#### Description

The current model focuses on the the economics of the Ethereum network as a whole, as well as the economic impact on the individual validators taking part in the Ethereum Beacon chain over the various phases of the transition of the Ethereum network from a Proof of Work network to a Proof of Stake network.
In order to get a better understanding of the dynamics introduced by EIP-1559, the model could be modified to disregard the Beacon chain, and to focus purely on the impact of EIP-1559 on the network issuance, as well as the miners' rewards under various scenarios. 
This simplified model could then be used to study how EIP-1559 performs under various network loads, trends, and what the network issuance could look like under those loads, and what the miner's rewards would look like.


#### What’s required to make it happen

* Simplify model by removing rewards, penalties and slashing related to the Beacon Chain.
* Align cadCAD time steps with blocks in order to accomodate EIP-1559 block level calculations.
* Include the EIP-1559 `base_fee` state variable and policy function.
* Create various random processes to represent changes in network load.

#### Outcomes

The resulting model could be used to study how `base_fee` changes under various network loads, trends and volatility, and under what scenarios does the tipping facility come into play.

#### Difficulty

The changes to the model are not very complicated. The area that will require the most effort is designing stochastic processes that accurately represent network loads, trends and volatility.

#### Follow on extensions / Analysis

* Add multiple agent types that represent how different types of users will respond to a varying `base_fee`, introducing a feedback loop between `base_fee` and network usage.
* Extend the model to investigate under what scenarios do tips to miners come into play, and what do the tipping dynamics look like.

### 2. Investigate what the cost would be to artificially manipulate the `base_fee` that EIP-1559 introduces

#### Description

EIP-1559 introduces a `base_fee` that is a function of how far the preceding blocks varied from the set point of 15 million gas. If the block size consistently remains below 15 million gas, `base_fee` will continuously decrease, eventually reaching zero. Under this situation, no Ether will be burned, and all the Ether paid by the users for the transactions will go to the miners.
For this scenario to be artificially introduced, mining pools would need to collude by limiting their block sizes to be below 15 million gas. 
Investigate what percentage of miners would need to collude, and value would they need to limit the block sizes to, to ensure `base_fee` is pushed to zero assuming various behaviours of the remainder of the mining pools.

#### What’s required to make it happen

* The introduction of the EIP-1559 `base_fee` mechanism as described in [extension 1](#1-Simplified-POW-only-Model-to-study-the-behaviour-of-EIP-1559)
* An ensemble of stochastic processes representing network load similar to those described in [extension 1](#1-Simplified-POW-only-Model-to-study-the-behaviour-of-EIP-1559).

* A parameter sweep of the percentage of miners participating in the limiting of the block size, in conjunction with a parameter sweep over the range of possible block sizes, from 0 to 30 million gas.
* For an initial study, assume non-participating miner's maintain their block sizes at 15 million gas.
* For a secondary study, assume non-participating miner's maintain their block sizes at 30 million gas.

#### Outcomes

The product of this investigation would be a surface plot with the x and y axis being % miner participation and artificial block size limit respectfully, with the z axis being the resulting `base_fee`. Multiple plots of this kind would be produced for various assumptions of network load.

#### Difficulty

As an extension to [extension 1](#1-Simplified-POW-only-Model-to-study-the-behaviour-of-EIP-1559), this extension should be fairly trivial.

#### Follow on extensions / Analysis

* What would the financial benefit be for miner's participating in such collusion?
* How would the non-participating miner's react to such an event?
* What would the inflation of Ethereum be if such a scenario were to come about?
* What would the cost/benefit to the participants in the collusion be?


### 3. Investigate the effect on transaction cost on layer 1 taking into account the introduction of layer 2 solutions

#### Description

Layer 2 solutions are maturing rapidly, offering users drastically reduced gas fees. Serenity introduces a data layer, allowing even further cost savings for layer 2 transactions. Extend the model to simulate various scenarios of users moving their transactions over to layer 2 solutions, and how that shift affects the transaction cost on layer 1.

#### What’s required to make it happen

* For an initial investigation, assume a fixed price for layer 2 transactions.
* Perform a parameter sweep for the percentage of transactions that move over to layer 2 solutions.
* Adjust L1 `base_fee` according to network load as developed in [extension 1](#1-Simplified-POW-only-Model-to-study-the-behaviour-of-EIP-1559).


#### Outcomes

Run the model to investigate whether or not the system reaches a steady state on layer 1 transaction load, and if so, what is the steady state.

#### Difficulty

Building on [extension 1](#1-Simplified-POW-only-Model-to-study-the-behaviour-of-EIP-1559), a basic implementation should not be too complicated.

#### Follow on extensions / Analysis

* Introduce multiple agent types that exhibit varying behaviour and optimisation vectors, which in turn dictates which layer they transact on.
* If transactions become extremely cheap due to the introduction of L2 solutions and the introduction of the data layer that comes with Serenity, at what point does it become financially impractical for miners to keep mining?
* If transactions become so cheap due to L2 that transactions on L1 almost fall to zero, what does the return on investment for validators look like if they have to rely entirely on Beacon chain rewards, and what does the network inflation look like under those conditions?

### 4. Compare the yields for different types of validators taking into account the ability for validators participating in pools to earn compounding returns

#### Description

Each discrete validator requires 32 ETH. This requirement prevents a solo validator from reinvesting their yield to earn returns on their yields until they accrue an additional 32 ETH. Stakers that utilise validator pools on exchanges for example, can compound their return a lot quicker due to the staking pools being able to pool the returns of multiple validators to initiate another validator with 32 ETH. The pooling of returns and initialising of a shared validator effectively results in compound interest for those utilising staking pools, resulting in much higher yields, especially over longer periods of time, than that of solo / distributed validators.
Investigate the difference in APY for a validator as a function of pool size, starting at 1 (solo validator), referencing current holdings of exchanges such as Binance on the charts as the number representing pool size is swept.

#### What’s required to make it happen

* Add compounding mechanisms for returns
* Plot APY vs Pool size

#### Outcomes

A plot showing normalized APY as a function of pool size.

#### Difficulty

Implementing the compounding mechanism will take some thought.

#### Follow on extensions / Analysis

* Utilise the differing APY as an input for an agent based model to study the transition of validators to centralised pools.


