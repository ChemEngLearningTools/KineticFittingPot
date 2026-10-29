# Conversion, Yield and Selectivity — KineticFittingPot v1.22

This Fundamentals workspace follows **Reaction Stoichiometry Fundamentals** and develops the performance quantities used for multiple-reaction systems.

## General basis

KineticFittingPot uses mole amounts for the general definitions so the framework remains valid for constant- and variable-volume batch reactors.

For reactant A:

```text
X_A = (n_A0 - n_A) / n_A0
```

For constant volume the equivalent concentration definition may be used.

With KineticFittingPot's species-by-reactions stoichiometric convention:

```text
R = S r

dn/dt = V S r
```

## Instantaneous metrics

For desired product D and reactant A:

```text
Y_D/A(inst) = (dn_D/dt)/[-dn_A/dt] = R_D/(-R_A)
```

For desired product D and undesired product U:

```text
S_D/U(inst) = (dn_D/dt)/(dn_U/dt) = R_D/R_U
```

These are local-in-time quantities and can vary through a batch as the reaction-rate vector changes.

## Overall metrics

Define `Delta n_i = n_i - n_i0`.

```text
Y~_D/A = Delta n_D / (-Delta n_A)
S~_D/U = Delta n_D / Delta n_U
```

Overall metrics describe accumulated performance from the initial state to the current/final state.

## Parallel reaction example

```text
nu_A1 A -> D
nu_A2 A -> U

S = [ -nu_A1  -nu_A2
       1        0
       0        1 ]
```

Then:

```text
R_A = -nu_A1 r1 - nu_A2 r2
R_D = r1
R_U = r2
```

and therefore:

```text
nu_A1 Y_D/A(inst) + nu_A2 Y_U/A(inst) = 1
S_D/U(inst) = r1/r2
```

The same weighted-yield closure holds for the overall yields after integration.

## Series reaction example

```text
A -> D -> U
```

with:

```text
R_A = -r1
R_D = r1 - r2
R_U = r2
```

Therefore:

```text
Y_D/A(inst) = 1 - r2/r1
Y_U/A(inst) = r2/r1
```

The desired intermediate can have a negative instantaneous net yield if it is being consumed faster than it is being formed, even while its accumulated overall yield remains positive.

## Stoichiometric dependencies

For a closed batch define a differential reaction-extent vector:

```text
dxi = V r dt
```

Then:

```text
dn = S dxi
```

For a full-column-rank reaction set, choose key-species rows that form an invertible square block `S_K`; collect the remaining rows in `S_dep`.

```text
dn_dep = Phi dn_K
Phi = S_dep S_K^-1
```

`Phi` is the **stoichiometric dependency matrix**. It is structural, not an instantaneous-yield matrix.

Because the stoichiometry is fixed:

```text
Delta n_dep = Phi Delta n_K
```

## Van de Vusse dependency

For the four reacting species:

```text
S = [ -2  -1   0
       1   0   0
       0   1  -1
       0   0   1 ]
```

Choose x2, x3 and x4 as key species. Then:

```text
S_K = [ 1  0   0
        0  1  -1
        0  0   1 ]

S_dep = [ -2  -1  0 ]

Phi = S_dep S_K^-1 = [ -2  -1  -1 ]
```

Therefore:

```text
dn1 = -2 dn2 - dn3 - dn4
Delta n1 = -2 Delta n2 - Delta n3 - Delta n4
n1 + 2 n2 + n3 + n4 = constant
```

This relation is independent of kinetic rate constants and reaction-rate expressions.

## Applications developed on the page

1. **Unmeasured-species reconstruction** — use the invariant to infer one species from the others, with a warning that measurement noise propagates into the reconstruction.
2. **ODE reduction** — solve only the independent dynamic variables and reconstruct dependent species algebraically if useful.
3. **Rate-free experimental validation** — evaluate the Van de Vusse stoichiometric residual

```text
epsilon_stoich(t) = Delta n1 + 2 Delta n2 + Delta n3 + Delta n4
```

which should be zero for data exactly consistent with the assumed reaction network.
4. **Stoichiometric data reconciliation** — project noisy measured composition changes into the column space of `S` using the unweighted pseudoinverse example

```text
xi_hat = S+ Delta n_meas
Delta n_hat = S xi_hat
```

and inspect the adjustment residual before any conditioning is accepted.

## Important caution

For variable-volume reactors, stoichiometric invariants and data-consistency checks should be applied to **mole amounts**, not directly to concentrations.

KineticFittingPot v1.22 introduces these ideas as Fundamentals teaching content. It does not yet change the kinetic-fitting engine or automatically reconcile experimental data.
