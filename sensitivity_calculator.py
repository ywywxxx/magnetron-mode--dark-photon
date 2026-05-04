"""
Numerical sensitivity calculator for the magnetron dark-photon setup.

The calculator assumes resonance:
    m_Aprime = omega_m = omega_z**2 / (2 * omega_c)

For a fixed omega_m, changing omega_c automatically adapts omega_z.
Changing omega_z automatically adapts omega_c.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from math import erfc, expm1, log, log1p, pi, sqrt

from units import unitConversion


U = {name: float(value) for name, value in unitConversion.items()}
RANGE_RTOL = 1e-12


def in_closed_range(value: float, lower: float, upper: float) -> bool:
    scale = max(abs(lower), abs(upper), abs(value), 1.0)
    tol = RANGE_RTOL * scale
    return lower - tol <= value <= upper + tol


def tail_probability(z: float) -> float:
    """One-sided Gaussian tail P(Z > z), Z ~ Normal(0, 1)."""
    return 0.5 * erfc(z / sqrt(2.0))


def inverse_tail_probability(p: float) -> float:
    """Return z such that P(Z > z) = p for 0 < p < 0.5."""
    if not 0.0 < p < 0.5:
        raise ValueError("p must satisfy 0 < p < 0.5")

    lo = 0.0
    hi = 8.0
    while tail_probability(hi) > p:
        hi *= 2.0
        if hi > 1_000.0:
            raise ValueError("p is too small to invert with double precision")

    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if tail_probability(mid) > p:
            lo = mid
        else:
            hi = mid

    return 0.5 * (lo + hi)


@dataclass(frozen=True)
class Ranges:
    omega_c_min: float = 0.1 * U["meV"]
    omega_c_max: float = 1.0 * U["meV"]
    omega_z_min: float = 4.1e-9 * U["eV"]
    omega_z_max: float = 8.3e-7 * U["eV"]

    @property
    def omega_m_min(self) -> float:
        return self.omega_z_min**2 / (2.0 * self.omega_c_max)

    @property
    def omega_m_max(self) -> float:
        return self.omega_z_max**2 / (2.0 * self.omega_c_min)

    def check_omega_m(self, omega_m: float) -> None:
        if not in_closed_range(omega_m, self.omega_m_min, self.omega_m_max):
            raise ValueError(
                "omega_m is outside the allowed range: "
                f"{fmt(omega_m, 'neV')} not in "
                f"[{fmt(self.omega_m_min, 'neV')}, {fmt(self.omega_m_max, 'neV')}]"
            )

    def check_omega_c(self, omega_c: float) -> None:
        if not in_closed_range(omega_c, self.omega_c_min, self.omega_c_max):
            raise ValueError(
                "omega_c is outside the allowed range: "
                f"{fmt(omega_c, 'meV')} not in "
                f"[{fmt(self.omega_c_min, 'meV')}, {fmt(self.omega_c_max, 'meV')}]"
            )

    def check_omega_z(self, omega_z: float) -> None:
        if not in_closed_range(omega_z, self.omega_z_min, self.omega_z_max):
            raise ValueError(
                "omega_z is outside the allowed range: "
                f"{fmt(omega_z, 'eV')} not in "
                f"[{fmt(self.omega_z_min, 'eV')}, {fmt(self.omega_z_max, 'eV')}]"
            )

    def omega_c_range_for_omega_m(self, omega_m: float) -> tuple[float, float]:
        lower = max(self.omega_c_min, self.omega_z_min**2 / (2.0 * omega_m))
        upper = min(self.omega_c_max, self.omega_z_max**2 / (2.0 * omega_m))
        if lower > upper:
            raise ValueError("No allowed omega_c values for this omega_m")
        return lower, upper

    def omega_z_range_for_omega_m(self, omega_m: float) -> tuple[float, float]:
        lower = max(self.omega_z_min, sqrt(2.0 * self.omega_c_min * omega_m))
        upper = min(self.omega_z_max, sqrt(2.0 * self.omega_c_max * omega_m))
        if lower > upper:
            raise ValueError("No allowed omega_z values for this omega_m")
        return lower, upper


@dataclass(frozen=True)
class State:
    omega_m: float
    omega_c: float
    omega_z: float
    t_ave: float
    t_obs: float

    @classmethod
    def from_omega_m_and_omega_c(
        cls,
        omega_m: float,
        omega_c: float,
        t_ave: float,
        t_obs: float,
        ranges: Ranges,
    ) -> "State":
        ranges.check_omega_m(omega_m)
        ranges.check_omega_c(omega_c)
        omega_z = sqrt(2.0 * omega_c * omega_m)
        ranges.check_omega_z(omega_z)
        return cls(omega_m=omega_m, omega_c=omega_c, omega_z=omega_z, t_ave=t_ave, t_obs=t_obs)

    @classmethod
    def from_omega_m_and_omega_z(
        cls,
        omega_m: float,
        omega_z: float,
        t_ave: float,
        t_obs: float,
        ranges: Ranges,
    ) -> "State":
        ranges.check_omega_m(omega_m)
        ranges.check_omega_z(omega_z)
        omega_c = omega_z**2 / (2.0 * omega_m)
        ranges.check_omega_c(omega_c)
        return cls(omega_m=omega_m, omega_c=omega_c, omega_z=omega_z, t_ave=t_ave, t_obs=t_obs)

    def with_omega_m(self, omega_m: float, ranges: Ranges) -> "State":
        """Change omega_m while holding omega_c fixed and adapting omega_z."""
        return State.from_omega_m_and_omega_c(
            omega_m=omega_m,
            omega_c=self.omega_c,
            t_ave=self.t_ave,
            t_obs=self.t_obs,
            ranges=ranges,
        )

    def with_omega_c(self, omega_c: float, ranges: Ranges) -> "State":
        """Change omega_c while holding omega_m fixed and adapting omega_z."""
        return State.from_omega_m_and_omega_c(
            omega_m=self.omega_m,
            omega_c=omega_c,
            t_ave=self.t_ave,
            t_obs=self.t_obs,
            ranges=ranges,
        )

    def with_omega_z(self, omega_z: float, ranges: Ranges) -> "State":
        """Change omega_z while holding omega_m fixed and adapting omega_c."""
        return State.from_omega_m_and_omega_z(
            omega_m=self.omega_m,
            omega_z=omega_z,
            t_ave=self.t_ave,
            t_obs=self.t_obs,
            ranges=ranges,
        )

    def with_t_ave(self, t_ave: float) -> "State":
        return State(self.omega_m, self.omega_c, self.omega_z, t_ave, self.t_obs)

    def with_t_obs(self, t_obs: float) -> "State":
        return State(self.omega_m, self.omega_c, self.omega_z, self.t_ave, t_obs)


@dataclass(frozen=True)
class Result:
    epsilon_min: float
    p_required: float
    z_required: float
    n_required: float
    sigma_noise: float
    sigma_m: float
    threshold: float
    gamma_m: float
    delta_c: float
    delta_m: float
    kappa_m_squared: float
    omega_m: float
    omega_c: float
    omega_z: float
    t_ave: float
    t_obs: float


def calculate_min_epsilon(state: State) -> Result:
    """Calculate the minimum epsilon that reaches 95% in state.t_obs."""
    n_required = state.t_obs / state.t_ave
    min_trials = log(0.05) / log(0.5)
    if n_required <= min_trials:
        raise ValueError(
            "No finite epsilon can reach 95% confidence because P_det <= 0.5. "
            f"Need t_obs/t_ave > {min_trials:.8g}."
        )

    p_required = -expm1(log(0.05) / n_required)
    z_required = inverse_tail_probability(p_required)

    rho_dm = 4.5 * U["GeV"] / U["cm"] ** 3
    r = U["m"]
    v_dm = 1e-3
    e_charge = U["e"]
    sin2theta_avg = 2.0 / 3.0
    n_m = 1e9
    n_e = 1.0

    sigma_noise = 0.03 * U["Hz"] / sqrt(state.t_ave / U["sec"])
    threshold = 5.0 * sigma_noise

    delta_c = 2.0 * pi * 57.0 * U["kHz"] * (
        10.0 * U["MHz"] / (state.omega_z / (2.0 * pi))
    )
    delta_m = delta_c * state.omega_m / state.omega_c
    delta_dm = state.omega_m * 1e-6
    kappa_m_squared = max((state.omega_m * r) ** 4, (state.omega_m * r * v_dm) ** 2)

    gamma_over_epsilon2 = (
        kappa_m_squared
        * n_m
        * n_e
        * (e_charge**2 * pi / 4.0)
        * (rho_dm / delta_dm)
        * sin2theta_avg
        * r**2
    )
    signal_per_epsilon = delta_m * sqrt(gamma_over_epsilon2 * state.t_ave)
    epsilon_min = threshold / (z_required * signal_per_epsilon)

    gamma_m = gamma_over_epsilon2 * epsilon_min**2
    sigma_m = signal_per_epsilon * epsilon_min

    return Result(
        epsilon_min=epsilon_min,
        p_required=p_required,
        z_required=z_required,
        n_required=n_required,
        sigma_noise=sigma_noise,
        sigma_m=sigma_m,
        threshold=threshold,
        gamma_m=gamma_m,
        delta_c=delta_c,
        delta_m=delta_m,
        kappa_m_squared=kappa_m_squared,
        omega_m=state.omega_m,
        omega_c=state.omega_c,
        omega_z=state.omega_z,
        t_ave=state.t_ave,
        t_obs=state.t_obs,
    )


def unit_value(value: float, unit_name: str) -> float:
    return value * U[unit_name]


def fmt(value: float, unit_name: str, precision: int = 6) -> str:
    return f"{value / U[unit_name]:.{precision}g} {unit_name}"


def print_ranges(ranges: Ranges) -> None:
    print("Allowed ranges")
    print(f"  omega_c: [{fmt(ranges.omega_c_min, 'meV')}, {fmt(ranges.omega_c_max, 'meV')}]")
    print(f"  omega_z: [{fmt(ranges.omega_z_min, 'eV')}, {fmt(ranges.omega_z_max, 'eV')}]")
    print(f"  omega_m: [{fmt(ranges.omega_m_min, 'neV')}, {fmt(ranges.omega_m_max, 'neV')}]")


def print_result(result: Result, ranges: Ranges | None = None) -> None:
    print("Current point")
    print(f"  omega_m = {fmt(result.omega_m, 'neV')}")
    print(f"  omega_c = {fmt(result.omega_c, 'meV')}")
    print(f"  omega_z = {fmt(result.omega_z, 'eV')}")
    print(f"  t_ave   = {fmt(result.t_ave, 'sec')}")
    print(f"  t_obs   = {fmt(result.t_obs, 'sec')}")
    if ranges is not None:
        omega_c_min, omega_c_max = ranges.omega_c_range_for_omega_m(result.omega_m)
        omega_z_min, omega_z_max = ranges.omega_z_range_for_omega_m(result.omega_m)
        print("  fixed-omega_m tuning")
        print(f"    omega_c: [{fmt(omega_c_min, 'meV')}, {fmt(omega_c_max, 'meV')}]")
        print(f"    omega_z: [{fmt(omega_z_min, 'eV')}, {fmt(omega_z_max, 'eV')}]")
    print("")
    print("Derived")
    print(f"  kappa_m_squared = {result.kappa_m_squared:.6e}")
    print(f"  delta_c         = {fmt(result.delta_c, 'Hz')}")
    print(f"  delta_m         = {fmt(result.delta_m, 'Hz')}")
    print(f"  sigma_noise     = {fmt(result.sigma_noise, 'Hz')}")
    print(f"  threshold       = {fmt(result.threshold, 'Hz')}")
    print("")
    print("95% detection boundary")
    print(f"  epsilon_min = {result.epsilon_min:.6e}")
    print(f"  P_det       = {result.p_required:.6e}")
    print(f"  N_det       = {result.n_required:.6e}")
    print(f"  z_thr       = {result.z_required:.6e}")
    print(f"  sigma_m     = {fmt(result.sigma_m, 'Hz')}")
    print(f"  Gamma_m     = {fmt(result.gamma_m, 'Hz')}")


def make_initial_state(args: argparse.Namespace, ranges: Ranges) -> State:
    omega_m = unit_value(args.omega_m, args.omega_m_unit)
    t_ave = unit_value(args.t_ave, args.t_ave_unit)
    t_obs = unit_value(args.t_obs, args.t_obs_unit)

    if args.omega_z is not None:
        omega_z = unit_value(args.omega_z, args.omega_z_unit)
        return State.from_omega_m_and_omega_z(omega_m, omega_z, t_ave, t_obs, ranges)

    omega_c = unit_value(args.omega_c, args.omega_c_unit)
    return State.from_omega_m_and_omega_c(omega_m, omega_c, t_ave, t_obs, ranges)


def interactive_loop(state: State, ranges: Ranges) -> None:
    print_ranges(ranges)
    print("")
    print("Commands: show, ranges, wm VALUE UNIT, wc VALUE UNIT, wz VALUE UNIT, tave VALUE UNIT, tobs VALUE UNIT, quit")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            print("")
            return

        if not line:
            continue
        if line in {"quit", "q", "exit"}:
            return
        if line == "ranges":
            print_ranges(ranges)
            continue
        if line == "show":
            print_result(calculate_min_epsilon(state), ranges)
            continue

        parts = line.split()
        if len(parts) != 3:
            print("Expected: command VALUE UNIT")
            continue

        command, raw_value, unit_name = parts
        if unit_name not in U:
            print(f"Unknown unit: {unit_name}")
            continue

        try:
            value = unit_value(float(raw_value), unit_name)
            if command == "wm":
                state = state.with_omega_m(value, ranges)
            elif command == "wc":
                state = state.with_omega_c(value, ranges)
            elif command == "wz":
                state = state.with_omega_z(value, ranges)
            elif command == "tave":
                state = state.with_t_ave(value)
            elif command == "tobs":
                state = state.with_t_obs(value)
            else:
                print(f"Unknown command: {command}")
                continue
            print_result(calculate_min_epsilon(state), ranges)
        except ValueError as exc:
            print(f"Error: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--omega-m", type=float, default=0.1, help="target omega_m value")
    parser.add_argument("--omega-m-unit", default="neV", choices=sorted(U), help="unit for omega_m")
    parser.add_argument("--omega-c", type=float, default=0.1, help="omega_c value; omega_z adapts")
    parser.add_argument("--omega-c-unit", default="meV", choices=sorted(U), help="unit for omega_c")
    parser.add_argument("--omega-z", type=float, help="omega_z value; omega_c adapts if supplied")
    parser.add_argument("--omega-z-unit", default="eV", choices=sorted(U), help="unit for omega_z")
    parser.add_argument("--t-ave", type=float, default=1e-6, help="single-trial averaging time")
    parser.add_argument("--t-ave-unit", default="sec", choices=sorted(U), help="unit for t_ave")
    parser.add_argument("--t-obs", type=float, default=6.0, help="total observation time")
    parser.add_argument("--t-obs-unit", default="sec", choices=sorted(U), help="unit for t_obs")
    parser.add_argument("--interactive", action="store_true", help="start an interactive adjustment prompt")
    return parser.parse_args()


def main() -> None:
    ranges = Ranges()
    args = parse_args()
    state = make_initial_state(args, ranges)
    print_ranges(ranges)
    print("")
    print_result(calculate_min_epsilon(state), ranges)
    if args.interactive:
        print("")
        interactive_loop(state, ranges)


if __name__ == "__main__":
    main()
