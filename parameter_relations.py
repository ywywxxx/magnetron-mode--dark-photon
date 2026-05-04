"""
Symbolic parameter relations for magnetron dark-photon calculations.

This file intentionally stores expressions first, not final numerical
evaluations. Add relations one by one as the model is specified.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Iterable

from units import unitConversion


@dataclass(frozen=True)
class Relation:
    """A named symbolic relation and the quantities it depends on."""

    name: str
    expression: str
    depends_on: tuple[str, ...] = ()
    note: str = ""


relations: dict[str, Relation] = {}

KNOWN_MATH_SYMBOLS = {"Normal", "erfc", "log", "log1p", "max", "min", "sqrt", "pi"}


def add_relation(
    name: str,
    expression: str,
    depends_on: Iterable[str] = (),
    note: str = "",
) -> None:
    """Register one symbolic parameter relation."""
    relations[name] = Relation(
        name=name,
        expression=expression,
        depends_on=tuple(depends_on),
        note=note,
    )


def get_relation(name: str) -> Relation:
    """Return one registered relation by name."""
    return relations[name]


def list_relations() -> list[Relation]:
    """Return all registered relations in insertion order."""
    return list(relations.values())


def expression_symbols(expression: str) -> set[str]:
    """Return all symbol names used by one Python-style expression string."""
    tree = ast.parse(expression, mode="eval")
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}


def undefined_symbols() -> set[str]:
    """Return symbols that appear in relations but are not defined here."""
    defined = set(relations) | set(unitConversion) | KNOWN_MATH_SYMBOLS
    used: set[str] = set()

    for relation in list_relations():
        used.update(expression_symbols(relation.expression))
        used.update(relation.depends_on)

    return used - defined


def print_relations() -> None:
    """Print the current expression table."""
    for relation in list_relations():
        deps = ", ".join(relation.depends_on) if relation.depends_on else "none"
        print(f"{relation.name} = {relation.expression}")
        print(f"  depends_on: {deps}")
        if relation.note:
            print(f"  note: {relation.note}")


# Default parameters.

add_relation(
    name="rho_DM",
    expression="4.5 * GeV / cm**3",
    note="Local dark matter energy density.",
)

add_relation(
    name="v_DM",
    expression="1e-3",
    note="Typical virial dark matter speed in c = 1 units, about 300 km/s.",
)

add_relation(
    name="R",
    expression="1 * m",
    note="Default radius or length scale when no special geometry is specified.",
)

add_relation(
    name="sin2theta_avg",
    expression="2 / 3",
    note="Default angular average <sin^2 theta> for an isotropic dark matter field.",
)

add_relation(
    name="n_m",
    expression="1e9",
    note="Default magnetron occupation number.",
)

add_relation(
    name="n_e",
    expression="1",
    note="Default electron number.",
)

# Scan ranges.

add_relation(
    name="omega_c_min",
    expression="0.1 * meV",
    note="Lower scan bound for omega_c.",
)

add_relation(
    name="omega_c_max",
    expression="1 * meV",
    note="Upper scan bound for omega_c.",
)

add_relation(
    name="omega_z_min",
    expression="4.1e-9 * eV",
    note="Lower scan bound for omega_z.",
)

add_relation(
    name="omega_z_max",
    expression="8.3e-7 * eV",
    note="Upper scan bound for omega_z.",
)

# Frequency and bandwidth relations.

add_relation(
    name="sigma_noise",
    expression="0.03 * Hz / sqrt(t_ave / sec)",
    depends_on=("t_ave",),
    note="Frequency noise. t_ave is the averaging time in seconds; result is in Hz.",
)

add_relation(
    name="delta_c",
    expression="2*pi * 57*kHz * (10*MHz / (omega_z / (2*pi)))",
    depends_on=("omega_z",),
    note=(
        "Equivalent input form: delta_c / (2*pi) = "
        "57 kHz * (10 MHz / (omega_z / (2*pi)))."
    ),
)

add_relation(
    name="omega_m",
    expression="omega_z**2 / (2 * omega_c)",
    depends_on=("omega_c", "omega_z"),
)

add_relation(
    name="delta_m",
    expression="delta_c * omega_m / omega_c",
    depends_on=("delta_c", "omega_m", "omega_c"),
)

add_relation(
    name="Delta_m",
    expression="m_Aprime * 1e-6",
    depends_on=("m_Aprime",),
    note=(
        "Dark matter signal bandwidth from virial velocity spread, "
        "Delta_m / m_Aprime ~ v_DM**2 ~ 1e-6."
    ),
)

add_relation(
    name="m_Aprime_resonance",
    expression="omega_m",
    depends_on=("omega_m",),
    note="On resonance, the dark photon mass is matched to the magnetron frequency.",
)

# Geometry and response factors.

add_relation(
    name="kappa_m_squared",
    expression="max((omega_m * R)**4, (omega_m * R * v_DM)**2)",
    depends_on=("omega_m", "R", "v_DM"),
    note="Approximate relation: kappa_m**2 ~ max[(omega_m R)**4, (omega_m R v_DM)**2].",
)

# Signal rate.

add_relation(
    name="Gamma_m",
    expression=(
        "kappa_m_squared * n_m * n_e * (epsilon**2 * e**2 * pi / 4) "
        "* (rho_DM / Delta_m) * sin2theta_avg * R**2"
    ),
    depends_on=(
        "kappa_m_squared",
        "n_m",
        "n_e",
        "epsilon",
        "e",
        "rho_DM",
        "Delta_m",
        "sin2theta_avg",
        "R",
    ),
    note=(
        "Signal rate for magnetron mode, including the geometric response "
        "kappa_m_squared. On resonance use m_Aprime = omega_m, so "
        "Delta_m = 1e-6 * omega_m."
    ),
)

add_relation(
    name="sigma_m",
    expression="delta_m * sqrt(Gamma_m * t_ave)",
    depends_on=("delta_m", "Gamma_m", "t_ave"),
    note="Magnetron signal scale from delta_m times sqrt(Gamma_m * t_ave).",
)

# Detection probability.

add_relation(
    name="x_distribution",
    expression="Normal(0, sigma_m)",
    depends_on=("sigma_m",),
    note="Detection statistic x is modeled as a normal random variable with mean 0 and standard deviation sigma_m.",
)

add_relation(
    name="thr",
    expression="5 * sigma_noise",
    depends_on=("sigma_noise",),
    note="Detection threshold set to 5 times the noise scale.",
)

add_relation(
    name="z_thr",
    expression="thr / sigma_m",
    depends_on=("thr", "sigma_m"),
    note="Dimensionless threshold used to evaluate P(x > thr).",
)

add_relation(
    name="P_det",
    expression="0.5 * erfc(z_thr / sqrt(2))",
    depends_on=("z_thr",),
    note="P_det = P(x > thr) for x ~ Normal(0, sigma_m).",
)

add_relation(
    name="N_det",
    expression="log(0.05) / log1p(-P_det)",
    depends_on=("P_det",),
    note="Number of independent trials required for 95% confidence. log1p(-P_det) is numerically stable for log(1 - P_det).",
)

add_relation(
    name="t_obs",
    expression="N_det * t_ave",
    depends_on=("N_det", "t_ave"),
    note="Observation time required for 95% confidence.",
)


if __name__ == "__main__":
    print_relations()
    missing = undefined_symbols()
    if missing:
        print("\nUndefined external symbols:")
        for symbol in sorted(missing):
            print(f"  {symbol}")
