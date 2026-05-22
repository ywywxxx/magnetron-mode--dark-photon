# Cyclotron Cavity Sensitivity Logic

This note sketches the deep-purple cyclotron/cavity curve. The statistics of
the occupation distribution are intentionally left as a placeholder function.

## Rate

Use the single-quantum rate scale

```text
Gamma0_cavity =
  kappa_m_squared
  * epsilon^2 * e^2 * pi
  / (2 * m_ion * m)
  * rho_DM / Delta_omega
  * sin2theta_avg
```

where

```text
m = m_Aprime = omega_m
Delta_omega = 1e-6 * omega_m
kappa_m_squared = max((omega_m * R)^4, (omega_m * R * v_DM)^2)
sin2theta_avg = 2/3
```

The transition rate from a cyclotron occupation `n_c` contains the matrix
element factor

```text
Gamma_up(n_c) = Gamma0_cavity * (n_c + 1)
```

The later distribution model should decide how to include downward transitions.
For now, everything after this point only needs the dimensionless time

```text
tau = Gamma0_cavity * t_ave
```

## Ion Mass

The ion mass is adjustable.

```text
m_ion = m_antiproton   default
m_antiproton ~= 0.938272 GeV
m_Ca40 ~= 37.26 GeV
```

Also allow a custom `m_ion` input in GeV.

## Signal Threshold

Use the same readout noise and SNR threshold as the magnetron curve:

```text
sigma_noise = 0.03 Hz / sqrt(t_ave / sec)
thr = snr_threshold * sigma_noise
```

If one cyclotron quantum produces a frequency jump `delta_c`, then the required
occupation threshold is

```text
n_thr = ceil(thr / delta_c)
```

with at least one quantum required:

```text
n_thr = max(1, ceil(thr / delta_c))
```

## Placeholder Distribution

Do not assume a Poisson distribution yet. Define a placeholder survival
probability:

```text
P_cav_survival(n_thr, tau) = P(n_c(t_ave) >= n_thr | n_c(0) = 0)
```

This function will later be supplied by simulation, a master-equation solver, or
an analytic approximation.

The single-trial detection probability is

```text
P_det = P_cav_survival(n_thr, tau)
```

## Repeated Trials

As in the magnetron case,

```text
N = t_obs / t_ave
```

The 95 percent detection condition is

```text
1 - (1 - P_det)^N = 0.95
```

so the required single-trial probability is

```text
P_req = 1 - 0.05^(1/N)
```

Equivalently, using a stable expression,

```text
P_req = -expm1(log(0.05) / N)
```

## Inverting The Placeholder Distribution

Define the inverse function

```text
tau_req = inverse_P_cav_survival(n_thr, P_req)
```

meaning

```text
P_cav_survival(n_thr, tau_req) = P_req
```

Then

```text
Gamma0_req = tau_req / t_ave
```

## Coupling Reach

Since

```text
Gamma0_cavity = epsilon^2 * Gamma0_over_epsilon2
```

where

```text
Gamma0_over_epsilon2 =
  kappa_m_squared
  * e^2 * pi
  / (2 * m_ion * omega_m)
  * rho_DM / (1e-6 * omega_m)
  * sin2theta_avg
```

the minimum dark-photon mixing is

```text
epsilon_min_cavity =
  sqrt(Gamma0_req / Gamma0_over_epsilon2)
```

## Placeholder Implementation Shape

The plotting code can be structured around these two functions:

```text
P_cav_survival(n_thr, tau)
inverse_P_cav_survival(n_thr, P_req)
```

The rest of the curve logic does not need to know whether these functions come
from Monte Carlo, a master equation, or a closed-form approximation.
