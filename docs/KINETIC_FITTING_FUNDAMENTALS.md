# Kinetic Fitting Fundamentals — KineticFittingPot v1.18

## Purpose

KineticFittingPot v1.18 activates the explanatory stage of the Kinetic Fitting section but deliberately does **not** yet implement an optimiser. The aim is to freeze the teaching and data architecture before parameter estimation is added.

## Forward and inverse problems

The existing Excel-defined isothermal simulator solves the forward problem:

`parameters -> ODE simulation -> concentration-time predictions`

Kinetic fitting is the inverse problem:

`experimental concentration-time observations -> adjust selected parameters -> best agreement between model and data`

The same general ODE engine should be reused in both directions.

## Multiple datasets

The fitter supports multiple experiments. Kinetic parameters selected for fitting are shared globally across datasets, while each dataset may have different initial conditions, catalyst loading, volume and observation times.

For each trial parameter vector, the fitter simulates every selected dataset and concatenate all valid residuals into one residual vector.

## Irregular and missing observations

Datasets do not require a common sampling grid. The continuous ODE solution is evaluated at each actual observation time.

Missing observations remain missing. The long-format `Experimental_Data` sheet contains one row per real observation; an unmeasured species/time combination is simply absent. Missing experimental observations are not interpolated or imputed.

## Residuals and weighting

A basic residual is `model - measured`. Raw least squares can be dominated by numerically large species, so the fitter provides explicit unweighted and species-scaled residual options.

## Bounds, starting values and multistart fitting

Every fitted parameter requires a finite lower and upper bound supplied by the user. Parameter ranges are supplied explicitly; the fitter does not invent hidden bounds.

The optimiser uses bounded multistart `scipy.optimize.least_squares`:

1. include the user's supplied estimate as one start;
2. generate additional starting vectors within the user bounds;
3. run bounded least squares from every start;
4. rank converged solutions by objective value;
5. display the best and competing outcomes.

Multistart is a practical defence against poor local minima, not a proof of the mathematical global optimum.

## Optimisation versus identifiability

If different starts lead to substantially different parameter vectors with almost the same objective value, the data may not uniquely identify the parameters. Convergence and parameter identifiability are distinct questions and must be assessed separately.

## Worked example

The fitting example workbook uses the catalytic saturation model:

`r1 = k1*c_Cat*c_A/(1 + KA*c_A)`

`r2 = k2*c_B`

Three synthetic datasets use initial catalyst concentrations of 0.05, 0.10 and 0.20 kmol m^-3, different measurement schedules and deliberately missing observations. The known generating values are retained separately for teaching validation only:

- k1 = 0.020 m3 kmol^-1 s^-1
- KA = 1.0 m3 kmol^-1
- k2 = 0.00030 s^-1

The `Parameters` sheet instead contains deliberately imperfect starting estimates and finite bounds.

The workbook contains:

- existing model-definition sheets;
- `Datasets` — dataset-specific initial conditions;
- `Experimental_Data` — long-format noisy observations;
- `Synthetic_Data_Info` — seed, noise model and known truth for validation only.

The optimiser does not use `Synthetic_Data_Info` to estimate parameters.
