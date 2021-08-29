# Model Extension Roadmap

The following is a list of possible model extensions to act as inspiration:

## 1. Make the model a live "digital twin"

### Description

The model currently has a number of State Variables and System Parameters that are initialized either using static values or calculated using static CSV files. These static values need to be updated periodically to ensure the model properly represents the real-world system state, this is currently a manual process.

For this model extension, we suggest refactoring a number of the State Variables and System Parameters to be updated from live data sources, and create a true digital twin.

### What’s required to make it happen

The following State Variables and System Parameters could be refactored to be initialized from a live data source, such as an API or Subgraph:
* `validator_process` System Parameter: Currently set to the 6 months mean validator adoption from a static variable. This parameter directly influences the network inflation and supply, and would benefit from being updated live to reflect the current system state.
* `eth_price_process` System Parameter: Currently set to the mean ETH price from a static CSV file from Etherscan. This parameter directly influences the profit yields of validators in certain environments, and would benefit from being updated live to reflect the current system state.
* `base_fee_process` System Parameter: Currently calculated based on the historical 3 month mean gas price and set to a static variable. This parameter directly influences the network inflation and supply, and would benefit from being updated live to reflect the current system state.

### Outcomes

Turn the model into a real live "digital twin", integrating with and automatically updating from live blockchain data, enabling accurate real-time analysis of validator economics.

### Follow-on extensions / analysis

* Simulate the model over historical validator deposit data from The Graph Subgraph, as a regression test, to validate the revenue yields produced by the model closely match those actually experienced by validators historically.

## 2. Study the effect of a dynamic EIP-1559 base fee under various network conditions

### Description

The current model assumes the long-term average gas used is equal to the gas target per block, and the base fee and priority fee are set using a time-series process. In order to get a better understanding of the dynamics introduced by EIP-1559, the model could be modified to introduce a changing transaction load, and resulting dynamic base fee.

Analyse the performance of EIP-1559, the effect of the base fee on network issuance as well as the specific miner and validator rewards, under various network loads and trends.

### What’s required to make it happen

* Determine and implement stochastic processes that accurately represent network loads, trends and volatility
* Align cadCAD time steps with slots/blocks in order to accommodate EIP-1559 slot/block level calculations
* Refactor the current EIP-1559 base fee process by implementing the dynamic base fee mechanism from the spec

### Outcomes

The resulting model could be used to study how the base fee changes under various network loads, trends and volatility, and under what scenarios the priority-fee facility comes into play.

### Follow-on extensions / analysis

* Add multiple agent types that represent how different types of users will respond to a varying base fee, introducing a feedback loop between the base fee and network usage
* Extend the model to investigate under what scenarios priority fees to validators/miners come into play, and what the priority fee dynamics look like

## 3. Investigate what the cost would be to artificially manipulate the base fee that EIP-1559 introduces

### Description

EIP-1559 introduces a base fee that is a function of the current base fee and how far the preceding block varied from the gas target of 15 million gas. If the block size consistently remains below 15 million gas, the base fee will continuously decrease, eventually reaching zero. Under this scenario, no Ether will be burned, and all the Ether paid by the users for transactions will go to miners and validators as a priority fee ("tips") - effectively introducing a blockspace auction.

For this scenario to be artificially introduced, mining pools would need to collude by limiting their block sizes to be below 15 million gas.

Investigate what percentage of miners would need to collude to limit the block size, and to what value, to ensure the base fee is pushed to zero – assuming behaviours for the remainder of the mining pools.

### What’s required to make it happen

* The introduction of the EIP-1559 base fee mechanism as described in extension 1
* An ensemble of stochastic processes representing network load similar to those described in extension 1
* A parameter sweep of the percentage of miners participating in the limiting of the block size, in conjunction with a parameter sweep over the range of possible block sizes, from 0 to 30 million gas
* For an initial study, assume non-participating miners maintain their block sizes at 15 million gas
* For a secondary study, assume non-participating miners maintain their block sizes at 30 million gas

### Outcomes

The product of this investigation would be a surface plot with the x- and y-axis being percentage miner participation and artificial block size limit respectfully, with the z-axis being the resulting base fee. Multiple plots of this kind would be produced for various network-load assumptions.

### Follow-on extensions / analysis

* What would the financial benefit be for miners participating in such collusion?
* How would the non-participating miners react to such an event?
* What would the network inflation rate of Ethereum be if such a scenario were to come about?
* What would the cost/benefit be to the participants in the collusion?

## 4. Investigate the effect of the introduction of layer 2 solutions on layer 1 transaction costs

### Description

Layer 2 solutions are maturing rapidly, offering users drastically reduced fees. Serenity introduces a data layer, allowing even further cost savings for layer 2 transactions.

Extend the model to simulate various scenarios of users moving their transactions over to layer 2 solutions, and how that shift affects the transaction cost on layer 1.

### What’s required to make it happen

* For an initial investigation, assume a fixed price for layer-2 transactions
* Perform a parameter sweep for the percentage of transactions that move over to layer-2 solutions
* Adjust the layer-1 base fee according to transaction load as developed in extension 1

### Outcomes

Determine whether the layer-1 transaction load reaches a steady state, and if so, determine the steady state.

### Follow-on extensions / analysis

* Introduce multiple agent types that exhibit varying behaviour and optimization vectors, which in turn dictates which layer they transact on.
* If transactions on layer 1 significantly decrease below the gas target and the base fee drops to near zero, what does the return on investment for validators look like if they have to rely entirely on Beacon Chain rewards? What does the network inflation rate look like under those conditions? 

## 5. Introduce compounding returns for validators participating in pools

### Description

Each discrete validator requires a 32 ETH deposit when initialized. A validator's effective balance – the value used to calculate validator rewards – is a maximum of 32 ETH. Any rewards a validator earns above and beyond the 32 ETH requirement do not contribute to their yields until they accrue an additional 32 ETH and create another validator instance. This prevents a solo validator from reinvesting their yields to receive compound interest.

On the other hand, stakers that utilise validator pools, on exchanges for example, can compound their returns by pooling the returns of multiple validators to initialize another validator with 32 ETH. The pooling of returns and initialization of a shared validator effectively results in compound interest for those utilising staking pools, resulting in much higher yields, especially over longer periods of time, than that of solo / distributed validators.

Investigate the difference in annualized profit yields for a validator as a function of pool size – starting at 1 (solo validator) – and perform a sweep of pool size, using the current holdings of exchanges such as Binance as a reference.

### What’s required to make it happen

* Add a compounding mechanism for validator returns for validators in pool environments 
* Generate a plot of annualized profit yields vs validator pool size

### Outcomes

A plot showing annualized profit yields as a function of pool size.

### Follow-on extensions / analysis

* Use the differing annualized profit yields as an input for an agent-based model to study the possible centralisation of validators in staking pools over time.
