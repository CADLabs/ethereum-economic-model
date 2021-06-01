# Model Assumptions

## 0. Base assumptions adopted from Hoban/Borger's Ethereum 2.0 Economic Model

The base assumptions are adopted from the Hoban/Borger's "Ethereum 2.0 Economic Model". Due to the Altair updates since their model was released, and the state-space representation of our model, some of these assumptions were updated or adapted where necessary.

See Hoban/Borger's "Ethereum 2.0 Economic Review" section 6, "Model Walk Through" - "General Inputs and Assumptions", "Validator Cost Assumptions", and "Control Panel Assumptions".

An extract from cadCAD Model Specification document:
> As part of the cadCAD Masterclass online course, the to-be-built cadCAD model  serves an educational purpose first and foremost, and was scoped accordingly in the ESP application as an “extendable, open-source, minimum viable product (MVP), eth2 validator economics cadCAD model replicating the core eth2 validator yield dynamics based on assumptions in Hoban/Borger's well-known eth2 economic model. The term "minimum viable product" is understood to mean a model that is useful in the eyes of current and future eth2 validators for simulating ETH2 yield dynamics while making simplifying assumptions where that appears necessary and possible without prohibitive implications on yield dynamics.” We note this explicitly since this initial dynamical systems model will abstract from several Eth2 dynamics - notably any agent-level mechanisms/dynamics - potentially of interest for protocol analysis by scientific stakeholders.

As per the scoping description above, and although our model will implement computational experiments with varying assumptions, we base the MVP model on survey and analysis based assumptions by Hoban/Borger’s across the following categories by default:
* Validator environment assumptions
    * Validator environment categories 
    * Relative weight of validator environments
    * Validator operational cost per validator environment
* Validator performance assumptions
    * Average validator uptime
    * Frequency of slashing events

## 1. Validators act altruisticly 

## 2. At most 1/3 of validators can be offline at any time i.e. the inactivity leak threshold is never reached

## 3. Epoch level granularity

Unless specified otherwise, all State Variables, System Metrics, and System Parameters are time-dependent and calculated at epoch level granularity. For ease of notation, units of time will be assumed implicitly. In the model implementation, calculations can be aggregated across epochs where necessary - for example for performance reasons.

By default calculations will be aggregated across 1 day in epochs (~= 225 epochs), using the delta-time or `dt` parameter - the simulation results will have the same aggregation i.e. State Variables will be per-day, assuming `dt = 225`.
