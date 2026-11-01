"""Currency and Numerical Formatting Utilities.

Provides comprehensive support for INR (₹), USD ($), and EUR (€) formatting
with Indian digit grouping (lakhs & crores) and Western standard grouping.
"""

from typing import Optional, Union

CURRENCY_SYMBOLS = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
}

CURRENCY_OPTIONS = {
    "INR": "INR (₹)",
    "USD": "USD ($)",
    "EUR": "EUR (€)",
}


def get_active_currency() -> str:
    """Retrieve the currently selected currency from Streamlit session state, defaulting to INR."""
    try:
        import streamlit as st
        return st.session_state.get("currency", "INR")
    except Exception:
        return "INR"


def get_currency_symbol(currency: Optional[str] = None) -> str:
    """Return the currency symbol for the given currency code or the active session currency."""
    curr = currency or get_active_currency()
    return CURRENCY_SYMBOLS.get(curr, "₹")


def format_indian_number(n: Union[int, float], precision: int = 0) -> str:
    """Format a number with Indian comma grouping (e.g. 12,34,567)."""
    if n is None:
        return "0"
    is_neg = n < 0
    an = abs(float(n))
    if precision > 0:
        int_part = int(an)
        dec_part = f"{an - int_part:.{precision}f}"[1:]
    else:
        int_part = int(round(an))
        dec_part = ""
    s = str(int_part)
    if len(s) <= 3:
        res = s
    else:
        last3 = s[-3:]
        rest = s[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        res = ",".join(groups) + "," + last3
    formatted = res + dec_part
    return f"-{formatted}" if is_neg else formatted


def format_currency(
    value: Union[int, float],
    currency: Optional[str] = None,
    compact: bool = False,
    precision: int = 2,
) -> str:
    """Format a monetary value into a styled currency string.

    Supports compact formats for KPI metric cards and charts (e.g. ₹85.0 L, ₹1.25 Cr, $1.2M),
    and full grouped numbers for tables and reports.
    """
    if value is None:
        return "N/A"
    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)

    curr = currency or get_active_currency()
    sym = get_currency_symbol(curr)
    is_neg = val < 0
    an = abs(val)

    if compact:
        if curr == "INR":
            prefix = f"-{sym}" if is_neg else sym
            if an >= 1e7:
                cr = an / 1e7
                s = f"{cr:.2f}" if abs(round(cr, 1) - round(cr, 2)) > 0.005 else f"{cr:.1f}"
                return f"{prefix}{s} Cr"
            elif an >= 1e5:
                l = an / 1e5
                s = f"{l:.2f}" if abs(round(l, 1) - round(l, 2)) > 0.005 else f"{l:.1f}"
                return f"{prefix}{s} L"
            else:
                return f"{prefix}{format_indian_number(an, precision=0)}"
        else:
            # Western compact grouping
            prefix = f"-{sym}" if is_neg else sym
            if an >= 1e6:
                m = an / 1e6
                s = f"{m:.2f}" if abs(round(m, 1) - round(m, 2)) > 0.005 else f"{m:.1f}"
                return f"{prefix}{s}M"
            elif an >= 1e3:
                k = an / 1e3
                s = f"{k:.2f}" if abs(round(k, 1) - round(k, 2)) > 0.005 else f"{k:.1f}"
                return f"{prefix}{s}K"
            else:
                return f"{prefix}{an:,.0f}"

    # Full grouped figure
    if curr == "INR":
        prefix = f"-{sym}" if is_neg else sym
        return f"{prefix}{format_indian_number(an, precision=precision)}"
    else:
        prefix = f"-{sym}" if is_neg else sym
        return f"{prefix}{an:,.{precision}f}"

