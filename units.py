"""
Natural-unit helpers for dark-photon parameter-space calculations.

Convention:
    hbar = c = 1
    base energy unit = eV
    electromagnetic fields use the Heaviside-Lorentz convention.

In this convention:
    length -> eV^-1
    time   -> eV^-1
    mass   -> eV
    B, E   -> eV^2
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import pi, sqrt


@dataclass(frozen=True)
class NaturalUnits:
    """Conversion factors from SI-like inputs to hbar = c = 1 units."""

    # Exact SI constants.
    c: float = 299_792_458.0  # m / s
    hbar_J_s: float = 1.054_571_817e-34  # J s
    eV_J: float = 1.602_176_634e-19  # J

    # Common measured constants.
    alpha_em: float = 7.297_352_5643e-3

    @property
    def hbar_eV_s(self) -> float:
        return self.hbar_J_s / self.eV_J

    @property
    def hbar_c_eV_m(self) -> float:
        return self.hbar_eV_s * self.c

    @property
    def electron_charge_HL(self) -> float:
        """Dimensionless electric charge e = sqrt(4 pi alpha)."""
        return sqrt(4.0 * pi * self.alpha_em)

    @property
    def J_to_eV(self) -> float:
        return 1.0 / self.eV_J

    @property
    def kg_to_eV(self) -> float:
        """Mass-energy conversion: kg -> eV."""
        return self.c**2 / self.eV_J

    @property
    def meter_to_inv_eV(self) -> float:
        """Length conversion: m -> eV^-1."""
        return 1.0 / self.hbar_c_eV_m

    @property
    def second_to_inv_eV(self) -> float:
        """Time conversion: s -> eV^-1."""
        return 1.0 / self.hbar_eV_s

    @property
    def Hz_to_eV(self) -> float:
        """Angular-frequency conversion: omega[rad/s] -> eV."""
        return self.hbar_eV_s

    @property
    def cycle_Hz_to_eV(self) -> float:
        """Ordinary-frequency conversion: f[cycles/s] -> eV."""
        return 2.0 * pi * self.hbar_eV_s

    @property
    def tesla_to_eV2(self) -> float:
        """
        Magnetic-field conversion: T -> eV^2.

        Derived from the Schwinger critical field,
        B_c = m_e^2 / e = 4.414e9 T, in Heaviside-Lorentz units.
        """
        m_e_eV = 510_998.95069
        B_critical_T = 4.414_005_218e9
        return m_e_eV**2 / self.electron_charge_HL / B_critical_T

    @property
    def V_per_m_to_eV2(self) -> float:
        """Electric-field conversion: V/m -> eV^2."""
        return self.tesla_to_eV2 / self.c

    @property
    def volt_to_eV(self) -> float:
        """
        Electric-potential conversion: V -> eV.

        A particle with charge e gains 1 eV crossing 1 V, so the
        natural-unit scalar potential is 1/e in eV.
        """
        return 1.0 / self.electron_charge_HL


u = NaturalUnits()


def _rational(value: str | int) -> Fraction:
    return Fraction(value)


def _build_unit_conversion() -> dict[str, Fraction]:
    """
    Mathematica-style unitConversion map, rationalized and reduced with sec = 1.

    This mirrors:
        <|alpha0 -> 1/137, e -> 0.303, K -> 86173.3 neV,
          cm -> 50677.3 eV^-1, neV -> 10^-18 GeV,
          eV -> 10^-9 GeV, hour -> 3600 sec, day -> 24 hour,
          year -> 365 day, GeV -> 1.51927*10^24 sec^-1, sec -> 1|>
    """
    sec = _rational(1)
    GeV = _rational("1.51927e24")
    eV = _rational("1e-9") * GeV
    meV = _rational("1e-3") * eV
    neV = _rational("1e-18") * GeV
    Hz = _rational(1) / sec
    kHz = _rational("1e3") * Hz
    MHz = _rational("1e6") * Hz
    hour = _rational(3600) * sec
    day = _rational(24) * hour
    year = _rational(365) * day
    cm = _rational("50677.3") / eV
    mm = cm / _rational(10)
    m = _rational(100) * cm

    return {
        "alpha0": _rational(1) / _rational(137),
        "e": _rational("0.303"),
        "K": _rational("86173.3") * neV,
        "m": m,
        "cm": cm,
        "mm": mm,
        "neV": neV,
        "meV": meV,
        "eV": eV,
        "Hz": Hz,
        "kHz": kHz,
        "MHz": MHz,
        "hour": hour,
        "day": day,
        "year": year,
        "GeV": GeV,
        "sec": sec,
    }


unitConversion = _build_unit_conversion()
unit_conversion = unitConversion


if __name__ == "__main__":
    print("hbar = c = 1 conversion factors, base unit eV")
    print(f"1 J        = {u.J_to_eV:.8e} eV")
    print(f"1 kg       = {u.kg_to_eV:.8e} eV")
    print(f"1 m        = {u.meter_to_inv_eV:.8e} eV^-1")
    print(f"1 s        = {u.second_to_inv_eV:.8e} eV^-1")
    print(f"1 rad/s    = {u.Hz_to_eV:.8e} eV")
    print(f"1 Hz       = {u.cycle_Hz_to_eV:.8e} eV")
    print(f"1 T        = {u.tesla_to_eV2:.8e} eV^2")
    print(f"1 V/m      = {u.V_per_m_to_eV2:.8e} eV^2")
    print(f"1 V        = {u.volt_to_eV:.8e} eV")

    print("\nMathematica-style unitConversion, reduced with sec = 1")
    for name, value in unitConversion.items():
        print(f"{name:6s} -> {float(value):.8e}")
