# Reaction Stoichiometry Fundamentals — v1.22

## Purpose

This workspace is the first learning page under **Fundamentals**. It develops the reaction-network language used throughout KineticFittingPot without turning the page into a general chemistry balancing lesson.

The teaching progression is:

**reaction equation → signed stoichiometric coefficients → stoichiometric vector → stoichiometric matrix → reaction-rate vector → species formation rates → reactor species balances**

## KineticFittingPot convention

KineticFittingPot uses a stoichiometric matrix with:

- rows = chemical species;
- columns = chemical reactions;
- reactant coefficients negative;
- product coefficients positive;
- zero for no stoichiometric participation in a given reaction.

Thus, for the reacting-species portion of the Van de Vusse network,

```text
2 x1 -> x2
x1 -> x3
x3 -> x4
```

KineticFittingPot uses

```text
S = [ -2  -1   0
       1   0   0
       0   1  -1
       0   0   1 ]
```

The built-in Van de Vusse simulator also tracks solvent x0, which contributes an all-zero stoichiometric row.

## Core balance relationship

If `r` is the vector of individual reaction rates, then

```text
R = S r
```

gives the net species formation/consumption rates per unit volume. For a well-mixed batch reactor,

```text
dn/dt = V S r
```

This is the same structural relationship used in the existing batch simulators and Excel-defined general model.

## Stoichiometry versus kinetics

The catalytic saturation example is used to show that stoichiometric participation and kinetic influence are different concepts. A catalyst can have zero stoichiometric coefficient while its concentration still appears in a kinetic rate expression.

## Elemental conservation

For an elemental matrix `A` with rows as elements and columns as species, balanced reaction columns satisfy

```text
A S = 0
```

For one reaction, a balanced stoichiometric vector satisfies

```text
A nu = 0
```

and therefore lies in the null space of the elemental matrix. The page explains that conservation constrains possible stoichiometries but does not, by itself, identify the physical multi-reaction mechanism.

## Deliberate scope

The workspace deliberately omits lengthy reaction classification, repeated balancing-by-inspection examples and reduced-row-echelon-form derivations. The emphasis is **reaction networks as engineering linear algebra** and direct connection to KineticFittingPot's numerical model structure.


## v1.22 presentation refinement

The small Van de Vusse and catalyst stoichiometry tables use KineticFittingPot's static teaching-table renderer so numeric coefficients are explicitly centred with their column headings. The next Fundamentals workspace is **Conversion, Yield and Selectivity**.
