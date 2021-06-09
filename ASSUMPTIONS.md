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

This is a validator economics model, and does not model security issues such as collusion, supermajority attacks, etc. Validators act altruistically, for the good of the network.

That being said, there is an abstraction for slashing with a simple process of x number of slashing events per 1000 epochs.

## 2. Validators have imperfect participation

We assume that not all online validators carry out their duties perfectly.

We do not make any assumptions about why aggregators act imperfectly, but rather we’ll assume validators are online and operating perfectly, or offline and not fulfilling their duties.

Those validators that are offline are penalized for not attesting to the source, target, and head.

We capture this participation rate using the `validator_uptime_process` System Parameter, which returns the percentage of online validators.

## 3. At most 1/3 of validators can be offline at any time i.e. the inactivity leak threshold is never reached

## 4. Epoch level granularity

Unless specified otherwise, all State Variables, System Metrics, and System Parameters are time-dependent and calculated at epoch level granularity. For ease of notation, units of time will be assumed implicitly. In the model implementation, calculations can be aggregated across epochs where necessary - for example for performance reasons.

By default calculations will be aggregated across 1 day in epochs (~= 225 epochs), using the delta-time or `dt` parameter - the simulation results will have the same aggregation i.e. State Variables will be per-day, assuming `dt = 225`.

## 5. Slashing events are applied equally to all validator environments

Whereas in reality the majority of slashing events have been due to institutional validators having too complex of a setup (StaaS for example), and as a result double-signing, we make the simplifying assumption that slashing events are applied equally to all validator environment types.

This assumption is adequate for calculations of validator economics under steady-state conditions, but might fail if slashing events increase significantly for a specific validator environment type, or if the network is under attack by a specific validator environment type.

See https://youtu.be/iaAEGs1DMgQ?t=574 for a good answer to the question of slashing for specific validator environments.

## 6. The same validator uptime is assumed for all validator environments

Whereas we could perhaps expect better uptime for cloud environments than local hardware environments, we do not have the necessary data to make these assumptions, and so we make the simplifying assumption that the same validator uptime is applied to all validator environments.

## 7. Validator environment costs are adopted from the Hoban/Borgers Ethereum 2.0 Economic Model

By analysing the expected costs of validating and infrastructure costs globally, Hoban/Borgers made certain assumptions about validator environment operational costs. These assumptions are listed in their spreadsheet model and report.

For example, they estimate 1 machine per 1000 validators, and global electricity and bandwidth averages are based on Ethereum node distribution.
