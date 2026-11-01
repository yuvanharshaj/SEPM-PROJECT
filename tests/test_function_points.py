"""Unit tests for Function Point Analysis Engine (VTU 24CS51 Module 3)."""

import pytest
import math
from core.function_points import (
    calculate_ufp,
    calculate_function_points,
    fp_to_kloc,
    FP_COMPLEXITY_WEIGHTS,
    LANGUAGE_LOC_FACTORS,
)


def test_ufp_calculation():
    """Verify UFP calculation across all 5 information domain characteristics."""
    # EI: 2 low (2*3=6), 3 avg (3*4=12), 1 high (1*6=6) -> 24
    # EO: 1 low (1*4=4), 2 avg (2*5=10), 0 high -> 14
    # EQ: 4 low (4*3=12), 1 avg (1*3=3), 2 high (2*6=12) -> 27
    # ILF: 1 low (1*7=7), 1 avg (1*10=10), 0 high -> 17
    # EIF: 0 low, 1 avg (1*7=7), 1 high (1*10=10) -> 17
    # Total UFP = 24 + 14 + 27 + 17 + 17 = 99
    comps = {
        "EI": {"low": 2, "average": 3, "high": 1},
        "EO": {"low": 1, "average": 2, "high": 0},
        "EQ": {"low": 4, "average": 1, "high": 2},
        "ILF": {"low": 1, "average": 1, "high": 0},
        "EIF": {"low": 0, "average": 1, "high": 1},
    }
    ufp = calculate_ufp(comps)
    assert ufp == 99.0


def test_vaf_boundaries():
    """VAF = 0.65 + 0.01 * TDI. Min TDI=0 -> VAF=0.65; Max TDI=70 -> VAF=1.35."""
    comps = {"EI": {"low": 10, "average": 0, "high": 0}}  # UFP = 30
    
    # Min GSC (all 0)
    res_min = calculate_function_points(comps, [0] * 14)
    assert res_min.tdi == 0
    assert math.isclose(res_min.vaf, 0.65, rel_tol=1e-5)
    assert math.isclose(res_min.afp, 30 * 0.65, rel_tol=1e-5)

    # Max GSC (all 5)
    res_max = calculate_function_points(comps, [5] * 14)
    assert res_max.tdi == 70
    assert math.isclose(res_max.vaf, 1.35, rel_tol=1e-5)
    assert math.isclose(res_max.afp, 30 * 1.35, rel_tol=1e-5)

    # Nominal (all 3) -> TDI = 42, VAF = 0.65 + 0.42 = 1.07
    res_nom = calculate_function_points(comps, [3] * 14)
    assert res_nom.tdi == 42
    assert math.isclose(res_nom.vaf, 1.07, rel_tol=1e-5)
    assert math.isclose(res_nom.afp, 30 * 1.07, rel_tol=1e-5)


def test_language_kloc_conversion():
    """Verify FP to KLOC conversion using language factors."""
    afp = 100.0
    python_kloc = fp_to_kloc(afp, "Python")  # 53 LOC/FP -> 5.3 KLOC
    c_kloc = fp_to_kloc(afp, "C")            # 128 LOC/FP -> 12.8 KLOC

    assert math.isclose(python_kloc, 5.3, rel_tol=1e-5)
    assert math.isclose(c_kloc, 12.8, rel_tol=1e-5)


def test_gsc_validation_errors():
    comps = {"EI": {"low": 5, "average": 0, "high": 0}}
    # Incorrect count (not 14)
    with pytest.raises(ValueError, match="Exactly 14"):
        calculate_function_points(comps, [3] * 13)

    # Out-of-range rating (> 5)
    with pytest.raises(ValueError, match="must be 0-5"):
        calculate_function_points(comps, [3] * 13 + [6])

