# Batch Reactor Fundamentals — v1.49 presentation

KineticFittingPot now begins the batch-reactor sequence by connecting the industrial multipurpose vessel to the simplified pure-batch model used for the first mathematical development. The original 2021 *Batch reactor models* notes remain available unchanged from the application.

## Included teaching sequence

1. Industrial batch reactors as generally well-mixed, multipurpose processing vessels.
2. The **operations list**: charging, controlled additions, heating/cooling, reaction, hold, sampling, transfer and discharge.
3. The distinction between **pure batch** and **semi-batch** operation.
4. A short description of real reactor hardware: metal or glass-lined vessel, agitation, connections, bottom discharge and heat-transfer jacket.
5. Why KineticFittingPot deliberately starts with a closed, well-mixed, liquid-phase, isothermal pure-batch reaction period.
6. Overall mass balance `d(rho V)/dt = 0`.
7. Constant-volume and variable-density interpretations.
8. Additive-volume calculation from species inventory.
9. Species balance `dn_j/dt = V R_j`.
10. Multiple-reaction representation with reactant/product stoichiometric matrices.
11. Mass-action kinetic rates and Arrhenius temperature dependence.
12. Net stoichiometric matrix `S = S_P - S_R`.
13. Net species production rates and the simulation-ready equation `dn/dt = V S r`.

## Industrial-to-model progression

The page makes the staged modelling decision explicit:

**Industrial batch process** — many operations may occur, including controlled additions and heating/cooling.

→ **Model considered here** — closed, well mixed, liquid phase, isothermal and pure batch during the reaction period.

→ **Beyond the isothermal batch model** — non-isothermal behaviour, heat removal, temperature control and fed-batch operation require additional balances.

This avoids implying that an industrial batch process is normally only “charge everything, react, discharge”. Pure batch is used first because it isolates the stoichiometry/kinetics/inventory relationship before feeds and thermal dynamics are added.

## Presentation decisions

- The page retains the existing mathematical development and validated model equations.
- The introductory industrial context is concise; detailed jacket construction and thermal-fluid design remain in **Reactor Heat Removal & Temperature Control Fundamentals**.
- No claim is made that batch processing dominates all chemical manufacture. The page instead distinguishes flexible/high-value/multiproduct batch use from large-volume continuous commodity production.
- Source figures remain omitted from the web fundamentals page; the source PDF is bundled unchanged and available for download.
- This teaching material remains separate from the immutable ChemEngBench research archive.

## Next page

The **Isothermal Batch Reactor Simulation** applies the closed pure-batch balances to the Van de Vusse network. The simulator provides an interactive way to explore the implications of its batch-reactor assumptions.
