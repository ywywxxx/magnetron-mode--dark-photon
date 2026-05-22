# Cyclotron Cavity Sensitivity Logic

This note sketches the deep-purple cyclotron/cavity curve. It uses the same
large-occupation Gaussian/random-walk statistics as the green magnetron curve.

## Large-n_c Approximation

For high cyclotron occupation, the lower boundary at `n_c = 0` is far away. We
therefore approximate the net cyclotron response as a symmetric random walk in
occupation number rather than a ground-state birth process.

The signal statistic is modeled as

```text
x_cavity ~ Normal(0, sigma_cavity)
```

with

```text
sigma_cavity = delta_c * sqrt(Gamma_cavity * t_ave)
```

## Rate

Use

```text
Gamma_cavity =
  kappa_m_squared
  * epsilon^2 * e^2 * pi * (n_c + 1)
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

The current default is

```text
n_c = 1e6
```

and `n_c` is adjustable in the web UI.

## Ion Mass

The ion mass is adjustable.

```text
m_ion = m_antiproton   default
m_antiproton ~= 0.938272 GeV
m_Ca40 ~= 37.26 GeV
```

The UI also allows a custom `m_ion` input in GeV.

## Detection Probability

Use the same readout noise and SNR threshold as the magnetron curve:

```text
sigma_noise = 0.03 Hz / sqrt(t_ave / sec)
thr = snr_threshold * sigma_noise
```

Define

```text
z_thr = thr / sigma_cavity
```

For two-sided detection,

```text
P_det = erfc(z_thr / sqrt(2))
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

or

```text
P_req = 1 - 0.05^(1/N)
```

Using the same inversion as the green curve, let `z_req` satisfy

```text
P_req = erfc(z_req / sqrt(2))
```

Then the required signal scale is

```text
sigma_cavity,req = thr / z_req
```

## Coupling Reach

Since

```text
Gamma_cavity = epsilon^2 * Gamma_cavity_over_epsilon2
```

where

```text
Gamma_cavity_over_epsilon2 =
  kappa_m_squared
  * e^2 * pi * (n_c + 1)
  / (2 * m_ion * omega_m)
  * rho_DM / (1e-6 * omega_m)
  * sin2theta_avg
```

the minimum dark-photon mixing is

```text
epsilon_min_cavity =
  thr / (
    z_req * delta_c * sqrt(Gamma_cavity_over_epsilon2 * t_ave)
  )
```

## Plot Lines

The first mass-scan plot includes two deep-purple lines:

```text
solid purple:  epsilon_min_cavity(t_ave)
dashed purple: epsilon_min_cavity(t_ave = t_obs)
```

The green magnetron curves are unchanged.
